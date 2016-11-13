from django.db import transaction
from django.db.models import Avg, Max, Sum, Q
from django.conf import settings

from dateutil.relativedelta import relativedelta

from . import models, serializers, constants, helpers, xirr, new_xirr
from profiles import models as profile_models
from profiles import helpers as profiles_helpers
from profiles import constants as profile_constants
from webapp.apps import random_with_N_digits
from payment import models as payment_models


from external_api import api
from collections import OrderedDict, defaultdict
from datetime import date, datetime, timedelta
import math
import ast
import logging
import copy
import re
import hmac
import hashlib
import threading

from itertools import chain
from core.utils import asset_allocation

debug_logger = logging.getLogger('django.debug')

def get_all_portfolio_details(user,fund_order_items):
    is_transient_dashboard = False
    # query all fund_order_items of a user
    all_investments_of_user = [fund_order_item for fund_order_item in fund_order_items if fund_order_item.portfolio_item.portfolio.user==user]
    if all_investments_of_user:
        # query all redeems of user
        all_redeems_of_user = models.FundRedeemItem.objects.filter(portfolio_item__portfolio__user=user,is_verified=True)
        # club all investments and redeems of a user according to the funds
        transaction_fund_map, today_portfolio, portfolios_to_be_considered = club_investment_redeem_together(all_investments_of_user, all_redeems_of_user)
        info =  get_dashboard_version_two(transaction_fund_map, today_portfolio, portfolios_to_be_considered, is_transient_dashboard)
        return info
    
    
def get_portfolio_dashboard():
    fund_order_items = models.FundOrderItem.objects.filter(is_cancelled=False,is_verified=True)
    users = []
    if fund_order_items is not None:
        for fund_order_item in fund_order_items:
            if fund_order_item.portfolio_item.portfolio.user not in users:
                user = fund_order_item.portfolio_item.portfolio.user
                users.append(user)
                
                portfolio_details = get_all_portfolio_details(user,fund_order_items)
                   
                try:
                    applicant_name = investor_info_check(user)
                except:
                    applicant_name = None

                profiles_helpers.send_mail_weekly_portfolio(portfolio_details,user,applicant_name,use_https=settings.USE_HTTPS)
            

def send_sms_weekly_portfolio_snapshot():
    """
    Send sms for the weekly portfolio snapshot for all users 
    """
    fund_order_items = models.FundOrderItem.objects.filter(is_cancelled=False,is_verified=True)
    users = []
    if fund_order_items is not None:
        for fund_order_item in fund_order_items:
            if fund_order_item.portfolio_item.portfolio.user not in users:
                user = fund_order_item.portfolio_item.portfolio.user
                users.append(user)
                
                portfolio_details = get_all_portfolio_details(user,fund_order_items)
    
                sms_code_sent = api.send_sms(profile_constants.PORTFOLIO_WEEKLY_DT.format(portfolio_details.date,portfolio_details.portfolio_overview.invested,portfolio_details.portfolio_overview.current_value.value), int(user.phone_number))
    
#investor info check
def investor_info_check(user):
    applicant_name = None
    try:
        investor_info = profile_models.InvestorInfo.objects.get(user=user)  
        if investor_info is not None:
            if investor_info.applicant_name is not None:
                applicant_name = investor_info.applicant_name
    except profile_models.InvestorInfo.DoesNotExist:
            applicant_name = None
    return applicant_name

def reminder_next_sip_allotment():
    curr_date = date.today()
    target_date = curr_date + timedelta(days=settings.SIP_REMINDER_DAYS)  
    target_date_1 = target_date + timedelta(days=1)
    buffer_date = target_date + timedelta(days=settings.SIP_BUFFER_DAYS)
    fund_order_items = models.FundOrderItem.objects.filter(next_allotment_date__range=(curr_date,target_date),order_amount__gt=0 , agreed_sip__gt=0,sip_reminder_sent=False, is_future_sip_cancelled=False)      
    users = []
    if len(fund_order_items) > 0:
        buffer_fund_order_items = models.FundOrderItem.objects.filter(next_allotment_date__range=(target_date_1,buffer_date) , order_amount__gt=0 , agreed_sip__gt=0,sip_reminder_sent=False, is_future_sip_cancelled=False)
        if len(buffer_fund_order_items) > 0:
            all_fund_order_items = list(chain(fund_order_items, buffer_fund_order_items))
        else:
            all_fund_order_items = fund_order_items
        for fund_order_item in all_fund_order_items:
            if fund_order_item.portfolio_item.portfolio.user not in users:
                user = fund_order_item.portfolio_item.portfolio.user
                users.append(user)
                user_fund_order_items,bank_details,applicant_name,total_sip =  reminder_next_sip_detail(all_fund_order_items,target_date,user)   
                email = profiles_helpers.send_mail_reminder_next_sip(user_fund_order_items,target_date,total_sip,bank_details,applicant_name,user,use_https=settings.USE_HTTPS)    
                if email == True:
                    for fund_item in user_fund_order_items:
                        fund_item.sip_reminder_sent = True
                        fund_item.save()
    if len(users) > 0:
        profiles_helpers.send_mail_admin_next_sip(users,curr_date,target_date,use_https=settings.USE_HTTPS)
  
def reminder_next_sip_detail(fund_order_items,target_date,user):
    try:
        user_fund_order_items = [fund_order_item for fund_order_item in fund_order_items if fund_order_item.portfolio_item.portfolio.user==user]
        total_sip = sum(fund_order_item.agreed_sip for fund_order_item in user_fund_order_items)

    except:
        user_fund_order_items = None
        total_sip = None

    if user_fund_order_items is not None:    
        try:
            bank_details = profile_models.InvestorBankDetails.objects.get(user=user)
        except profile_models.InvestorBankDetails.DoesNotExist:
            bank_details = None
   
        try:
            applicant_name = models.investor_info_check(user)
        except:
            applicant_name = None
                    
    else:
        bank_details = None
        applicant_name = None
        
    return user_fund_order_items, bank_details,applicant_name,total_sip 
                    
        

def get_answers(answers, questions, id):
    """
    :param answers: A list of answers objects
    :param id: question id for which selected options needs to be sent
    :param questions: list of selected question
    :return: an array with objects of type id of option selected or text of the answer
    """
    answers = answers.filter(question__id=id)
    try:
        question = questions.get(id=id)
    except Exception as error:
        return None
    answer_object = []
    if question.type in ["C", "R"]:
        for answer in answers:
            answer_object.append({"answer": str(answer.option.id), "metadata": answer.metadata})
    else:
        for answer in answers:
            answer_object.append({"answer": answer.text, "metadata": answer.metadata})
    return answer_object


def save_risk_profile(request):
    """
    Saves the risk profile of user for assess questions
    :param request:
    """
    # if question_for is assess save the risk score of the user
    if request.data.get('risk_score', None):
        request.user.risk_score = request.data.get('risk_score', 0.0)
        request.user.save()


def process_plan_answer(request):
    """
    :param request:
    :return:
    """
    for key, value in request.data.items():
        if key != "P2" and key != "P7":
            question = models.Question.objects.get(question_id=key)
            models.Answer.objects.update_or_create(
                question_id=question.id, user=request.user, defaults={'text': value})
        elif key == "P2":
            question = models.Question.objects.get(question_id=key)
            question1 = models.Question.objects.get(question_id="P3")  # for shared preference ease
            count = 1
            for answer in value:
                models.Answer.objects.update_or_create(question_id=question.id, user=request.user,
                                                       metadata={"order": str(count)},
                                                       defaults={'text': answer.split(",")[0]}, )
                models.Answer.objects.update_or_create(question_id=question1.id, user=request.user,
                                                       metadata={"order": str(count)},
                                                       defaults={'text': answer.split(",")[1]}, )
                count = count + 1
        else:
            question = models.Question.objects.get(question_id=key)
            option_selected = models.Option.objects.get(option_id=value.split(",")[0], question__question_id=key)
            answer, created = models.Answer.objects.update_or_create(
                question_id=question.id, user=request.user, defaults={'option': option_selected})
            answer.text = value.split(",")[1]
            answer.save()
    return True


def process_assess_answer(request):
    """
    :param request:
    :return:
    """
    total_denominator = 0.0
    score = 0.0
    for key, value in request.data.items():
        if key != "A1":
            question = models.Question.objects.get(question_id=key)
            option_selected = models.Option.objects.get(option_id=value, question__question_id=key)
            total_denominator += question.weight
            score += (option_selected.weight * question.weight)
            models.Answer.objects.update_or_create(
                question_id=question.id, user=request.user, defaults={'option': option_selected})
        else:
            request.user.age = int(value)
            request.user.save()
            value = helpers.find_right_option(int(value))
            question = models.Question.objects.get(question_id=key)
            option_selected = models.Option.objects.get(option_id=value, question__question_id=key)
            total_denominator += question.weight
            score += (option_selected.weight * question.weight)
            models.Answer.objects.update_or_create(
                question_id=question.id, user=request.user, defaults={'option': option_selected})
    request.user.risk_score = round((score / total_denominator), 1)
    request.user.save()
    return True

def process_assess_answer_unregistered_users(request):
    """
    :param request:
    :return: risk score value
    """
    total_denominator = 0.0
    score = 0.0
    try:
        for key, value in request.data.items():
            if key != "A1":
                question = models.Question.objects.get(question_id=key)
                option_selected = models.Option.objects.get(option_id=value, question__question_id=key)
                total_denominator += question.weight
                score += (option_selected.weight * question.weight)
            else:
                value = helpers.find_right_option(int(value))
                question = models.Question.objects.get(question_id=key)
                option_selected = models.Option.objects.get(option_id=value, question__question_id=key)
                total_denominator += question.weight
                score += (option_selected.weight * question.weight)
        risk_score = round((score / total_denominator), 1)
    except:
        risk_score = None
    return risk_score



def make_allocation_dict(sip, lumpsum, allocation):
    """
    makes an allocation dict that can be used by get_number_of_funds utility to check if sip, lumpsum is above min level
    :param sip: sip for a goal
    :param lumpsum: lumpsum for a goal
    :param allocation: allocation for a goal
    :return: allocation dict in format to be used by get_number_of_funds utility
    """
    allocation_dict = {
        constants.EQUITY: {"lumpsum": lumpsum * int(allocation[constants.EQUITY]) / 100,
                           "sip": sip * int(allocation[constants.EQUITY]) / 100},
        constants.DEBT: {"lumpsum": lumpsum * int(allocation[constants.DEBT]) / 100,
                         "sip": sip * int(allocation[constants.DEBT]) / 100},
        constants.ELSS: {"lumpsum": lumpsum * int(allocation[constants.ELSS]) / 100,
                         "sip": sip * int(allocation[constants.ELSS]) / 100}
    }
    return allocation_dict


def roundTo100(amount1, amount2):
    amount1_remainder = amount1%100
    if amount1_remainder < 50:
        amount1 -= amount1_remainder
        amount2 += amount1_remainder
    else:
        amount1 += (100 - amount1_remainder)
        amount2 -= (100 - amount1_remainder)
    return amount1, amount2
    
def calculate_asset_allocation(lumpsum_amount, sip_amount, equity_allocation, debt_allocation):
    lumpsum_equity, lumpsum_debt, sip_equity, sip_debt = 0, 0, 0, 0
    if equity_allocation:
        lumpsum_equity = round((lumpsum_amount * float(equity_allocation)) / 100)
        sip_equity = round((sip_amount * float(equity_allocation)) / 100)
    
    if debt_allocation:
        lumpsum_debt = round((lumpsum_amount * float(debt_allocation)) / 100)
        sip_debt = round((sip_amount * float(debt_allocation)) / 100)
    
    if lumpsum_equity > 0 and lumpsum_debt > 0:
        if lumpsum_amount%100 == 0 and lumpsum_equity%100 > 0:
            lumpsum_equity, lumpsum_debt = roundTo100(lumpsum_equity, lumpsum_debt)
                
    if sip_equity > 0 and sip_debt > 0:
        if sip_amount%100 == 0 and sip_equity%100 > 0:
            sip_equity, sip_debt = roundTo100(sip_equity, sip_debt)
            
    return lumpsum_equity, lumpsum_debt, sip_equity, sip_debt
    

def calculate_overall_allocation(user, investment_date=None):
    """
    :param user_id:
    :param investment_date:the date for investing
    :return: a dictionary of overall allocation for user with keys - equity, elss and debt and values as - a dictionary
    with percentage and amount for respective ( elss, debt and equity )
    """
    from core import goals_helper #TODO
    
    goals = goals_helper.GoalBase.get_current_goals(user) 

    summary, status_summary = [], []
    total_equity, total_debt, total_elss = 0, 0, 0
    elss_lumpsum, elss_sip, debt_lumpsum, debt_sip, equity_lumpsum, equity_sip = 0, 0, 0, 0, 0, 0

    for goal in goals:
        investment_till_date = 0
        lumpsum_amount, sip_amount, term = 0, 0, 0

        category_allocation = goal.asset_allocation
        
        goal_object = goals_helper.GoalBase.get_goal_instance(goal)
        lumpsum_amount = goal_object.get_lumpsum_amount()
        sip_amount = goal_object.get_sip_amount()
        
        corpus, investment_till_date, term, debt, equity, elss = calculate_corpus_and_investment_till_date(goal, investment_date)

        if float(category_allocation[constants.ELSS]):
            elss_lumpsum += round((lumpsum_amount * float(category_allocation[constants.ELSS])) / 100)
            elss_sip += round((sip_amount * float(category_allocation[constants.ELSS])) / 100)
            
        equity_l, debt_l, equity_s, debt_s = calculate_asset_allocation(lumpsum_amount, sip_amount, float(category_allocation[constants.EQUITY]), float(category_allocation[constants.DEBT]))
        debt_lumpsum += debt_l
        debt_sip += debt_s
        equity_lumpsum += equity_l
        equity_sip += equity_s
        
        category_summary = {"goal": goal.name, "corpus": round(corpus, 2), "sip": sip_amount,
                            "lumpsum": lumpsum_amount, "term": term}
        goal_status = copy.deepcopy(category_summary)
        goal_status.update({'investment_till_date': investment_till_date})
        summary.append(category_summary)
        status_summary.append(goal_status)

    total_equity += equity_lumpsum + equity_sip * 12
    total_debt += debt_lumpsum + debt_sip * 12
    total_elss += elss_lumpsum + elss_sip * 12
    total_investment = total_equity + total_elss + total_debt  # total investment by user in all categories
    overall_allocation = {constants.EQUITY: {"percentage": helpers.percentage(total_equity, total_investment),
                                             "amount": total_equity},
                          constants.DEBT: {"percentage": helpers.percentage(total_debt, total_investment),
                                           "amount": total_debt},
                          constants.ELSS: {"percentage": helpers.percentage(total_elss, total_investment),
                                           "amount": total_elss}}
    overall_allocation_with_sip_lumpsum = {constants.EQUITY: {"lumpsum": equity_lumpsum, "sip": equity_sip},
                                           constants.DEBT: {"lumpsum": debt_lumpsum, "sip": debt_sip},
                                           constants.ELSS: {"lumpsum": elss_lumpsum, "sip": elss_sip},}
    result = {"overall_allocation": overall_allocation, "total_sum": total_investment, "summary": summary}
    return result, overall_allocation_with_sip_lumpsum, status_summary
        

def get_assess_answer(user):
    """
    :param request:
    :return:
    """
    # TODO : Research if this can be done through serializer
    answers_object = {}
    answers = models.Answer.objects.filter(question__question_for=constants.ASSESS, user=user)
    if len(answers) == 0:
        return answers_object
    for answer in answers:
        answers_object[answer.question.question_id] = answer.option.option_id
    answers_object["A1"] = str(user.age)
    return answers_object

def generate_goals_data(goal):
    category_answers_result = {}
    if not goal:
        return category_answers_result
    
    category_answers_result[constants.ALLOCATION] = goal.asset_allocation
    category_answers_result[constants.GOAL_NAME] = goal.name
    answers = goal.answer_set.all()
    
    for answer in answers:
        if answer.question.type == constants.TEXT:
            category_answers_result[answer.question.question_id] = int(answer.text)
        else:
            answer_bool_converted = True if models.Option.objects.get(id=answer.option_id).option_id == "op1" else False
            category_answers_result[answer.question.question_id] = answer_bool_converted
    
    return category_answers_result

def get_category_answers(user, question_for):
    """
    Works for any category that does not have multi text questions
    presently works for - retirement, wedding, other event, buy property, tax, invest, education
    :param user: the user whose answers are to be returned
    :param question_for: category for which answers ar to be returned
    :return:  dict of category related answers by user
    """
    from core import goals_helper
    
    goal = goals_helper.GoalBase.get_current_goal(user, constants.MAP[question_for])
    return generate_goals_data(goal)    


def get_plan_answers(user):
    """
    Returns plan answers for a user
    :param user:
    :return:
    """
    category_answers = {}
    specific_answers = models.Answer.objects.filter(user=user, question__question_for=constants.PLAN).select_related(
        'question')
    if len(specific_answers) == 0:
        return category_answers
    for answer in specific_answers:
        if answer.question.type == constants.TEXT:
            category_answers[answer.question.question_id] = answer.text
        elif answer.question.type == constants.RADIO:
            if answer.text == "":
                category_answers[answer.question.question_id] = models.Option.objects.get(id=answer.option_id).option_id
            else:
                category_answers[answer.question.question_id] = str(answer.option.option_id) + "," + str(answer.text)
    question_28_answers = models.Answer.objects.filter(user=user, question__question_id='P2').order_by('created_at')
    question_29_answers = models.Answer.objects.filter(user=user, question__question_id='P3').order_by('created_at')
    p2_answer = []
    for i in range(len(question_28_answers)):
        string_to_append = question_28_answers[i].text + "," + question_29_answers[i].text
        p2_answer.append(string_to_append)
    category_answers["P2"] = p2_answer
    return category_answers


def format_porfolioitems(equity_funds, debt_funds, elss_funds, is_error, errors):
    """
    :param equity_funds:the equity funds in user portfolio
    :param debt_funds:the debt funds in user portfolio
    :param elss_funds:the elss funds in user portfolio
    :param is_error:if there is error
    :param errors:the error dictionry
    :return:
    """
    return_value = {constants.RECOMMENDED_SCHEMES: []}
    if not is_error:
        if equity_funds.get("data"):
            return_value.get(constants.RECOMMENDED_SCHEMES).append(equity_funds)
        if debt_funds.get("data"):
            return_value.get(constants.RECOMMENDED_SCHEMES).append(debt_funds)
        if elss_funds.get("data"):
            return_value.get(constants.RECOMMENDED_SCHEMES).append(elss_funds)
        return return_value, errors
    else:
        return None, errors


def get_portfolio_items(user_id, overall_allocation, sip_lumpsum_allocation):
    """
    Assigns funds to user's portfolio if no entry is present in portfolio item for that user or returns the portfolio
    item list if an entry is already resent
    :param user_id: the id of active user
    :return: a dictionary of portfolio items of user
    """
    from core import goals_helper
    
    try:
        portfolio = models.Portfolio.objects.get(user_id=user_id, has_invested=False)
    except models.Portfolio.DoesNotExist:
        equity_funds, debt_funds, elss_funds, is_error, errors = create_portfolio_items(
            user_id, overall_allocation, sip_lumpsum_allocation)
        return format_porfolioitems(equity_funds, debt_funds, elss_funds, is_error, errors)
    
    latest_answer_time = goals_helper.GoalBase.get_current_goals(portfolio.user).latest(
        constants.MODIFIED_AT).modified_at
    portfolio_modified_time = models.Portfolio.objects.get(user_id=user_id, has_invested=False).modified_at
    if latest_answer_time > portfolio_modified_time:
        equity_funds, debt_funds, elss_funds, is_error, errors = create_portfolio_items(
            user_id, overall_allocation, sip_lumpsum_allocation)
        return format_porfolioitems(equity_funds, debt_funds, elss_funds, is_error, errors)
    else:
        equity_funds = get_recommended_schemes(user_id, constants.EQUITY)
        debt_funds = get_recommended_schemes(user_id, constants.DEBT)
        elss_funds = get_recommended_schemes(user_id, constants.ELSS)
        return format_porfolioitems(equity_funds, debt_funds, elss_funds, False, {})


def create_portfolio_items(user_id, overall_allocation, sip_lumpsum_allocation):
    """
    Utility to create portfolio items for a user
    :param user_id: the id of user for whom portfolio items are to be created
    :param overall_allocation: the overall allocation contains data for creating portfolio
    :param sip_lumpsum_allocation: contains relevant data to create portfolio items
    :return:
    """
    kwargs = {}
    for key in overall_allocation['overall_allocation'].keys():
        kwargs[key + "_percentage"] = overall_allocation['overall_allocation'][key]['percentage']
    kwargs['total_sum_invested'] = overall_allocation['total_sum']
    kwargs['investment_date'] = date.today()  # TODO change it after invest flow
    with transaction.atomic():
        start = transaction.savepoint()
        portfolio, created = models.Portfolio.objects.update_or_create(user_id=user_id, has_invested=False,
                                                                       defaults=kwargs)
        number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip, \
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum, is_error, \
        errors = get_number_of_funds(sip_lumpsum_allocation)
        if is_error:
            transaction.savepoint_rollback(start)
            try:
                models.PortfolioItem.objects.filter(portfolio_id=portfolio).delete()
                models.Portfolio.objects.get(user_id=user_id, has_invested=False).delete()
            except Exception:
                pass
            return None, None, None, is_error, errors
        if created:
            models.Goal.objects.filter(portfolio=None).update(portfolio=portfolio)
    get_funds_to_allocate_to_user(constants.EQUITY, number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum,
                                  sip_lumpsum_allocation, portfolio)
    get_funds_to_allocate_to_user(constants.DEBT, number_of_debt_funds_by_sip, number_of_debt_funds_by_lumpsum,
                                  sip_lumpsum_allocation, portfolio)
    get_funds_to_allocate_to_user(constants.ELSS, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum,
                                  sip_lumpsum_allocation, portfolio)
    equity_funds = get_recommended_schemes(user_id, constants.EQUITY)
    debt_funds = get_recommended_schemes(user_id, constants.DEBT)
    elss_funds = get_recommended_schemes(user_id, constants.ELSS)
    return equity_funds, debt_funds, elss_funds, is_error, errors


def get_number_of_funds(sip_lumpsum_allocation):
    """
    Algorithm to find number of funds to be allocated to the user for each category(elss, debt and equity)
    :param sip_lumpsum_allocation: the sip and lumpsum investment in debt, equity and elss
    :return: 3 integers which are respectively number of equity funds, debt funds and elss funds
    """
    errors = {}
    is_error = False
    equity_sip = sip_lumpsum_allocation[constants.EQUITY][constants.SIP]
    debt_sip = sip_lumpsum_allocation[constants.DEBT][constants.SIP]
    equity_lumpsum = sip_lumpsum_allocation[constants.EQUITY][constants.LUMPSUM]
    debt_lumpsum = sip_lumpsum_allocation[constants.DEBT][constants.LUMPSUM]
    elss_lumpsum = sip_lumpsum_allocation[constants.ELSS][constants.LUMPSUM]
    # TODO add numbers to constants
    equity_funds_by_sip = 4 if equity_sip >= 8000 else (
        3 if equity_sip >= 4500 else(2 if equity_sip >= 2000 else (1 if equity_sip >= 500 else (
            -1 if equity_sip > 0 else 0))))
    if equity_funds_by_sip is -1:
        is_error = True
        errors = update_error(errors, 'Sip amount in Equity', equity_sip, 500)
    debt_funds_by_sip = 3 if debt_sip >= 4500 else(2 if debt_sip >= 2000 else (1 if debt_sip >= 1000 else
                                                                               (-1 if debt_sip > 0 else 0)))
    if debt_funds_by_sip is -1:
        is_error = True
        errors = update_error(errors, 'Sip amount in Debt', debt_sip, 1000)
    equity_funds_by_lumpsum = 4 if equity_lumpsum >= 40000 else(
        3 if equity_lumpsum >= 20000 else (2 if equity_lumpsum >= 10000 else (1 if equity_lumpsum >= 5000 else
                                                                             (-1 if equity_lumpsum > 0 else 0))))
    if equity_funds_by_lumpsum is -1:
        is_error = True
        errors = update_error(errors, 'Lumpsum amount in Equity', equity_lumpsum, 5000)
    debt_funds_by_lumpsum = 3 if debt_lumpsum >= 20000 else(
        2 if debt_lumpsum >= 10000 else (1 if debt_lumpsum >= 5000 else (-1 if debt_lumpsum > 0 else 0)))
    if debt_funds_by_lumpsum is -1:
        is_error = True
        errors = update_error(errors, 'Lumpsum amount in Debt', debt_lumpsum, 5000)
    elss_funds_by_lumpsum = 2 if elss_lumpsum >= 5000 else(
    1 if elss_lumpsum >= 500 else (-1 if elss_lumpsum > 0 else 0))
    if elss_funds_by_lumpsum is -1:
        is_error = True
        errors = update_error(errors, 'Lumpsum amount in ELSS', elss_lumpsum, 500)
    return equity_funds_by_sip, equity_funds_by_lumpsum, debt_funds_by_sip, debt_funds_by_lumpsum, \
           constants.ELSS_FUNDS_BY_SIP, elss_funds_by_lumpsum, is_error, errors


def update_error(error_dictionary, type, user_amount, minimum_amount):
    """
    :param error_dictionary:the error dictionary in which we are appending error
    :param type: the type for which error occoured
    :param user_amount: the user amount
    :param minimum_amount: the minimum amount
    :return: appended dictionary
    """
    error_response = "Your {} schemes is Rs {}, which is below minimum required amount Rs {}. " \
                     "Please change total investment amount or asset allocation to meet the minimum requirement"
    error_dictionary.update({type: error_response.format(type, round(user_amount), minimum_amount)})
    return error_dictionary


def get_funds_to_allocate_to_user(type, number_of_funds_by_sip, number_of_funds_by_lumpsum, sip_lumpsum_allocation,
                                  portfolio, funds=None):
    """
    Algorithm to allocate funds to user according to his investment
    :param type: the type of funds (equity, elss or debt)
    :param number_of_funds_by_sip: number of funds to allocate to user by sip amount
    :param number_of_funds_by_lumpsum: number of funds to allocate to user by lumpsum amount
    :param sip_lumpsum_allocation: the sip and lumpsum allocation of user
    :param portfolio: the portfolio of user
    :param funds: a list of fund ids (default is none). In case funds is none the funds will be added according to
    fund ranks else the fund ids specified in the list will be added to portfolio
    :return: a dict of funds ids to allocate to user
    """
    
    fund_ids_updated = []
    number_of_funds = max(number_of_funds_by_lumpsum, number_of_funds_by_sip)
    if funds is None:
        if type == constants.EQUITY and number_of_funds == constants.MAX_NUMBER_EQUITY_FUNDS:
            
            fund_objects = recommendedPortfolio_equity(type)
            
        else:
            fund_objects = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[type], is_enabled=True
                                           ).order_by('fund_rank')[:number_of_funds]
    else:
        fund_data = models.Fund.objects.in_bulk(funds)
        fund_objects = [fund_data.get(id, None) for id in funds]
        fund_objects = filter(None, fund_objects)
    fund_allocation = amount_allocation(type, number_of_funds_by_sip, number_of_funds_by_lumpsum,
                                        sip_lumpsum_allocation[type])
    for index, fund in enumerate(fund_objects):
        kwargs = {}
        kwargs["broad_category_group"] = fund.type_of_fund
        kwargs[constants.SIP] = fund_allocation[constants.SIP][index]
        kwargs[constants.LUMPSUM] = fund_allocation[constants.LUMPSUM][index]
        kwargs['sum_invested'] = int(fund_allocation[constants.SIP][index] + fund_allocation[constants.LUMPSUM][index])
        models.PortfolioItem.objects.update_or_create(portfolio_id=portfolio.id, fund_id=fund.id, defaults=kwargs)
        fund_ids_updated.append(fund.id)
    funds_to_be_deleted = models.PortfolioItem.objects.filter(
        portfolio_id=portfolio, fund__type_of_fund=constants.FUND_MAP[type]).exclude(fund__id__in=fund_ids_updated)
    funds_to_be_deleted.delete()


def recommendedPortfolio_equity(type):
    fund_objects = []
    
    mid_cap_count = constants.MAX_NUMBER_EQUITY_FUNDS - constants.MAX_NUMBER_EQUITY_FUNDS_LARGE
    
    fund_object_cat1 = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[type], 
                                                         category_name=constants.FUND_CATEGORY_NAME_LARGE, is_enabled=True
                                                         ).order_by('fund_rank')[:constants.MAX_NUMBER_EQUITY_FUNDS_LARGE]
    fund_objects.extend(fund_object_cat1)
            
    fund_object_cat2 = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[type], 
                                                          category_name=constants.FUND_CATEGORY_NAME_MID, is_enabled=True
                                                          ).order_by('fund_rank')[:mid_cap_count]
    fund_objects.extend(fund_object_cat2)
    
    return fund_objects
    

def amount_allocation(type, number_of_funds_by_sip, number_of_funds_by_lumpsum, sip_lumpsum_allocation):
    """
    :param type: the type for which we are allocating
    :param number_of_funds_by_sip: number of funds to be allocated to user on basis of sip
    :param sip_lumpsum_allocation: number of funds to be allocated to user on basis of lumpsum
    :return:
    """
    lumpsum_amount = int(sip_lumpsum_allocation[constants.LUMPSUM])
    sip_amount = int(sip_lumpsum_allocation[constants.SIP])
    sip_allocation, lumpsum_allocation = [], []
    sip_amount_left, lumpsum_amount_left = sip_amount, lumpsum_amount
    for i in range(max(number_of_funds_by_sip, number_of_funds_by_lumpsum)):
        if type == constants.ELSS:
            sip = 0
            if i == 0:
                lumpsum = math.ceil(lumpsum_amount/(number_of_funds_by_lumpsum*500)) * 500
            else:
                lumpsum = lumpsum_amount_left
        else:
            if i == number_of_funds_by_sip - 1:
                sip = sip_amount_left
            elif i >= number_of_funds_by_sip:
                sip = 0
            else:
                base_amount_sip = math.floor(sip_amount/(number_of_funds_by_sip*100)) * 100
                check_amount_sip = sip_amount - base_amount_sip * number_of_funds_by_sip
                extra_amount_sip = 100 if check_amount_sip > 100 * (i+1) else(
                    check_amount_sip - (i * 100) if check_amount_sip > 100 * i else 0)
                sip = base_amount_sip + extra_amount_sip
            if i == number_of_funds_by_lumpsum - 1:
                lumpsum = lumpsum_amount_left
            elif i >= number_of_funds_by_lumpsum:
                lumpsum = 0
            else:
                base_amount_lumpsum = math.floor(lumpsum_amount/(number_of_funds_by_lumpsum*100)) * 100
                check_amount_lumpsum = lumpsum_amount - base_amount_lumpsum * number_of_funds_by_lumpsum
                extra_amount_lumpsum = 100 if check_amount_lumpsum > 100 * (i+1) else(
                    check_amount_lumpsum - (i*100) if check_amount_lumpsum > 100 * i else 0)
                lumpsum = base_amount_lumpsum + extra_amount_lumpsum

        sip_allocation.append(sip)
        lumpsum_allocation.append(lumpsum)
        sip_amount_left -= sip
        lumpsum_amount_left -= lumpsum
    return {constants.SIP: sip_allocation, constants.LUMPSUM: lumpsum_allocation}


def get_recommended_schemes(user_id, type):
    """

    :param user_id:
    :param type:
    :return:
    """
    portfolio_dict = {"key": type}
    portfolio_data = []
    portfolio_items = models.PortfolioItem.objects.filter(broad_category_group=constants.FUND_MAP[type],
                                                          portfolio__user_id=user_id, portfolio__has_invested=False
                                                          ).select_related('fund').order_by('fund__fund_rank')
    for portfolio_item in portfolio_items:
        portfolio_data.append({"id": portfolio_item.fund.id, "fund_name": portfolio_item.fund.fund_name,
                               "sip": portfolio_item.sip, "lumpsum": portfolio_item.lumpsum, 
                               "category_name": portfolio_item.fund.category_name})
    portfolio_dict['data'] = portfolio_data
    return portfolio_dict


def get_recommended_and_scheme_funds(user_id):
    """
    Utility to return funds of user divided into elss , equity, debt and each category having two subsections-
    -Funds in portfolio item of user
    -Other recommended schemes not in user portfolio
    :param user_id: The id of the user
    :return: a list of funds f user in different category
    """
    equity_funds, debt_funds, elss_funds, user_fund_ids = [], [], [], []
    user_equity_funds, user_debt_funds, user_elss_funds = [], [], []
    # get schemes under user portfolio items
    user_portfolio_items = models.PortfolioItem.objects.filter(portfolio__user_id=user_id, portfolio__has_invested=False
                                                               ).order_by('fund__fund_rank')
    # makes a list of the ids of funds in user portfolio items
    for portfolio_item in user_portfolio_items:
        user_fund_ids.append(portfolio_item.fund.id)
    # get all funds in morning star excluding those in user portfolio items
    all_funds = models.Fund.objects.exclude(id__in=user_fund_ids).exclude(is_enabled=False).order_by('fund_rank')
    # divides all funds(excluding those in user portfolio items) under elss, equity, debt
    for fund in all_funds:
        if fund.type_of_fund == constants.FUND_MAP[constants.EQUITY]:
            equity_funds.append(fund)
        elif fund.type_of_fund == constants.FUND_MAP[constants.DEBT]:
            debt_funds.append(fund)
        else:
            elss_funds.append(fund)
    # divides user portfolio funds under elss, equity, debt
    for user_portfolio_item in user_portfolio_items:
        if user_portfolio_item.fund.type_of_fund == constants.FUND_MAP[constants.EQUITY]:
            user_equity_funds.append(user_portfolio_item.fund)
        elif user_portfolio_item.fund.type_of_fund == constants.FUND_MAP[constants.DEBT]:
            user_debt_funds.append(user_portfolio_item.fund)
        else:
            user_elss_funds.append(user_portfolio_item.fund)
    return equity_funds, debt_funds, elss_funds, user_equity_funds, user_debt_funds, user_elss_funds


def get_scheme_details(fund, monthly_data_points, daily_data_points):
    """
    utility to return scheme details dict for schema fact sheet
    :param fund: data points from fund model
    :param monthly_data_points: data points from data points change monthly model
    :param daily_data_points: data points from data points change daily model
    :return:
    """
    scheme_details = {}
    fund_serializer = serializers.FundSerializer(fund)
    monthly_data_point_serializer = serializers.FundDataPointsChangeMonthlySerializer(monthly_data_points)
    daily_data_point_serializer = serializers.FundDataPointsChangeDailySerializer(daily_data_points)
    fund_detail = fund_serializer.data.copy()
    fund_detail.update(monthly_data_point_serializer.data)
    fund_detail.update(daily_data_point_serializer.data)
    for field in constants.SCHEME_DETAILS_LIST:
        if field == constants.DESCRIPTION:
            scheme_details[field] = fund.get_type_of_fund_display() + ":" + fund.category_name + "|" + " ".join(
                fund.legal_structure.split(" ")[:2])
        elif field == constants.DAY_CHANGE_NAV:
            scheme_details[field] = str(round(fund_detail[constants.CAPITAL_GAIN], 2)) + \
                                    "(" + str(round(fund_detail[constants.CAPITAL_GAIN_PERCENTAGE], 2)) + "%)"
        elif field == constants.IMAGE_URL:
            # TODO: http or https?
            scheme_details[field] = fund_detail[constants.IMAGE_URL]
        elif field == constants.DAY_END_DATE:
            day_end_date = datetime.strptime(fund_detail[field], '%Y-%m-%d').date()
            # scheme_details[field] = datetime.strftime(day_end_date, '%d-%m-%Y')
            scheme_details[field] = day_end_date.strftime('%d-%m-%Y')
        elif field == constants.AUM:
            scheme_details[field] = calculate_aum_in_string(fund_detail[field], 0)
        else:
            scheme_details[field] = fund_detail[field]
        if type(scheme_details[field]) is float and field != constants.DAY_END_NAV:
            scheme_details[field] = round(scheme_details[field], 2)
        if field == constants.DAY_END_NAV:
            scheme_details[field] = format(scheme_details[field], '.4f')

    return scheme_details


def calculate_aum_in_string(aum, decimal_point=1):
    """
    :param aum: aum in integer
    :return: aum in string format
    """
    if aum >= 10000000:
        if decimal_point == 0:
            return str(round(aum / 10000000)) + ' Cr'
        return str(round(aum / 10000000, decimal_point)) + ' Cr'
    elif aum >= 100000:
        if decimal_point == 0:
            return str(round(aum / 100000)) + ' L'
        return str(round(aum / 100000, decimal_point)) + ' L'
    elif aum >= 1000:
        if decimal_point == 0:
            return str(round(aum / 1000)) + ' K'
        return str(round(aum / 1000, decimal_point)) + ' K'
    else:
        return str(aum)


def get_debt_portfolio(debt_data_points):
    """
    utility portfolio for debt funds
    :param debt_data_points: data points from debt model
    :return:
    """
    top_block_portfolio, bottom_block_portfolio = [], []
    debt_serializer = serializers.DebtFundSerializer(debt_data_points).data
    for field in constants.TOP_PORTFOLIO_DEBT:
        if field == constants.NUMBER_OF_HOLDINGS:
            top_block_portfolio.append({constants.KEY: field,
                                        constants.VALUE: round(debt_serializer[constants.TOP_PORTFOLIO_MAP[field]])})
        else:
            top_block_portfolio.append({constants.KEY: field,
                                        constants.VALUE: round(debt_serializer[constants.TOP_PORTFOLIO_MAP[field]], 2)})
    bottom_block_portfolio.append({constants.KEY: constants.TOP_THREE_HOLDING_PORTFOLIO,
                                   constants.VALUE: round_holdings_to_two_decimals(ast.literal_eval(
                                       debt_serializer[constants.NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS][
                                           constants.HOLDINGS])[0:3])})
    credit_quality_list = []
    for credit_quality in constants.CREDIT_QUALITY_LIST:
        credit_quality_list.append(
            {constants.WEIGHTING: round(debt_serializer[constants.CREDIT_QUALITY_MAP[credit_quality]], 2),
             constants.KEY_NAME: credit_quality})
    bottom_block_portfolio.append({constants.KEY: constants.CREDIT_QUALITY, constants.VALUE: credit_quality_list})
    return {constants.TOP: top_block_portfolio, constants.BOTTOM: bottom_block_portfolio}


def round_holdings_to_two_decimals(holding_list):
    """
    Rounds off weighting in holdings to two decimals
    :param holding_list: a list of holdings in dict format
    :return:
    """
    return [{constants.KEY_NAME: x.get(constants.KEY_NAME),
             constants.WEIGHTING: round(float(x.get(constants.WEIGHTING)), 2)} for x in holding_list]


def get_equity_portfolio(equity_data_points, sector_data_points):
    """
    utility to return portfolio for equity and elss funds
    :param equity_data_points: data points of equity data model
    :param sector_data_points: data points for sector data model
    :return:
    """
    top_block_portfolio, bottom_block_portfolio = [], []
    equity_serializer = serializers.EquityFundSerializer(equity_data_points).data
    sector_serializer = serializers.SectorFundSerializer(sector_data_points).data
    for field in constants.TOP_PORTFOLIO_EQUITY:
        if field == constants.NUMBER_OF_HOLDINGS:
            top_block_portfolio.append(
                {constants.KEY: field,
                 constants.VALUE: round(equity_serializer[constants.TOP_PORTFOLIO_MAP_EQUITY[field]])})
        else:
            top_block_portfolio.append(
                {constants.KEY: field,
                 constants.VALUE: round(equity_serializer[constants.TOP_PORTFOLIO_MAP_EQUITY[field]], 2)})

    top_five_holdings = ast.literal_eval(equity_serializer[constants.NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS]
                                         [constants.HOLDINGS])
    top_five_holdings_rounded = []
    for holding in top_five_holdings:
        top_five_holdings_rounded.append({constants.KEY_NAME: holding.get(constants.KEY_NAME), constants.WEIGHTING:
            round(float(holding.get(constants.WEIGHTING)), 2)})

    top_five_holding_percentage = 0
    for holding in top_five_holdings:
        top_five_holding_percentage += float(holding[constants.WEIGHTING])
    bottom_block_portfolio.append({constants.KEY: constants.TOP_FIVE_HOLDING,
                                constants.VALUE: top_five_holdings_rounded,
                                constants.TOTAL: round(top_five_holding_percentage, 2)})
    # top_block_portfolio.append({constants.KEY: constants.TOP_THREE_SECTORS,
    #                             constants.VALUE: round(sector_serializer[constants.FIRST_WEIGHT] +
    #                                                    sector_serializer[constants.SECOND_WEIGHT] +
    #                                                    sector_serializer[constants.THIRD_WEIGHT], 2)})

    # bottom_block_portfolio.append({constants.KEY: constants.TOP_THREE_HOLDING_PORTFOLIO,
    #                                constants.VALUE: round_holdings_to_two_decimals(ast.literal_eval(
    #                                    equity_serializer[constants.NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS]
    #                                    [constants.HOLDINGS])[:3])})

    top_three_sector_list = [{constants.KEY_NAME: reduce_sector_name(sector_serializer[constants.FIRST_NAME]),
                              constants.WEIGHTING: round(sector_serializer[constants.FIRST_WEIGHT], 2)},
                             {constants.KEY_NAME: reduce_sector_name(sector_serializer[constants.SECOND_NAME]),
                              constants.WEIGHTING: round(sector_serializer[constants.SECOND_WEIGHT], 2)},
                             {constants.KEY_NAME: reduce_sector_name(sector_serializer[constants.THIRD_NAME]),
                              constants.WEIGHTING: round(sector_serializer[constants.THIRD_WEIGHT], 2)}]

    bottom_block_portfolio.append({constants.KEY: constants.TOP_THREE_SECTORS_PORTFOLIO,
                                   constants.VALUE: top_three_sector_list,
                                   constants.TOTAL: round(sector_serializer[constants.FIRST_WEIGHT] +
                                                          sector_serializer[constants.SECOND_WEIGHT] +
                                                          sector_serializer[constants.THIRD_WEIGHT], 2)})
    return {constants.TOP: top_block_portfolio, constants.BOTTOM: bottom_block_portfolio}


def reduce_sector_name(original_sector_name):
    """
    :param original_sector_name:the orignal sector name
    :return: the modified sector name
    """
    return " ".join(re.findall('[A-Z][^A-Z]*', original_sector_name[12:-12]))


def get_key_performance(fund, monthly_data_points, daily_data_points):
    """

    :param fund: fund data points
    :param monthly_data_points:  data points from monthly change model
    :param daily_data_points: data points from daily change model
    :return:
    """
    key_performance = []
    fund_serializer = serializers.FundSerializer(fund)
    monthly_data_point_serializer = serializers.FundDataPointsChangeMonthlySerializer(monthly_data_points)
    daily_data_point_serializer = serializers.FundDataPointsChangeDailySerializer(daily_data_points)
    fund_detail = fund_serializer.data.copy()
    fund_detail.update(monthly_data_point_serializer.data)
    fund_detail.update(daily_data_point_serializer.data)
    for field in constants.KEY_PERFORMANCE_FIELD_LIST:
        if field == constants.INCEPTION_DATE:
            inception_date = datetime.strptime(fund_detail[field], '%Y-%m-%d').date()
            key_performance.append({constants.KEY: constants.KEY_PERFORMANCE_MAP[field],
                                    constants.VALUE: datetime.strftime(inception_date, '%d-%m-%Y')})
        elif field == constants.MINIMUM_INVESTMENT or field == constants.MINIMUM_SIP_INVESTMENT:
            key_performance.append({constants.KEY: constants.KEY_PERFORMANCE_MAP[field],
                                    constants.VALUE: format(round(fund_detail[field]), ',')})
        else:
            key_performance.append({constants.KEY: constants.KEY_PERFORMANCE_MAP[field],
                                    constants.VALUE: fund_detail[field]})
    investment_strategy = fund_detail[constants.INVESTMENT_STRATEGY]
    managers = ast.literal_eval(monthly_data_point_serializer.data[constants.MANAGERS][constants.MANAGERS])
    manager_name = ''
    start_date = datetime.strptime(managers[0][constants.START_DATE], "%Y-%m-%d").strftime("%d-%m-%Y")
    for manager in managers:
        manager_name = '/'.join([manager_name, manager[constants.FUND_MANAGR_NAME_KEY]])
    key_performance.append({constants.KEY: constants.FUND_MANAGER_NAME, constants.VALUE: manager_name[1:]})
    key_performance.append({constants.KEY: constants.FUND_MANAGER_START_DATE, constants.VALUE: start_date})
    return key_performance, investment_strategy


def get_compared_data(fund_ids):
    """
    A utility to make dictionary for compared funds according to fund_ids
    :param fund_ids: an array of fund ids that needs to be compared
    :return: a dictionary for compared fund data
    """
    compared_fund, category_other_data, fund_types = [], [], []
    funds = models.Fund.objects.filter(id__in=fund_ids).order_by('id')
    funds_daily_change_data_points = models.FundDataPointsChangeDaily.objects.filter(
        fund__id__in=fund_ids).order_by('fund__id')
    for index, fund in enumerate(funds):
        compared_fund.append(
            {constants.ID: fund.id, constants.FUND_NAME: fund.fund_name,
             constants.RETURN_ONE_YEAR: round(funds_daily_change_data_points[index].return_one_year, 2),
             constants.RETURN_THREE_YEAR: round(funds_daily_change_data_points[index].return_three_year, 2),
             constants.RETURN_FIVE_YEAR: round(funds_daily_change_data_points[index].return_five_year, 2)})
        fund_types.append(fund.type_of_fund)
    if len(set(fund_types)) == 1:
        if fund_types[0] == constants.FUND_MAP[constants.DEBT]:
            funds_debt_data_points = models.DebtFunds.objects.filter(fund__id__in=fund_ids).order_by('fund__id')
            fund_data_points_monthly = models.FundDataPointsChangeMonthly.objects.filter(
                fund__id__in=fund_ids).order_by('fund__id')
            fund_data_points_daily = models.FundDataPointsChangeDaily.objects.filter(fund__id__in=fund_ids).order_by(
                'fund__id')
            for index, fund in enumerate(funds):
                category_other_data.append({
                    constants.ID: fund.id, constants.FUND_NAME: fund.fund_name,
                    constants.AUM: calculate_aum_in_string(round(fund_data_points_daily[index].aum), 0),
                    constants.CREDIT_QUALITY: funds_debt_data_points[index].average_credit_quality,
                    constants.MAX_DEFERRED_LOAD: fund_data_points_monthly[index].max_deferred_load,
                    constants.AVERAGE_MATURITY: funds_debt_data_points[index].average_maturity,
                    constants.YIELD_TO_MATURITY: round(funds_debt_data_points[index].yield_to_maturity, 2)})
            return True, {constants.COMAPRED_FUND: compared_fund, constants.DEBT_OTHER_DATA: category_other_data,
                          constants.EQUITY_OTHER_DATA: constants.EMPTY_lIST_FOR_DATA}
        else:
            funds_equity_data_points = models.EquityFunds.objects.filter(fund__id__in=fund_ids).order_by('fund__id')
            fund_data_points_daily = models.FundDataPointsChangeDaily.objects.filter(fund__id__in=fund_ids).order_by(
                'fund__id')
            fund_data_points_monthly = models.FundDataPointsChangeMonthly.objects.filter(
                fund__id__in=fund_ids).order_by('fund__id')
            for index, fund in enumerate(funds):
                category_other_data.append({
                    constants.ID: fund.id, constants.FUND_NAME: fund.fund_name,
                    constants.AUM: calculate_aum_in_string(round(fund_data_points_daily[index].aum), 0),
                    constants.EXPENSE_RATIO: fund_data_points_monthly[index].expense_ratio,
                    constants.MAX_DEFERRED_LOAD: fund_data_points_monthly[index].max_deferred_load,
                    constants.TOP_TEN_HOLDING: round(funds_equity_data_points[index].top_ten_holdings, 2),
                    constants.BETA: fund_data_points_daily[index].beta})
            return True, {constants.COMAPRED_FUND: compared_fund, constants.EQUITY_OTHER_DATA: category_other_data,
                          constants.DEBT_OTHER_DATA: constants.EMPTY_lIST_FOR_DATA}
    else:
        return False, None


def get_annualised_return(portfolio_items, nav_list):
    """
    Utility to return annualised data for user portfolio
    :param portfolio_items: all portfolio item objects related to user portfolio
    :param nav_list: a list of nav fro the funds in portfolio items of user at dates required
    :return:
    """
    portfolio_item_map, nav_list_map, = {constants.EQUITY: [], constants.DEBT: [], constants.ELSS: []}, {}
    # 0 is current category value, 1 represents value 1 year earlier , 2 is value 3 years earlier
    #  and 4 is value 5 years earlier
    category_value_map = {constants.EQUITY: [0, 0, 0, 0], constants.DEBT: [0, 0, 0, 0], constants.ELSS: [0, 0, 0, 0]}
    portfolio_value_map = [0, 0, 0, 0]
    annualised_return = []

    # make a map of fund nav
    for nav in nav_list:
        try:
            nav_list_map[nav.fund_id.id].append(nav.nav)
        except KeyError:
            nav_list_map.update({nav.fund_id.id: [nav.nav]})

    # loop through portfolio items and calculate category values according to the fund weighted
    for portfolio_item in portfolio_items:
        portfolio_fund_navs = nav_list_map.get(portfolio_item.fund_id)
        portfolio_item_weightage = portfolio_item.sum_invested / portfolio_fund_navs[0]
        # category_values = category_value_map[constants.FUND_MAP_REVERSE[portfolio_item.broad_category_group]]
        for index in range(len(portfolio_fund_navs)):
            category_value_map[constants.FUND_MAP_REVERSE[portfolio_item.broad_category_group]][index] += \
                portfolio_fund_navs[index] * portfolio_item_weightage
            portfolio_value_map[index] += portfolio_fund_navs[index] * portfolio_item_weightage
    for category in category_value_map:
        if category_value_map[category][3]:
            category_returns = get_annualized_returns(category_value_map[category])
            annualised_return.append(get_category_returns(category_returns, category))
    portfolio_returns = get_annualized_returns(portfolio_value_map)
    annualised_return.append(get_category_returns(portfolio_returns, constants.PORTFOLIO))
    return annualised_return


def get_annualised_return_for_index(nav_list_for_indices):
    """
    Returns annualised returns for indices
    :param nav_list_for_indices: nav list of index for one, two and three year
    :return:
    """
    index_returns = get_annualized_returns(nav_list_for_indices)
    return {constants.NAME: constants.SENSEX, constants.ONE_YEAR_RETURN: round(index_returns[0], 2),
            constants.TWO_YEAR_RETURN: round(index_returns[1], 2),
            constants.THREE_YEAR_RETURN: round(index_returns[2], 2)}


def get_dates_for_nav(latest_date):
    """
    Return a list of dates containing today date, date one year ago, date 2 years ago, date 3 years ago
    :return:
    """
    return [latest_date, next_working_day(latest_date - relativedelta(years=1)),
            next_working_day(latest_date - relativedelta(years=3)),
            next_working_day(latest_date - relativedelta(years=5))]


def next_working_day(date):
    """
    :param date:
    :return:
    """
    if date.isoweekday() < 6:
        return date
    elif date.isoweekday() == 6:
        return date + timedelta(days=2)
    elif date.isoweekday() == 7:
        return date + timedelta(days=1)


def get_annualized_returns(nav_list):
    """
    Returns a list of one year, two year and three year returns
    :param nav_list: a list whose elements are in order - nav today, nav one year earlier, nav two years earlier,
    nav three years earlier
    :return: a list whose elemnts are in order - one year return , two year return and three year return
    """
    one_year_return = ((nav_list[0] - nav_list[1]) * 100 / nav_list[1])
    three_year_return_cumulative = (nav_list[0] / nav_list[2])
    five_year_return_cumulative = (nav_list[0] / nav_list[3])
    return [one_year_return, calculate_annulaized_return(three_year_return_cumulative, 3),
            calculate_annulaized_return(five_year_return_cumulative, 5)]


def calculate_annulaized_return(cumulative_return, years):
    """
    calculates and returns annualized return
    :param cumulative_return: the cumulative return
    :param years: the timeframe of cumulative return
    :return: annualized return
    """
    return (pow(cumulative_return, 1/years) - 1) * 100


def returns_normalized(category_fund_returns, total_investment):
    """
    Calculates the normalized returns of funds according to their weightage
    :param category_fund_returns: a list with fund returns and the amount that was invested
    :param total_investment: total investment of all funds
    :return: the average weighted returns of all the funds
    """
    normalized_returns = []
    for fund_return in category_fund_returns:
        fund_investment = fund_return[0]
        normalized_fund_return = []
        for returns in fund_return[1]:
            normalized_fund_return.append((fund_investment * returns) / total_investment)
        normalized_returns.append(normalized_fund_return)
    return normalized_returns


def get_category_returns(normalized_fund_returns, category):
    """
    utility to calculate returns of a category for one, two and three years
    :param normalized_fund_returns: the normalized fund returns under that category of usr portfolio
    :param category: the category for which returns is being calculated
    :return: category returns based on normalized fund returns
    """
    return {constants.NAME: category, constants.ONE_YEAR_RETURN: round(normalized_fund_returns[0], 2),
            constants.TWO_YEAR_RETURN: round(normalized_fund_returns[1], 2),
            constants.THREE_YEAR_RETURN: round(normalized_fund_returns[2], 2)}


def calculate_next_sip(sip, year, growth):
    """
    :param sip: initial sip amount
    :param year: number of years
    :param growth: annual percent growth
    :return:
    """
    sip = sip * pow((1 + growth), year)
    return sip


def get_expected_corpus(type, lumpsum, init_sip, month, debt, equity, growth=0.0, debt_gain=2 / 300,
                        equity_gain=0.01, elss_gain=0.01):
    """
    :param type: the category(tax, invest etc) for which expected corpus is being calculated
    :param lumpsum: lumpsum
    :param init_sip: initial sip
    :param month: month for growth
    :param debt: debt percentage split user selected
    :param equity: equity percentage split user selected
    :param growth: if we expect growth of sip yearly then its % (optional) divide by 100 before setting
    :param debt_gain: fixed for now equal 0.0066666666 for month growth (ie 8% annual growth)
    :param equity_gain: fixed for now 0.01 for month (ie 12% annual growth)
    :param elss_gain: fixed for now 0.01 for month (ie 12% annual growth)

    :return: Amount the person expects after investing
    """
    if type == "tax":
        for i in range(1, month + 1):
            lumpsum = lumpsum * (1 + elss_gain)
        return lumpsum

    debt_init = lumpsum * debt
    equity_init = lumpsum * equity
    debt_addn_amount = init_sip * debt
    equity_addn_amount = init_sip * equity
    total_init = 0.0

    for i in range(1, month + 1):
        debt_gain_amt = (debt_init + debt_addn_amount) * debt_gain
        equity_gain_amt = (equity_init + equity_addn_amount) * equity_gain
        next = (i) // 12  # mojo to find the year for next sip
        sip = calculate_next_sip(init_sip, next, growth)
        debt_init = debt_gain_amt + debt_init + debt_addn_amount
        equity_init = equity_gain_amt + equity_init + equity_addn_amount
        total_init = debt_init + equity_init
        debt_addn_amount = sip * debt
        equity_addn_amount = sip * equity
    return total_init


def get_fund_historic_data(funds, start_date, end_date, send_normalized_data=True, benchmark=constants.INDEX_NAME,
                           category=None):
    """
    A utility to return historic data of fund and related benchmarks in an array
    :param funds: a list of fund objects or a single fund object
    :param start_date: the start date
    :param end_date: the end date
    :param benchmark: the benchmark related to fund
    :param category: the category related to fund
    :param send_normalized_data: a flag to determine to send either normalized or simple data
    :return: three arrays - dates, historic data of fund on these dates, historic data of benchmark on these dates
    """
    funds_historic_data, category_historic_data = [], []
    date_list = [start_date + timedelta(days=num_of_days) for num_of_days in range((end_date - start_date).days + 1)
                 if (start_date + timedelta(num_of_days)).isoweekday() < 6]  # 6,7 is for saturday, sunday
    for fund in funds:
        funds_historic_data.append(
            {constants.ID: fund.fund_name, constants.VALUE: models.HistoricalFundData.objects.filter(
                fund_id=fund, date__in=date_list).order_by(constants.DATE).values_list(constants.NAV, flat=True)})
    index = models.Indices.objects.get(index_name=benchmark)
    index_historic_data = models.HistoricalIndexData.objects.filter(
        index=index, date__in=date_list).order_by(constants.DATE).values_list(constants.NAV, flat=True)
    if category is not None:
        category_historic_data = models.HistoricalCategoryData.objects.filter(
            category_code=category, date__in=date_list).order_by(constants.DATE).values_list(constants.NAV, flat=True)
    date_list = change_date_format(date_list)
    if send_normalized_data is True:
        funds_historic_data, index_historic_data, category_historic_data = normalize_data(
            funds_historic_data, index_historic_data, category_historic_data)
    return {constants.DATES: date_list, constants.FUND: funds_historic_data, constants.INDEX: index_historic_data,
            constants.CATEGORY: category_historic_data}


def get_fund_historic_data_tracker(funds, start_date, end_date):
    """
    A utility to return historic data of fund and related benchmarks in an array
    :param funds: a list of fund objects or a single fund object
    :param start_date: the start date
    :param end_date: the end date
    :return: two arrays - dates, historic data of fund on these dates
    """
    funds_historic_data, category_historic_data = [], []

    date_list = [start_date + timedelta(days=num_of_days) for num_of_days in range((end_date - start_date).days + 1)
                 if (start_date + timedelta(num_of_days)).isoweekday() < 6]  # 6,7 is for saturday, sunday
    for fund in funds:
        historic_data = list(models.HistoricalFundData.objects.filter(
            fund_id=fund, date__in=date_list).order_by(constants.DATE).values_list(constants.NAV, flat=True))
        for i in range(len(date_list)-len(historic_data)):
            historic_data.append(historic_data[-1])
        funds_historic_data.append({constants.ID: fund.fund_name, constants.VALUE: historic_data})
    date_list = change_date_format(date_list)
    return {constants.DATES: date_list, constants.FUND: funds_historic_data}


def change_date_format(date_list):
    """
    a utility to change date format from yyyy-mm-dd to dd-mm-yy
    :param date_list: the list of ates whose format is to be changed
    :return:
    """
    date_list_new_format = []
    for date in date_list:
        date_list_new_format.append(datetime.strftime(date, '%d-%m-%y'))
    return date_list_new_format


def normalize_data(funds_value_list, index_value_list, category_value_list):
    """
    helper to normalize value_list
    :param funds_value_list: a list containing list of values to be normalized
    :param index_value_list: a list containing values to be normalized
    :param category_value_list: a list containing values to be normalized
    :return:
    """
    logger = logging.getLogger('django.debug')
    logger.debug('category: ' + str(len(category_value_list)) + ' index: ' + str(len(index_value_list)) + ' fund: '+ str(
        len(funds_value_list[0].get(constants.VALUE))))

    normalized_funds_value_list, normalized_index_value_list, normalized_category_value_list = [], [], []
    for fund_value_list in funds_value_list:
        normalization_value = 100.00 / fund_value_list[constants.VALUE][0]
        normalized_fund_value_list = []
        for value in fund_value_list[constants.VALUE]:
            normalized_fund_value_list.append(round(value * normalization_value, 6))
        normalized_funds_value_list.append({constants.ID: fund_value_list[constants.ID],
                                            constants.VALUE: normalized_fund_value_list})
    normalization_value = 100.00 / index_value_list[0]
    for index in range(len(index_value_list)):
        normalized_index_value_list.append(round(index_value_list[index] * normalization_value, 2))

    for index in range(len(category_value_list)):
        if len(category_value_list) != 0:
            normalized_category_value_list.append(
                round(category_value_list[index] * 100.00 / category_value_list[0], 2))
    return normalized_funds_value_list, normalized_index_value_list, normalized_category_value_list


def expected_corpus(year, monthly_sip, lumpsum, equity_asset_allocation, debt_asset_allocation, growth_rate=0.0,
                    MONTHLY_EXPECTED_EQUITY=pow(1.12, 1/12)-1, MONTHLY_EXPECTED_DEBT=pow(1.08, 1/12)-1):
    """
    :param year:
    :param monthly_sip:
    :param lumpsum:
    :param equity_asset_allocation:
    :param debt_asset_allocation:
    :param growth_rate:
    :param MONTHLY_EXPECTED_EQUITY:
    :param MONTHLY_EXPECTED_DEBT:
    :return:
    # TODO: document this
    """
    expected_corpus_total = 0.0
    for i in range(int(year) + 1):
        end_of_month_equity = calculate_end_of_year_sum(MONTHLY_EXPECTED_EQUITY,
                                                        monthly_sip * (equity_asset_allocation), i, growth_rate,
                                                        lumpsum * (equity_asset_allocation))
        end_of_month_debt = calculate_end_of_year_sum(MONTHLY_EXPECTED_DEBT, monthly_sip * (debt_asset_allocation), i,
                                                      growth_rate, lumpsum * (debt_asset_allocation))
        expected_corpus_total = end_of_month_equity + end_of_month_debt
    return round(expected_corpus_total)


def calculate_end_of_year_sum(rate, pmt, current_year, growth_rate, lumpsum):
    """
    # TODO : document this too
    :param rate:
    :param pmt:
    :param current_year:
    :param growth_rate:
    :param lumpsum:
    :return:
    """
    power, pow1, pow3 = pow(1 + rate, +12), pow(1 + rate, current_year * 12), pow(1 + growth_rate, current_year)
    fvsip = ((pmt * (1 + rate)) * (power - 1) * (pow1 - pow3)) / (rate * (power - (1 + growth_rate)))
    fvlum = (lumpsum * pow1)
    fv = fvsip + fvlum
    return fv


def new_expected_corpus(sip, lumpsum, debt_asset_allocation, equity_asset_allocation, actual_term, term, growth_rate=0.0,
                        monthly_expected_debt=pow(1.08, 1/12)-1, monthly_expected_equity=pow(1.12, 1/12)-1):
    """
    :param type
    :param sip:
    :param lumpsum:
    :param debt_asset_allocation:
    :param equity_asset_allocation:
    :param term:
    :param growth_rate:
    :param monthly_expected_debt:
    :param monthly_expected_equity:
    :return:
    """
    starting_amount_debt, starting_amount_equity, total_end_of_month, monthly_sip = 0, 0, 0, sip
    sip_paying_term = actual_term
    year_count = 1
    month_count = 1
    while year_count < term + 1:
        additional_amount_debt = (lumpsum + monthly_sip) * debt_asset_allocation
        additional_amount_equity = (lumpsum + monthly_sip) * equity_asset_allocation
        gain_in_month_debt = (starting_amount_debt + additional_amount_debt) * monthly_expected_debt
        gain_in_month_equity = (starting_amount_equity + additional_amount_equity) * monthly_expected_equity
        starting_amount_debt = starting_amount_debt + additional_amount_debt + gain_in_month_debt
        starting_amount_equity = starting_amount_equity + additional_amount_equity + gain_in_month_equity
        total_end_of_month = starting_amount_debt + starting_amount_equity
        lumpsum = 0
        if month_count % 12 == 0:
            year_count += 1
        month_count += 1
        if year_count < sip_paying_term + 1:
            monthly_sip = sip * pow((1 + growth_rate), year_count - 1)
        else:
            monthly_sip = 0
    return round(total_end_of_month)


def get_portfolio_overview(portfolio_items):
    """
    utility to return portfolio overview cart items for dashboard
    :param portfolio_items: the funds in which user has invested
    :return:
    """
    asset_overview, portfolio_item_map, default_indices_id = [], {'equity': [], 'debt': [], 'elss': []}, []
    invested_value, total_return_value, total_one_day_return, total_previous_day_port_value = 0, 0, 0, 0
    latest_date = get_dashboard_change_date()

    for portfolio_item in portfolio_items:
        portfolio_item_map[constants.FUND_MAP_REVERSE[portfolio_item.fund.type_of_fund]].append(portfolio_item)

    for category in constants.FUND_CATEGORY_LIST:
        category_portfolio_items = portfolio_item_map.get(category)
        category_return_value, category_sum_invested, category_holding_percentage = 0, 0, 0
        if category_portfolio_items:
            for category_portfolio_item in category_portfolio_items:
                category_portfolio_item.set_values(latest_date)
                category_return_value += category_portfolio_item.returns_value
                category_sum_invested += category_portfolio_item.sum_invested
                total_one_day_return += category_portfolio_item.one_day_return
                total_previous_day_port_value += category_portfolio_item.one_day_previous_portfolio_value
                category_holding_percentage = getattr(category_portfolio_item.portfolio, category + '_percentage')
            total_return_value += category_return_value
            invested_value += category_sum_invested
            gain_percentage = generate_xirr(category_return_value / category_sum_invested,
                                            (latest_date - category_portfolio_items[0].portfolio.modified_at.date()).days)
            category_overview = {constants.NAME: category, constants.INVESTED: category_sum_invested,
                                 constants.GAIN: round(category_return_value, 2),
                                 constants.GAIN_PERCENTAGE: round(gain_percentage * 100),
                                 constants.IS_GAIN: True if category_return_value >= 0 else False,
                                 constants.HOLDING_PERCENTAGE: round(category_holding_percentage, 1),
                                 constants.CURRENT_VALUE: round(category_return_value + category_sum_invested)}
            asset_overview.append(category_overview)
    default_index_one = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[0])
    default_index_two = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[1])
    index_one_return, index_one_return_percentage, index_one_latest_nav = get_index_one_day_return(default_index_one,
                                                                                                   latest_date)
    index_two_return, index_two_return_percentage, index_two_latest_nav = get_index_one_day_return(default_index_two,
                                                                                                   latest_date)
    if portfolio_items[0].portfolio.modified_at.date() >= get_dashboard_change_date():
        total_one_day_return = 0
    yesterday_changes = [{constants.NAME: constants.YOUR_PORTFOLIO, constants.GAIN: round(total_one_day_return),
                          constants.IS_GAIN: True if total_one_day_return >= 0 else False,
                          constants.CURRENT_VALUE: round(total_return_value + invested_value),
                          constants.GAIN_PERCENTAGE: round(total_one_day_return * 100 / total_previous_day_port_value, 1)},
                         {constants.NAME: constants.BSE_SENSEX, constants.GAIN: round(index_two_return, 2),
                          constants.IS_GAIN: True if index_two_return >= 0 else False,
                          constants.GAIN_PERCENTAGE: round(index_two_return_percentage, 2),
                          constants.CURRENT_VALUE: round(index_two_latest_nav, 2)},
                         {constants.NAME: constants.NSE_CNX_Nifty, constants.GAIN: round(index_one_return, 2),
                          constants.IS_GAIN: True if index_one_return >= 0 else False,
                          constants.GAIN_PERCENTAGE: round(index_one_return_percentage, 2),
                          constants.CURRENT_VALUE: round(index_one_latest_nav, 2)}]
    gain_percentage = generate_xirr((total_return_value / invested_value),
                                    (latest_date - portfolio_items[0].portfolio.modified_at.date()).days)

    portfolio_overview = {constants.PORTFOLIO_OVERVIEW:
                              {constants.INVESTED: invested_value,
                               constants.CURRENT_RETURNS: round(total_return_value),
                               constants.CURRENT_VALUE:
                                   {constants.VALUE: round(total_return_value + invested_value),
                                    constants.IS_GAIN: True if total_return_value >= 0 else False,
                                    constants.GAIN_PERCENTAGE: round(gain_percentage * 100, 1)}},
                          constants.ASSET_CLASS_OVERVIEW: asset_overview,
                          constants.YESTERDAY_CHANGE: yesterday_changes,
                          constants.DATE: get_dashboard_change_date(),
                          constants.IS_VIRTUAL: True,
                          constants.FINANCIAL_GOAL_STATUS: get_financial_goal_status_for_dashboard_virtual(
                              asset_overview, portfolio_items[0].portfolio)}
    return portfolio_overview


def get_financial_goal_status_for_dashboard_virtual(asset_overview, portfolio):
    """
    :param asset_overview: an array with category overview
    :param portfolio: the virtual portfolio of user
    """
    return calculate_financial_goal_status(asset_overview, [portfolio])

def get_index_one_day_return(index, latest_index_date):
    """
    :param index: index object
    :param latest_index_date: teh date on which index nav is to be considered
    :return: one day return and one day return percentage of the index
    """
    date_list = []
    for i in range(4):
        date_list.append(latest_index_date-timedelta(days=i))
    list = models.HistoricalIndexData.objects.filter(index=index, date__in=date_list).order_by('-date')
    nav_list = []
    for i in list:
        if i.date.isoweekday()<6:
            nav_list.append(i)
    one_day_return = nav_list[0].nav - nav_list[1].nav
    one_day_return_percentage = one_day_return * 100 / nav_list[1].nav
    return one_day_return, one_day_return_percentage, nav_list[0].nav


def get_leader_portfolio_funds(portfolio_items, total_sum_invested):
    """
    :param portfolio_items: the funds in a user portfolio
    :param total_sum_invested: total sum invested by bove user in all funds
    :return:
    """
    funds_into_category = {constants.EQUITY: [], constants.DEBT: [], constants.ELSS: []}
    for item in portfolio_items:
        if item.fund.type_of_fund == constants.FUND_MAP[constants.EQUITY]:
            funds_into_category = _append_to_dict(constants.EQUITY, item, funds_into_category, total_sum_invested)
        elif item.fund.type_of_fund == constants.FUND_MAP[constants.DEBT]:
            funds_into_category = _append_to_dict(constants.DEBT, item, funds_into_category, total_sum_invested)
        else:
            funds_into_category = _append_to_dict(constants.ELSS, item, funds_into_category, total_sum_invested)
    return funds_into_category


def _append_to_dict(type, portfolio_item, funds_into_category, total_sum_invested):
    """
    appends a portfolio item to funds into category according to type
    :param type: either of equity/elss/debt (type of fund)
    :param portfolio_item: the portfolio item that has to be appended
    :param funds_into_category: the dictionary into which we need to append
    :param total_sum_invested: the total sum invested into portfolio
    :return:
    """
    return funds_into_category[type].append({constants.FUND_NAME: portfolio_item.fund.fund_name,
                                             constants.ALLOCATION: portfolio_item.sum_invesed / total_sum_invested,
                                             constants.ONE_YEAR_RETURN: portfolio_item.fund.get_one_year_return(),
                                             constants.ID: portfolio_item.fund.id})


def get_average_holding(fund):
    """
    For a particular fund return the average holding percentage.

    :param fund: The fund for which the average_holding percentage must be calculated.
    :return: The average holding percentage for that fund.
    """
    percent_array = []
    users = [i.user for i in models.OrderDetail.objects.filter(order_status=2).distinct("user")]
    for user in users:
        order_amount_particular_fund = 0
        order_amount_all_funds = 0
        redeem_amount_particular_fund = 0
        redeem_amount_all_funds = 0
        for i in models.FundOrderItem.objects.filter(portfolio_item__portfolio__user=user, is_verified=True,
                                                     is_cancelled=False):
            if i.portfolio_item.fund.fund_id == fund.fund_id:
                order_amount_particular_fund += i.order_amount
            order_amount_all_funds += i.order_amount
        for i in models.FundRedeemItem.objects.filter(portfolio_item__portfolio__user=user, is_verified=True,
                                                      is_cancelled=False):
            if i.portfolio_item.fund.fund_id == fund.fund_id:
                redeem_amount_particular_fund += i.redeem_amount
            redeem_amount_all_funds += i.redeem_amount

        # business logic
        numerator = order_amount_particular_fund - redeem_amount_particular_fund
        denominator = order_amount_all_funds - redeem_amount_all_funds
        print(user, numerator, denominator)
        if denominator and numerator != 0:
            average_for_user = numerator/denominator
            percent_array.append(average_for_user)
    if len(percent_array) == 0:
        return 0.0
    else:
        return sum(percent_array)*100/float(len(percent_array))


def get_most_popular_funds(type, limit=10):
    """
    :param: limit is the top n
    :param: type is the type of the fund to be extracted
    :returns: the top n funds of that type sorted by popularity

    """
    most_popular_funds = []
    total_count = models.OrderDetail.objects.filter(order_status=2).distinct("user").count()
    ordered_funds = {}
    for i in models.Fund.objects.filter(type_of_fund=type):
        average_holding = get_average_holding(i)
        counts = models.FundOrderItem.objects.filter(
            is_verified=True, portfolio_item__fund_id=i.id, is_cancelled=False).distinct("portfolio_item__portfolio__user").count()
        ordered_funds[i.id] = {}
        ordered_funds[i.id]['three_year_fund'] = round(i.get_three_year_return(), 1)
        ordered_funds[i.id]['fund_name'] = i.fund_name
        ordered_funds[i.id]['average_holding'] = round(average_holding, 1) if average_holding else 0.0
        ordered_funds[i.id]['popularity'] = round((counts*100)/total_count, 1)
        ordered_funds[i.id]['type'] = i.type_of_fund
        ordered_funds[i.id]['id'] = i.id

    ordered_funds = OrderedDict(sorted(ordered_funds.items(), key=lambda t: t[1]['popularity'], reverse=True))

    for fund in ordered_funds.values():
        most_popular_funds.append(fund)

    return most_popular_funds[:limit]


def get_portfolio_historic_data(funds_historic_data_list, portfolio_items, for_portfolio_tracker=False):
    """
    :param funds_historic_data_list:a dictionary having historic performance of all funds in portfolio
    :param portfolio_items: a list of portfolio items
    :param for_portfolio_tracker: a boolean to signify if data is needed for portfolio historic performance
    :return: historic performance of portfolio calculated from portfolio items
    """
    fund_investment_map, portfolio_historic_data, funds_relative_nav_list = {}, [], []
    for portfolio_item in portfolio_items:
        fund_investment_map[portfolio_item.fund.fund_name] = portfolio_item.sum_invested
    for fund in funds_historic_data_list.get(constants.FUND):
        fund_name = fund.get(constants.ID)
        fund_nav_list = fund.get(constants.VALUE)
        fund_nav_relative_list = [nav * fund_investment_map.get(fund_name) / fund_nav_list[0] for nav in fund_nav_list]
        funds_relative_nav_list.append(fund_nav_relative_list)
    for index in range(len(funds_relative_nav_list[0])):
        portfolio_date_performance = 0
        for fund in funds_relative_nav_list:
            portfolio_date_performance += fund[index]
        portfolio_historic_data.append(portfolio_date_performance)
    if for_portfolio_tracker:
        return portfolio_historic_data, funds_historic_data_list.get(constants.DATES)
    portfolio_historic_data, index_historic = normalize_portfolio_data(
        portfolio_historic_data, funds_historic_data_list[constants.INDEX])
    return {constants.DATES: funds_historic_data_list.get(constants.DATES),
            constants.FUND: [{constants.ID: constants.PORTFOLIO, constants.VALUE: portfolio_historic_data}],
            constants.INDEX: index_historic,
            constants.CATEGORY: constants.EMPTY_lIST_FOR_DATA}


def normalize_portfolio_data(portfolio_historic_data, index_historic_data):
    """
    :param portfolio_historic_data:
    :param index_historic_data:
    :return:
    """
    length = len(index_historic_data)
    normalized_historic_data, normalized_index_data = [], []
    normalization_value = 100.0 / portfolio_historic_data[0]
    normalization_value_index = 100.0 / index_historic_data[0]
    for index in range(length):
        normalized_historic_data.append(round(portfolio_historic_data[index] * normalization_value, 2))
        normalized_index_data.append(round(index_historic_data[index] * normalization_value_index, 2))
    return normalized_historic_data, normalized_index_data


def get_billdesk_checksum(string, secret_key):
    """

    :param string: String to be hashed
    :param secret_key: A secret used for hashing
    :return: hashed string
    """
    bytes_string = string.encode('utf-8')
    bytes_secret_key = secret_key.encode('utf-8')
    sign = hmac.new(bytes_secret_key, bytes_string, digestmod=hashlib.sha256).hexdigest()
    return sign.upper()


def get_portfolio_details(portfolio_items, for_leader_board=False):
    """
    :param portfolio_items: the funds in a user portfolio
    :param for_leader_board: flag to check if api will return data for leader board
    :return:
    """
    portfolio_current_value, sum_invested = 0, 0
    portfolio_id, equity_id, debt_id, elss_id = [], [], [], []
    fund_map = [{constants.KEY: constants.EQUITY, constants.VALUE: []},
                {constants.KEY: constants.DEBT, constants.VALUE: []},
                {constants.KEY: constants.ELSS, constants.VALUE: []}]

    latest_date = get_dashboard_change_date()
    for portfolio_item in portfolio_items:
        portfolio_item.set_values(latest_date)
        portfolio_current_value += portfolio_item.sip + portfolio_item.lumpsum + portfolio_item.returns_value
        sum_invested += portfolio_item.sip + portfolio_item.lumpsum

    for portfolio_item in portfolio_items:
        if portfolio_item.portfolio.id not in portfolio_id:
            portfolio_id.append(portfolio_item.portfolio.id)
        if portfolio_item.broad_category_group == constants.FUND_MAP[constants.EQUITY]:
            if portfolio_item.fund.id in equity_id:
                fund_map = similar_fund_data_for_portfolio_details(fund_map, 0, portfolio_item, portfolio_current_value) # 0 refers to position of equity fund in dictionary
            else:
                fund_map[0].get(constants.VALUE).append(fund_data_for_portfolio_details(
                    portfolio_item, portfolio_current_value))
                equity_id.append(portfolio_item.fund.id)
        elif portfolio_item.broad_category_group == constants.FUND_MAP[constants.DEBT]:
            if portfolio_item.fund.id in debt_id:
                fund_map = similar_fund_data_for_portfolio_details(fund_map, 1, portfolio_item, portfolio_current_value) # 1 refers to position of debt fund in dictionary
            else:
                fund_map[1].get(constants.VALUE).append(fund_data_for_portfolio_details(
                    portfolio_item, portfolio_current_value))
                debt_id.append(portfolio_item.fund.id)
        else:
            if portfolio_item.fund.id in elss_id:
                fund_map = similar_fund_data_for_portfolio_details(fund_map, 2, portfolio_item, portfolio_current_value) # 2 refers to position of elss fund in dictionary
            else:
                fund_map[2].get(constants.VALUE).append(fund_data_for_portfolio_details(
                    portfolio_item, portfolio_current_value))
                elss_id.append(portfolio_item.fund.id)
    current_gain = generate_xirr(
        (portfolio_current_value - sum_invested) / sum_invested,
        (get_latest_date() - portfolio_items[0].portfolio.modified_at.date()).days)
    current_portfolio = {constants.CORPUS: round(portfolio_current_value),
                         constants.GAIN: round(current_gain * 100),
                         constants.IS_GAIN: True if current_gain >= 0 else False}
    if for_leader_board is True:
        current_portfolio = {constants.GAIN: current_gain, constants.IS_GAIN: True if current_gain >= 0 else False}
    return {constants.ASSET_CLASS_OVERVIEW: fund_map, constants.CURRENT_PORTFOLIO: current_portfolio}


def get_portfolio_details_new(amount_invested_fund_map, is_today_portfolio):
    """
    Utility to return json response as required by using calculations of make_xirr_calculations
    :param amount_invested_fund_map:a dict with key as fund and value as list of transactions for that
     fund(invest+redeem)
    :return:
    """
    fund_map_based_on_type, portfolio_total_value, portfolio_gain_percentage = make_xirr_calculations_for_dashboard(
        amount_invested_fund_map, constants.PORTFOLIO_DETAILS, is_today_portfolio)
    for index in range(len(fund_map_based_on_type)):
        for fund_dict in fund_map_based_on_type[index].get(constants.VALUE):
            try:
                fund_percentage = fund_dict.get(constants.CURRENT_VALUE) * 100 / portfolio_total_value
            except ZeroDivisionError:
                fund_percentage = 0
            fund_dict.update({constants.FUND_PERCENTAGE: fund_percentage})

    current_portfolio = {constants.CORPUS: portfolio_total_value,
                         constants.GAIN: portfolio_gain_percentage,
                         constants.IS_GAIN: True if portfolio_gain_percentage >= 0 else False}
    return {constants.ASSET_CLASS_OVERVIEW: fund_map_based_on_type, constants.CURRENT_PORTFOLIO: current_portfolio}


def calculate_financial_goal_status(asset_class_overview, portfolios_to_be_considered):
    """
    utility to calculate financial goal status of all goals of a user
    :param asset_class_overview:a dict containing key as category(equity, elss, debt) and values as gain percentage and
     gain
    :param user_id:the id of user whose dashboard is being calculated
    :param portfolios_to_be_considered: user portfolios to be considered
    :return:
    """
    from core import goals_helper
    
    total_debt, total_equity, total_elss = 0, 0, 0
    goal_map = {
        constants.RETIREMENT: [[], 0], constants.TAX_SAVING: [[], 0], constants.BUY_PROPERTY: [[], 0],
        constants.EDUCATION: [[], 0], constants.WEDDING: [[], 0], constants.OTHER_EVENT: [[], 0],
        constants.INVEST: [[], 0]
    }

    for portfolio in portfolios_to_be_considered:
        if portfolio.has_invested == False:
            goals = goals_helper.GoalBase.get_current_goals(portfolio.user)
            investment_date = portfolio.modified_at.date()
        else:
            goals = goals_helper.GoalBase.get_portfolio_goals(portfolio.user, portfolio)
            investment_date = portfolio.investment_date
        
        for goal in goals:
            corpus, investment_till_date, term, debt_investment, equity_investment, elss_investment = \
                calculate_corpus_and_investment_till_date(goal, investment_date)
            goal_data = generate_goals_data(goal)
        
            goal_map[goal.category][0].append({
                constants.EXPECTD_VALUE: corpus,
                constants.EQUITY: equity_investment, constants.DEBT: debt_investment,
                constants.ELSS: elss_investment,
                constants.DATE: portfolio.modified_at.date() + relativedelta(years=int(term)),
                constants.GOAL_ANSWERS: goal_data
            })
            total_debt += debt_investment
            total_equity += equity_investment
            total_elss += elss_investment
     
    return make_financial_goal_response(goal_map, total_equity, total_debt, total_elss, asset_class_overview)   


def make_financial_goal_response(goal_map, total_equity_invested, total_debt_invested, total_elss_invested,
                                 asset_class_overview):
    """
    utility to make financial goal response as required by dashboard

    :param goal_map:a goal map containing goals and their respective values
    :param total_equity_invested:total investment in equity
    :param total_debt_invested:total investment in debt
    :param total_elss_invested:total investment in elss
    :param asset_class_overview:a dict containing key as category(equity, elss, debt) and values as gain percentage and
     gain
    :return:
    """
    current_value_map = {constants.EQUITY: 0, constants.DEBT: 0, constants.ELSS: 0}
    for category in asset_class_overview:
        current_value_map[category[constants.NAME]] = category[constants.INVESTED] + category[constants.GAIN]
    financial_goal_list = []
    for category in goal_map:
        if goal_map[category][0]:
            for category_individual_goal in goal_map[category][0]:
                goal_current_value = 0
                if total_equity_invested:
                    goal_current_value += category_individual_goal.get(constants.EQUITY) * (
                        current_value_map[constants.EQUITY] / total_equity_invested)
                if total_debt_invested:
                    goal_current_value += category_individual_goal.get(constants.DEBT) * (
                        current_value_map[constants.DEBT] / total_debt_invested)
                if total_elss_invested:
                    goal_current_value += category_individual_goal.get(constants.ELSS) * (
                        current_value_map[constants.ELSS] / total_elss_invested)
                progress = round(goal_current_value * 100 / category_individual_goal.get(constants.EXPECTD_VALUE), 1)
                
                goal_status = {
                    constants.NAME: str(constants.ASSET_ALLOCATION_MAP[category][2]) +
                                    str(goal_map[category][1] + 1),
                    constants.EXPECTD_VALUE: calculate_aum_in_string(round(goal_current_value)),
                    constants.DATE: category_individual_goal.get(constants.DATE),
                    constants.GOAL: calculate_aum_in_string(round(category_individual_goal.get(
                        constants.EXPECTD_VALUE))), constants.PROGRESS: progress,
                    constants.GOAL_ANSWERS: category_individual_goal.get(constants.GOAL_ANSWERS)
                }
                financial_goal_list.append(goal_status)
                goal_map[category][1] += 1
    return financial_goal_list


def calculate_corpus_and_investment_till_date(goal, investment_date):
    """
    calculates corpus target and investment till date for ech goal

    :param answer_map: the answer map of a user
    :param portfolio: a portfolio of user
    :param category:the goal category
    :param category_allocation:asset allocation for the goal
    :return:
    """
    from core import goals_helper
    
    investment_till_date, invest_date = 0, 0, investment_date
    term = 0

    category_allocation = goal.asset_allocation
    
    goal_object = goals_helper.GoalBase.get_goal_instance(goal)
    if goal.category == constants.TAX_SAVING:
        term = constants.TAX_DEFAULT_TERM
    else:
        term = goal_object.get_duration()
        
    actual_term = term
    if goal.category == constants.INVEST and term == 0:
        term = constants.INVEST_MINIMUM_TERM
    
    corpus = goal_object.get_expected_corpus(actual_term, term)
    
    if investment_date is not None:
        time_since_invest = relativedelta(date.today(), invest_date).months
        invest_date += relativedelta(months=time_since_invest)
        time_since_invest += relativedelta(date.today(), invest_date).years * 12
        investment_till_date = goal_object.get_expected_corpus(time_since_invest, time_since_invest)

    return corpus, investment_till_date, term, investment_till_date * float(category_allocation[constants.DEBT]) / 100, \
           investment_till_date * float(category_allocation[constants.EQUITY]) / 100,\
           investment_till_date * float(category_allocation[constants.ELSS]) / 100


def make_xirr_calculations_for_dashboard(amount_invested_fund_map, api_type, is_today_portfolio=False):
    """
    make calculations on basis of xirr at fund level, category of fund level and portfolio level
    :param amount_invested_fund_map:a dict with key as fund and value as list of transactions for that
     fund(invest+redeem)
    :param api_type: dashboard or portfolio detail
    :param is_today_portfolio: if the user portfolio is just made today(gains will be zero)
    :return:
    """
    array_for_portfolio_gain_calculation, portfolio_total_value, portfolio_one_previous_day_value = [], 0, 0
    sum_invested_in_portfolio, portfolio_gain_percentage, date_for_portfolio = 0, 0, date.today()
    fund_map_based_on_type = [{constants.KEY: constants.EQUITY, constants.VALUE: []},
                              {constants.KEY: constants.DEBT, constants.VALUE: []},
                              {constants.KEY: constants.ELSS, constants.VALUE: []}]
    # in the list first element is an array for gain calculation, second is sum invested in that category, third is
    # current value of that category, and last is gain percentage for that category
    array_for_category_gain_calculation = {constants.FUND_MAP[constants.EQUITY]: [[], 0, 0, 0],
                                           constants.FUND_MAP[constants.DEBT]: [[], 0, 0, 0],
                                           constants.FUND_MAP[constants.ELSS]: [[], 0, 0, 0]}

    # loop through all transactions of a user clubbed according to fund id and calculate fund gain for each fund
    # on basis of all fund gains and type calculate equity/debt/elss and portfolio gain
    for fund in amount_invested_fund_map:
        latest_fund_data, fund_one_previous_nav = calculate_latest_and_one_previous_nav(fund)
        if latest_fund_data.day_end_date < date_for_portfolio:
            date_for_portfolio = latest_fund_data.day_end_date
        # utility to make an array required for xirr calculation for a single fund
        array_for_gain_cal, number_of_units, sum_invested_in_fund = make_array_for_gain_calculation(
            amount_invested_fund_map[fund])
        sum_invested_in_portfolio += sum_invested_in_fund
        array_for_portfolio_gain_calculation += array_for_gain_cal
        fund_current_value = latest_fund_data.day_end_nav * number_of_units
        portfolio_total_value += fund_current_value
        portfolio_one_previous_day_value += fund_one_previous_nav * number_of_units

        # based on type of fund(equity, elss and debt) append the respective array for gain calculation
        array_for_category_gain_calculation, fund_gain = append_category_cal_arrays(
            array_for_category_gain_calculation, fund, array_for_gain_cal, fund_current_value, sum_invested_in_fund)
        for category in fund_map_based_on_type:
            if category.get(constants.KEY) == constants.FUND_MAP_REVERSE[fund.type_of_fund]:
                category.get(constants.VALUE).append(make_fund_dict_for_portfolio_detail(
                    fund.fund_name, fund_current_value, fund_gain, sum_invested_in_fund, fund.id))

    # calculating gain percentage for categories and the portfolio
    for category in array_for_category_gain_calculation:
        if not is_today_portfolio and array_for_category_gain_calculation.get(category)[0]:
            array_for_category_gain_calculation.get(category)[0].append(
                (get_dashboard_change_date(), -array_for_category_gain_calculation.get(category)[2]))
            try:
                category_gain = xirr.xirr(array_for_category_gain_calculation.get(category)[0])
            except Exception as e:
                print("XIRR failed for following input")
                print(array_for_category_gain_calculation.get(category)[0])
                category_gain = 0.0
            category_gain = 0 if type(category_gain) is complex or category_gain == float('inf') else category_gain
            array_for_category_gain_calculation.get(category)[3] = round(category_gain * 100)
        else:
            array_for_category_gain_calculation.get(category)[3] = 0
    if not is_today_portfolio and array_for_portfolio_gain_calculation:
        array_for_portfolio_gain_calculation.append((get_dashboard_change_date(), -portfolio_total_value))
        try:
            portfolio_gain = xirr.xirr(array_for_portfolio_gain_calculation)
        except Exception as e:
            print("XIRR failed for following input")
            print(array_for_portfolio_gain_calculation)
            portfolio_gain = 0.0
        portfolio_gain = 0 if type(portfolio_gain) is complex else portfolio_gain
        portfolio_gain_percentage = round(portfolio_gain * 100, 1)
        if api_type == constants.SET_XIRR:
            return portfolio_gain_percentage

    # return based on api_type
    if api_type == constants.PORTFOLIO_DETAILS:
        return fund_map_based_on_type, portfolio_total_value, portfolio_gain_percentage
    elif api_type == constants.DASHBOARD:
        return make_asset_class_overview(array_for_category_gain_calculation, portfolio_total_value), \
               make_portfolio_overview(sum_invested_in_portfolio, portfolio_total_value, portfolio_gain_percentage), \
               make_yesterday_change_dashboard(portfolio_one_previous_day_value, portfolio_total_value), \
               date_for_portfolio


def make_yesterday_change_dashboard(portfolio_one_previous_day_value, portfolio_total_value, today_portfolio=False,
                                    latest_index_date=None, is_transient_dashboard=False):
    """
    utility to make dict for yesterday change card of dashboard
    :param portfolio_one_previous_day_value: portfolio one day previous value
    :param portfolio_total_value: portfolio current value
    :param today_portfolio: a boolean to signify is any fund order item exists with allotment date before today
    :param latest_index_date: teh latest date of index
    :param is_transient_dashboard: a boolean to specify if dashboard is transient
    :return:
    """
    portfolio_one_day_gain = 0 if today_portfolio else portfolio_total_value - portfolio_one_previous_day_value
    portfolio_one_day_gain = 0 if is_transient_dashboard else portfolio_one_day_gain

    if portfolio_one_previous_day_value == 0:
        portfolio_one_day_gain_percentage = 0
    else:
        portfolio_one_day_gain_percentage = 0 if today_portfolio else round(
            portfolio_one_day_gain * 100 / portfolio_one_previous_day_value, 1)

    default_index_one = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[0])
    default_index_two = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[1])
    index_one_return, index_one_return_percentage, index_one_latest_nav = get_index_one_day_return(default_index_one,
                                                                                                   latest_index_date)
    index_two_return, index_two_return_percentage, index_two_latest_nav = get_index_one_day_return(default_index_two,
                                                                                                   latest_index_date)

    yesterday_changes = [
        {constants.NAME: constants.YOUR_PORTFOLIO, constants.GAIN: round(portfolio_one_day_gain),
         constants.IS_GAIN: True if portfolio_one_day_gain >= 0 else False,
         constants.GAIN_PERCENTAGE: round(portfolio_one_day_gain_percentage, 1),
         constants.CURRENT_VALUE: round(portfolio_total_value)},
        {constants.NAME: constants.BSE_SENSEX, constants.GAIN: round(index_two_return, 2),
         constants.IS_GAIN: True if index_two_return >= 0 else False,
         constants.GAIN_PERCENTAGE: round(index_two_return_percentage, 2),
         constants.CURRENT_VALUE: round(index_two_latest_nav, 2)},
        {constants.NAME: constants.NSE_CNX_Nifty, constants.GAIN: round(index_one_return, 2),
         constants.IS_GAIN: True if index_one_return >= 0 else False,
         constants.GAIN_PERCENTAGE: round(index_one_return_percentage, 2),
         constants.CURRENT_VALUE: round(index_one_latest_nav, 2)}
    ]
    return yesterday_changes


def calculate_latest_and_one_previous_nav(fund, latest_index_date=None):
    """
    utility to find latest fund data nd one previous nav for a fund
    :param fund: the fund whose latest and one previous nav is to be found
    :param latest_index_date: the minimum date of bse and nse
    :return:
    """
    latest_fund_data = models.FundDataPointsChangeDaily.objects.get(fund_id=fund)
    if latest_index_date is not None:
        if latest_fund_data.day_end_date > latest_index_date:
            latest_fund_data = models.HistoricalFundData.objects.get(fund_id=fund, date=latest_index_date)
            fund_latest_nav_date = latest_fund_data.date
        else:
            fund_latest_nav_date = latest_fund_data.day_end_date
    else:
        fund_latest_nav_date = latest_fund_data.day_end_date
    if fund_latest_nav_date.isoweekday() == 7:
        fund_one_previous_date = fund_latest_nav_date - timedelta(days=3)
    elif fund_latest_nav_date.isoweekday() == 6:
        fund_one_previous_date = fund_latest_nav_date - timedelta(days=2)
    else:
        fund_one_previous_date = fund_latest_nav_date - timedelta(days=1)
    one_previous_nav = models.HistoricalFundData.objects.get(fund_id=fund, date=fund_one_previous_date).nav
    return latest_fund_data, one_previous_nav


def make_portfolio_overview(invested_value, current_value, gain_percentage):
    """
    utility to make dictionary required by dashboard for portfolio overview

    :param invested_value: invested value in portfolio
    :param current_value: current day value for portfolio
    :param gain_percentage: gain percentage for portfolio
    :return: a dictionary for portfolio overview for dashboard
    """
    portfolio_overview = {
        constants.INVESTED: invested_value, constants.CURRENT_RETURNS: round(current_value - invested_value, 2),
        constants.CURRENT_VALUE: {
            constants.VALUE: round(current_value, 2),
            constants.GAIN_PERCENTAGE: round(gain_percentage),
            constants.IS_GAIN: True if gain_percentage >= 0 else False
        }
    }
    return portfolio_overview


def make_asset_class_overview(array_for_category_gain_calculation, portfolio_total_value):
    """
    utility to make asset_class_overview based on array_for_gain_calulation
    :param array_for_category_gain_calculation:an array containing data to make asset_class_overview
    :param portfolio_total_value: current total value of portfolio
    :return:
    """
    asset_class_overview = []
    for category in array_for_category_gain_calculation:
        sum_invested, current_value, gain_percentage = 0, 0, 0
        if array_for_category_gain_calculation.get(category)[0]:
            sum_invested = array_for_category_gain_calculation.get(category)[1]
            current_value = array_for_category_gain_calculation.get(category)[2]
            gain_percentage = round(array_for_category_gain_calculation.get(category)[3], 2)
        category_overview = {
            constants.NAME: constants.FUND_MAP_REVERSE.get(category),
            constants.HOLDING_PERCENTAGE: round(current_value * 100 / portfolio_total_value),
            constants.CURRENT_VALUE: round(current_value),
            constants.INVESTED: sum_invested,
            constants.GAIN: round(current_value - sum_invested),
            constants.GAIN_PERCENTAGE: gain_percentage,
            constants.IS_GAIN: True if gain_percentage >= 0 else False
        }
        asset_class_overview.append(category_overview)
    return asset_class_overview


def append_category_cal_arrays(array_for_category_gain_calculation, fund, array_for_gain_cal, fund_current_value,
                               sum_invested_in_fund):
    """
    utility to append fund gain array to category gain array and calculate fund gain
    :param array_for_category_gain_calculation:the array which need to be appended
    :param fund: the fund whose array_for_gain_cal is being appended
    :param array_for_gain_cal:the array which has to be appended to above array
    :param fund_current_value:the current day value of fund held bya  user
    :param sum_invested_in_fund: the sum invested in that fund
    :return:
    """
    array_for_category_gain_calculation.get(fund.type_of_fund)[0] += array_for_gain_cal
    array_for_gain_cal.append((get_dashboard_change_date(), -fund_current_value))
    try:
        fund_gain = xirr.xirr(array_for_gain_cal)
    except Exception as e:
        print("XIRR failed for following input")
        print(array_for_gain_cal)
        fund_gain = 0.0
    fund_gain = 0 if type(fund_gain) is complex else fund_gain
    array_for_category_gain_calculation.get(fund.type_of_fund)[1] += sum_invested_in_fund
    array_for_category_gain_calculation.get(fund.type_of_fund)[2] += fund_current_value
    return array_for_category_gain_calculation, fund_gain


def make_fund_dict_for_portfolio_detail(fund_name, fund_current_value, fund_gain, sum_invested_in_fund, fund_id):
    """
    utility to make a dict
    :param fund_name: the name of fund
    :param fund_current_value: the current value of fund
    :param fund_gain: the gain of fund on today
    :param sum_invested_in_fund: the sum(lumpsum+sip) paid by user till present in a fund
    :return:
    """
    try:
        fund_gain_rounded = round(fund_gain * 100, 1)
    except:
        fund_gain_rounded = 0
    return {constants.FUND_NAME: fund_name, constants.RETURN_PERCENTAGE: fund_gain_rounded,
            constants.IS_GAIN: True if float(round(fund_current_value - sum_invested_in_fund)) >= 0 else False,
            constants.CURRENT_VALUE: round(fund_current_value),
            constants.INVESTED_VALUE: round(sum_invested_in_fund),
            constants.GAIN: round(fund_current_value - sum_invested_in_fund),
            constants.ID: fund_id}


def make_array_for_gain_calculation(fund_transactions):
    """
    utility to make an array for calculation of gain for a fund
    :param fund_transactions: the transactions related to a fund
    :return:
    """
    array_for_gain_cal, number_of_units_of_funds, sum_invested_in_fund = [], 0, 0

    for transct in fund_transactions:
        if isinstance(transct, models.FundOrderItem):
            sum_invested_in_fund += transct.order_amount
            if transct.is_verified:
                array_for_gain_cal.append((transct.allotment_date, transct.order_amount))
                number_of_units_of_funds += transct.unit_alloted
        elif isinstance(transct, models.FundRedeemItem):
            if transct.is_verified:
                array_for_gain_cal.append((transct.redeem_date, -transct.redeem_amount))
                number_of_units_of_funds -= transct.unit_redeemed
            sum_invested_in_fund -= transct.redeem_amount

    return array_for_gain_cal, number_of_units_of_funds, sum_invested_in_fund


def similar_fund_data_for_portfolio_details(fund_map, map_index, portfolio_item, portfolio_current_value):
    """
    :param fund_map: fund data
    :param map_index: index of fund data, 0 refers to position of equity fund, 1 refers to position of debt, 2 refers to position of elss fund in dictionary.
    :param portfolio_item: the fund whose dict is to be made
    :param portfolio_current_value: total current value of portfolio
    :return: updated fund data
    """
    index = next(index for (index, d) in enumerate(fund_map[map_index][constants.VALUE])
                 if d[constants.FUND_NAME] == portfolio_item.fund.fund_name)
    return_value = portfolio_item.returns_value + portfolio_item.sum_invested
    portfolio_item_current_value = fund_map[map_index][constants.VALUE][index][constants.CURRENT_VALUE] + return_value
    fund_percentage = round(portfolio_item_current_value * 100 / portfolio_current_value)
    fund_map[map_index][constants.VALUE][index][constants.CURRENT_VALUE] += return_value
    fund_map[map_index][constants.VALUE][index][constants.FUND_PERCENTAGE] = fund_percentage
    return fund_map


def fund_data_for_portfolio_details(portfolio_item, portfolio_current_value):
    """
    makes a dict of fund parameters required for portfolio details
    :param portfolio_item: the fund whose dict is to be made
    :param portfolio_current_value: total current value of portfolio
    :return: a dict of format as required for portfolio detail
    """
    latest_date = get_dashboard_change_date()
    portfolio_item.set_values(latest_date)
    sum_invested = portfolio_item.sip + portfolio_item.lumpsum
    portfolio_item_current_value = portfolio_item.returns_value + sum_invested
    fund_percentage = round(portfolio_item_current_value * 100 / portfolio_current_value, 1)
    return_percentage = round(portfolio_item.returns_percentage * 100, 1)
    portfolio_detail_dict = {constants.FUND_NAME: portfolio_item.fund.fund_name,
                             constants.CURRENT_VALUE: round(portfolio_item_current_value),
                             constants.RETURN_PERCENTAGE: return_percentage,
                             constants.IS_GAIN: True if return_percentage >= 0 else False,
                             constants.FUND_PERCENTAGE: fund_percentage,
                             constants.GAIN: round(portfolio_item_current_value - sum_invested),
                             constants.INVESTED_VALUE: sum_invested,
                             constants.ID: portfolio_item.fund.id}
    return portfolio_detail_dict


def set_xirr_values_for_users_having_investment():
    """
    calculates and stores xirr for all users who have had invested(atleast one fund order item)
    :return:
    """
    investment_map, count = {}, 0
    redeem_map = {}

    # all investments and redeems
    investments = list(models.FundOrderItem.objects.exclude(is_verified=False))
    redeems = list(models.FundRedeemItem.objects.exclude(is_verified=False))

    # make a map with id as user and value as list of investments and reems from that user
    if investments+redeems:
        for transct in investments:
            try:
                investment_map[transct.portfolio_item.portfolio.user].append(transct)
            except KeyError:
                investment_map.update({transct.portfolio_item.portfolio.user: [transct]})
        for transct in redeems:
            try:
                redeem_map[transct.portfolio_item.portfolio.user].append(transct)
            except KeyError:
                redeem_map.update({transct.portfolio_item.portfolio.user: [transct]})

        for user in investment_map:
            # print(user)
            user_xirr = 0
            try:
                redeem = redeem_map[user]
            except KeyError:
                redeem = []
            array_for_gain_calculation, is_today_port, portfolios = club_investment_redeem_together(
                investment_map[user], redeem)
            if not is_today_port:
                user_xirr = make_xirr_calculations_for_dashboard(array_for_gain_calculation, constants.SET_XIRR)
                # print(user_xirr)
            profile_models.AggregatePortfolio.objects.update_or_create(
                user=user, defaults={'total_xirr': user_xirr, 'update_date': date.today()})
            count += 1
    return count


def set_xirr_values_for_users_not_having_investment():
    """
    :return: calculates and stores xirr for all users who have not invested
    """
    count = 0
    non_invested_users = []
    for user in profile_models.User.objects.all():
        if models.Portfolio.objects.filter(user=user, has_invested=False):
            non_invested_users.append(user)

    for non_invested_user in non_invested_users:
        count += 1
        portfolio_items = models.PortfolioItem.objects.filter(
            portfolio__user=non_invested_user, portfolio__has_invested=False, portfolio__is_deleted=False).select_related(
            'portfolio','fund')
        portfolio_overview = get_portfolio_overview(portfolio_items)
        total_xirr = get_xirr_value_from_dashboard_response(portfolio_overview)
        profile_models.AggregatePortfolio.objects.update_or_create(
            user=non_invested_user ,defaults={'total_xirr': round(total_xirr, 1), 'update_date': datetime.now()})
    return count


def get_finaskus_id(user):
    """
    Generates the user finaskus id based on these lines

    1. The default format will be BSE0XXXXXX - which is first three alphabets fixed as BSE, next digit '0' and next 6 digits as last six digits of user's phone number as per the investor form (which may or may not be the same as the user login phone number)
    2. The significant of first 3 digits is that we will use this for BSE Unique Client Code, whereas in future if we have the same user registered with other agencies then we can keep the last 7 digits same and only change the first 3 digits.
    3. The 4th digit by default is to be set as zero, but it can be '1' or '2' if the last 6 digits happen to be the same for another user (which is a rare possibility, but cannot be ruled out completely).
    :param user:
    :return: the generated finaskus investor id.
    """
    result_id = constants.FINASKUS_ID_PREFIX
    contact = profile_models.ContactInfo.objects.get(user=user)
    last_six_digits = contact.phone_number[-6:]  # this makes sure no matter the length of contact phone
    # number the last 6 digits are extracted

    users_count = profile_models.User.objects.filter(finaskus_id__contains=last_six_digits).count()
    # this makes sure to check if the id is not incremented unnecessarily on new image saves.
    # if existing id has len 10 then use existing id itself.
    if user.finaskus_id:
        if len(user.finaskus_id) == 10:
            result_id = user.finaskus_id
    else:
        # new id is assigned
        if users_count != 0:
            # some other user has similar last six digits in phone number
            result_id = result_id[:-1]
            result_id += str(users_count) + last_six_digits
        else:
            # no other user has similar last six digits in phone number
            result_id += last_six_digits
    return result_id

def send_transaction_complete_email(txn, user, portfolio, order_detail_lumpsum,order_detail_sip, inlinePayment):
    sip_tenure = 0
    goal_len = 0
    if order_detail_sip is not None:
        sip_tenure,goal_len = user.get_sip_tenure(portfolio) 
       
    applicant_name = investor_info_check(user)

    payment_completed = True if txn.txn_status == payment_models.Transaction.Status.Success else False
    profiles_helpers.send_transaction_completed_email(order_detail_lumpsum,order_detail_sip,applicant_name,user.email,sip_tenure,goal_len,payment_completed, inlinePayment, use_https=settings.USE_HTTPS)

def convert_to_investor(txn, exchange_vendor, inlinePayment=False):
    """
    :param txn: a transaction object
    Run only after investment is successful
    :return:
    """
    #TODO intil amount fixing
    user = txn.user
    portfolio = models.Portfolio.objects.get(user=user, has_invested=False)
    order_detail_lumpsum, order_detail_sip = save_portfolio_snapshot(txn, exchange_vendor)
    
    portfolio.has_invested = True
    portfolio.investment_date = date.today()
    portfolio.save()
    
    portfolio.portfolioitem_set.all().update(investment_date = date.today())

    profile_models.AggregatePortfolio.objects.update_or_create(
        user=txn.user, defaults={"update_date":datetime.now().date()})
    
    send_email_thread = threading.Thread(target=send_transaction_complete_email, args=(txn, user, portfolio, order_detail_lumpsum,order_detail_sip,inlinePayment,))
    send_email_thread.start()


def save_portfolio_snapshot(txn, exchange_vendor):
    """
    utility to save a snapshot of portfolio at the time of investment
    :param txn: the transaction object
    :return:
    """
    portfolio_items = models.PortfolioItem.objects.filter(portfolio__user=txn.user, portfolio__has_invested=False)
    order_item_list_sip, order_item_list_lumpsum = [], []
    for portfolio_item in portfolio_items:
        order_item_lump = models.FundOrderItem.objects.create(portfolio_item=portfolio_item,
                                                              order_amount=portfolio_item.lumpsum,
                                                              agreed_sip=portfolio_item.sip,
                                                              agreed_lumpsum=portfolio_item.lumpsum,
                                                              internal_ref_no="FIN" + str(random_with_N_digits(7)))
        
        order_item_list_lumpsum.append(order_item_lump)

        if portfolio_item.sip != 0:
            order_item_sip = models.FundOrderItem.objects.create(portfolio_item=portfolio_item,
                                                                 order_amount=portfolio_item.sip,
                                                                 agreed_sip=portfolio_item.sip,
                                                                 agreed_lumpsum=0,
                                                                 internal_ref_no="FIN" + str(random_with_N_digits(7)))
            order_item_list_sip.append(order_item_sip)
            

    order_detail_lump = models.OrderDetail.objects.create(user=txn.user, order_status=0, transaction=txn,
                                                          is_lumpsum=True, vendor=exchange_vendor)
    order_detail_lump.fund_order_items.set(order_item_list_lumpsum)

    order_detail_sip = None
    if order_item_list_sip:
        order_detail_sip = models.OrderDetail.objects.create(user=txn.user, order_status=0, transaction=txn, vendor=exchange_vendor)
        order_detail_sip.fund_order_items.set(order_item_list_sip)
            
    
    return order_detail_lump, order_detail_sip


def get_is_enabled(portfolio_item):
    """
    :return: True is non elss related portfolio item and if its elss fund related portfolio item then returns true only
    if its more than 3 years old
    """
    if portfolio_item.fund.type_of_fund != 'T':
        return True
    else:
        # Checks that they are atleast 3 years old
        return (datetime.now().date() - portfolio_item.investment_date).days > 365 * 3


def get_fund_detail(portfolio_item):
    """

    :param portfolio_item:
    :return:
    """
    date = get_latest_date_funds_only()

    # add all allocated units
    unit_alloted__sum = models.FundOrderItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=True).aggregate(Sum('unit_alloted'))['unit_alloted__sum']
    if unit_alloted__sum == None:
        unit_alloted__sum = 0.0

    # subtract all redeem units
    unit_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if unit_redeemed__sum == None:
        unit_redeemed__sum = 0.0

    # Subtracts all unverified amount redeem requested
    unverified_amount_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False
    ).aggregate(Sum('redeem_amount'))['redeem_amount__sum']
    if unverified_amount_redeemed__sum == None:
        unverified_amount_redeemed__sum = 0.0

    # Subtracts all unverified unit redeem requested
    unverified_units_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False, is_all_units_redeemed=True
    ).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if unverified_units_redeemed__sum == None:
        unverified_units_redeemed__sum = 0.0

    nav = models.HistoricalFundData.objects.get(fund_id=portfolio_item.fund.id, date=date).nav
    return_value = ((unit_alloted__sum - unit_redeemed__sum - unverified_units_redeemed__sum) * nav
                    ) - unverified_amount_redeemed__sum
    portfolio_detail_dict = {'name': portfolio_item.fund.fund_name,
                             'fund_id': portfolio_item.fund.id,
                             'return_value': round(return_value, 2),
                             'is_enabled': get_is_enabled(portfolio_item),
                             'minimum_withdrawal': portfolio_item.fund.minimum_withdrawal,
                             'minimum_balance': portfolio_item.fund.minimum_balance
                             }
    return portfolio_detail_dict


def update_funds_list(funds_list, portfolio_item):
    """
    :param funds_list
    :param portfolio_item
    :return: updated fund data
    """
    date = get_latest_date_funds_only()
    index = next(index for (index, d) in enumerate(funds_list) if d["fund_id"] == portfolio_item.fund.id)

    # add all allocated units
    unit_alloted__sum = models.FundOrderItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=True).aggregate(Sum('unit_alloted'))['unit_alloted__sum']
    if unit_alloted__sum == None:
        unit_alloted__sum = 0.0

    # subtract all redeem units
    unit_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if unit_redeemed__sum == None:
        unit_redeemed__sum = 0.0

    # Subtracts all unverified amount redeem requested
    unverified_redeemed_amount__sum = models.FundRedeemItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False
    ).aggregate(Sum('redeem_amount'))['redeem_amount__sum']
    if unverified_redeemed_amount__sum == None:
        unverified_redeemed_amount__sum = 0.0

    # Subtracts all unverified unit redeem requested
    unverified_units_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False
    ).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if unverified_units_redeemed__sum == None:
        unverified_units_redeemed__sum = 0.0

    nav = models.HistoricalFundData.objects.get(fund_id=portfolio_item.fund.id, date=date).nav
    return_value =  ((unit_alloted__sum - unit_redeemed__sum - unverified_units_redeemed__sum) * nav
                     ) - unverified_redeemed_amount__sum
    funds_list[index]['return_value'] += round(return_value, 2)
    return funds_list


def get_redeem_fund(fund_redeem_item):
    """

    :param fund_redeem_item:
    :return:
    """
    redeem_fund_detail = {'name': fund_redeem_item.portfolio_item.fund.fund_name,
                          "fund_id": fund_redeem_item.portfolio_item.fund.id,
                          'redeem_amount': fund_redeem_item.redeem_amount}
    return redeem_fund_detail


def get_latest_date():
    """
    returns latest nav date for funds/indices and category
    :return:the minimum date frm daily indices
    """
    minimum_date_object, minimum_date = None, date.today()

    historical_fund_objects_by_max_date = models.Fund.objects.annotate(max_date=Max('historicalfunddata__date'))
    for historical_fund_object in historical_fund_objects_by_max_date:
        if historical_fund_object.max_date < minimum_date:
            minimum_date = historical_fund_object.max_date

    historical_indices_objects_by_max_date = models.Indices.objects.annotate(max_date=Max('historicalindexdata__date'))
    for historical_index_object in historical_indices_objects_by_max_date:
        if historical_index_object.max_date < minimum_date:
            minimum_date = historical_index_object.max_date

    historical_category_objects_by_max_date = models.HistoricalCategoryData.objects.order_by('category_code', '-date'
                                                                                             ).distinct('category_code')
    for historical_category_object in historical_category_objects_by_max_date:
        if historical_category_object.date < minimum_date:
            minimum_date = historical_category_object.date
    return minimum_date


def get_latest_date_funds_only():
    """
    returns latest nav date for funds
    :return:the minimum date fron funds
    """
    minimum_date_object, minimum_date = None, date.today()

    historical_fund_objects_by_max_date = models.Fund.objects.annotate(max_date=Max('historicalfunddata__date'))
    for historical_fund_object in historical_fund_objects_by_max_date:
        if historical_fund_object.max_date < minimum_date:
            minimum_date = historical_fund_object.max_date
    return minimum_date


def get_indice_latest_working_date(index):
    """
    :param index:
    :return:
    """
    list = models.HistoricalIndexData.objects.filter(index=index).order_by('-date')[:3]
    nav_list = []
    for i in list:
        if i.date.isoweekday() < 6:
            nav_list.append(i)
    latest_date = nav_list[0].date
    return latest_date


def get_dashboard_change_date():
    """
    :return: Minimum dates among all funds date + BSE and NSE
    """
    NSE = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[0])
    BSE = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[1])
    NSE_latest = get_indice_latest_working_date(NSE)
    BSE_latest = get_indice_latest_working_date(BSE)
    return min(NSE_latest, BSE_latest)


def get_start_date(funds, index, end_date):
    """
    returns start dates list for five years, three years, one year, three months, one month
    :param funds: a list of funds
    :param index: an index name
    :param end_date: the date at which intervals will end
    :return:
    """
    start_dates = [end_date - relativedelta(years=5), end_date - relativedelta(years=3),
                   end_date - relativedelta(years=1), end_date - relativedelta(months=3),
                   end_date - relativedelta(months=1)]
    index = models.Indices.objects.get(index_name=index)
    funds = list(funds)
    funds.append(index)
    is_modified = False
    message = ''
    for fund in funds:
        for index in range(len(start_dates)):
            if fund.inception_date > start_dates[index]:
                start_dates[index], is_modified = fund.inception_date, True
                message = '*Note: Complete data available from {}.'.format(datetime.strftime(fund.inception_date,
                                                                                             '%d-%m-%Y'))
    return start_dates, is_modified, message


def create_order_items_based_on_next_allotment_date():
    """
    utility to add order items based on next allotment date via cron
    :return:
    """
    #TODO add amount to portfolio/portfolio item
    order_detail_map = {}
    # search all fund order items with next allotment date of today
    fund_order_items_with_today_allotment_date = models.FundOrderItem.objects.filter(next_allotment_date=date.today(), is_future_sip_cancelled=False)

    # create a fund order item object and club them in a dict with key as uer
    for fund_order_item in fund_order_items_with_today_allotment_date:
        new_fund_item = models.FundOrderItem.objects.create(portfolio_item=fund_order_item.portfolio_item,
                                                            order_amount=fund_order_item.agreed_sip,
                                                            agreed_sip=fund_order_item.agreed_sip,
                                                            agreed_lumpsum=fund_order_item.agreed_lumpsum,
                                                            internal_ref_no= "FIN" + str(random_with_N_digits(7)))

        try:
            order_detail_map[fund_order_item.portfolio_item.portfolio.user].append(new_fund_item)
        except KeyError:
            order_detail_map.update({fund_order_item.portfolio_item.portfolio.user: [new_fund_item]})

    # create order items based on the dict created above
    for order_detail_user in order_detail_map:
        order_detail = models.OrderDetail.objects.create(user=order_detail_user, order_status=0)
        for fund_order_item in order_detail_map[order_detail_user]:
            order_detail.fund_order_items.add(fund_order_item)
    return len(order_detail_map)


def club_investment_redeem_together(all_investments_of_user, all_redeem_of_user):
    """
    Clubs together the investments and redeems of a user based on funds
    :param all_investments_of_user: a list of investments(fund order item objects) of a user
    :param all_redeem_of_user: a list of redeems(fund redeem item objects) of a user
    :return: a dict with key as fund and value as a list of investments and redeem made in that fund
    """
    amount_invested_fund_map, distinct_dates, today_portfolio = {}, set(), False
    portfolios_to_be_considered = []

    # club the investments
    for investment in all_investments_of_user:
        try:
            amount_invested_fund_map[investment.portfolio_item.fund].append(investment)
        except KeyError:
            amount_invested_fund_map.update({investment.portfolio_item.fund: [investment]})
        distinct_dates.add(investment.allotment_date)
        portfolios_to_be_considered.append(investment.portfolio_item.portfolio)

    # club the redeems in the same dict too
    for redeem in all_redeem_of_user:
        try:
            amount_invested_fund_map[redeem.portfolio_item.fund].append(redeem)
        except KeyError:
            amount_invested_fund_map.update({redeem.portfolio_item.fund: [redeem]})
        distinct_dates.add(redeem.redeem_date)

    if len(distinct_dates) == 1 and distinct_dates.pop() == get_dashboard_change_date():
        today_portfolio = True

    sorted_portfolios_to_be_considered = list(set(portfolios_to_be_considered))
    sorted_portfolios_to_be_considered.sort(key=lambda x: x.investment_date)
    return amount_invested_fund_map, today_portfolio, sorted_portfolios_to_be_considered



def xirr_calculation(fund_data, start_date, end_date):
    """
    :param fund_data: it consists of these keys: fund_name, id, lumpsum amt, sip amount
    :param start_date
    :param end_date
    :return: the calculated xirr value
    """
    cashflows = []
    temp_start_date = start_date
    temp_end_date = end_date
    final_amount, count, total_cashflow = 0, 1, 0
    fund_data_nav = [models.HistoricalFundData.objects.filter(fund_id=i.get('id')).latest('modified_at').nav for i in fund_data]
    while True:
        if temp_start_date > temp_end_date:
            break
        for index, i in enumerate(fund_data):
            if count == 1:
                total_cashflow += i.get('lumpsum_amount', 0) + i.get('sip_amount', 0)
                cashflows.append((temp_start_date, i.get('sip_amount', 0)))
                cashflows.append((temp_start_date, i.get('lumpsum_amount', 0)))
                nav = get_historical_fund_data(i.get('id'), temp_start_date)
                if nav is not None:
                    final_amount += (round(i.get('sip_amount', 0) / nav, 3) + round(i.get('lumpsum_amount', 0) / nav, 3)) * fund_data_nav[index]
                else:
                    final_amount += round(i.get('sip_amount', 0)) + round(i.get('lumpsum_amount', 0)) + 1
            else:
                cashflows.append((temp_start_date, i.get('sip_amount', 0)))
                total_cashflow += i.get('sip_amount', 0)
                nav = get_historical_fund_data(i.get('id'), temp_start_date)
                if nav is not None:
                    final_amount += (round(i.get('sip_amount', 0) / nav, 3) * fund_data_nav[index])
                else:
                    final_amount += round(i.get('sip_amount', 0))
        temp_start_date += timedelta(30)
        count += 1
    cashflows.append((get_dashboard_change_date(), -final_amount))
    return cashflows, final_amount, total_cashflow


def no_of_months(start_date, end_date):
    """
    :param start_date
    :param end_date
    :return: no of 30 days months between two months
    """
    count = 0
    while start_date < end_date:
        count += 1
        start_date += timedelta(30)
    return count


def get_ending_date(sip_amount_1, lumpsum_amount_1, start_date_1, end_date_1, start_date_2, lumpsum_amount_2, sip_amount_2):
    """
    :param sip_amount_1
    :param lumpsum_amount_1
    :param start_date_1
    :param end_date_1
    :param start_date_2
    :param lumpsum_amount_2
    :param sip_amount_2
    :return: end_date_2 which signifies date at which amount limit would reach
    """
    if start_date_2 > end_date_1:
        return (1, None)
    elif start_date_2 + timedelta(30 * 3) <= end_date_2:
        return (2, None)
    else:
        total_withstanding_amount = lumpsum_amount_1 + sip_amount_1 * (no_of_months(start_date_1, end_date_1))
        given_amount = lumpsum_amount_1 + lumpsum_amount_2 + (sip_amount_1) * (no_of_months(start_date_1, start_date_2))
        difference_amount = total_withstanding_amount - given_amount
        numerator = difference_amount
        denominator = sip_amount_1 + sip_amount_2
        rem_months = numerator / denominator
        days = numerator % denominator
        end_date_2 = start_date_2 + timedelta(30 * (rem_months - 1)) + timedelta(days)
        return (3, end_date_2 - timedelta(90))


def get_historical_fund_data(id, temp_start_date):
    """
    :param id: fund id
    :param temp_start_date
    :return: historical fund data object
    """
    try:
        historical_fund_data = models.HistoricalFundData.objects.get(fund_id=id, date=temp_start_date)
        nav = historical_fund_data.nav
    except models.HistoricalFundData.DoesNotExist:
        nav = None
    return nav


def get_all_fund_data(user):
    """
    :return: all the fund data
    """
    fund_data = []
    portfolio_items = models.PortfolioItem.objects.filter(portfolio__has_invested=False, portfolio__user=user).select_related('fund')
    for portfolio_item in portfolio_items:
        fund_data.append(get_fund_data(portfolio_item))
    return fund_data


def get_all_equity_fund_type_data(user):
    """
    :return: all the equity type fund data
    """
    fund_data = []
    portfolio_items = models.PortfolioItem.objects.filter(portfolio__has_invested=False, portfolio__user=user, fund__type_of_fund=constants.FUND_MAP.get("equity")).select_related('fund')
    for portfolio_item in portfolio_items:
        fund_data.append(get_fund_data(portfolio_item))
    return fund_data


def get_all_debt_fund_type_data(user):
    """
    :return: all the debt type fund data
    """
    fund_data = []
    portfolio_items = models.PortfolioItem.objects.filter(portfolio__has_invested=False, portfolio__user=user, fund__type_of_fund=constants.FUND_MAP.get("debt")).select_related('fund')
    for portfolio_item in portfolio_items:
        fund_data.append(get_fund_data(portfolio_item))
    return fund_data


def get_all_elss_fund_type_data(user):
    """
    :return: all the elss type fund data
    """
    fund_data = []
    portfolio_items = models.PortfolioItem.objects.filter(portfolio__has_invested=False, portfolio__user=user, fund__type_of_fund=constants.FUND_MAP.get("elss")).select_related('fund')
    for portfolio_item in portfolio_items:
        fund_data.append(get_fund_data(portfolio_item))
    return fund_data


def get_fund_data(portfolio_item):
    """
    :param portfolio_item
    "return: meta data about fund
    """
    return {"sip_amount": portfolio_item.sip,
            "id": portfolio_item.fund.id,
            "lumpsum_amount": portfolio_item.lumpsum}


def generate_total_xirr():
    """
    Creates aggregate portfolio for users
    :return: count of users having portfolio and of type not invested
    """
    users_related_to_order_detail = models.OrderDetail.objects.all().select_related('user')
    exclude_user_id = [order_detail.user.id for order_detail in users_related_to_order_detail]
    users_related_to_portfolios = models.Portfolio.objects.filter(has_invested=False).exclude(
        user__id__in=exclude_user_id).select_related('user')
    users = [(users_related_to_portfolio.user, users_related_to_portfolio.created_at) for users_related_to_portfolio in users_related_to_portfolios]
    for user in users:
        fund_data = get_all_fund_data(user[0])
        cashflows, final_amount, total_cashflow = xirr_calculation(fund_data, user[1], datetime.now())
        try:
            total_xirr = xirr.xirr(cashflows)
        except Exception as e:
            print("XIRR failed for following input")
            print(cashflows)
            total_xirr = 0.0
        total_xirr = 0 if type(total_xirr) is complex else total_xirr * 100
        profile_models.AggregatePortfolio.objects.update_or_create(
            user=user[0], defaults={'total_xirr': round(total_xirr, 1), 'update_date': datetime.now()})
    return (len(users))


def sum_invested_in_portfolio_item(portfolio_item, include_unverified=False):
    """
    :param portfolio_item:
    :return: The sum of order_amount added and redeem_amount subtracted for a particular item
    """
    date = get_latest_date_funds_only()
    nav = models.HistoricalFundData.objects.get(fund_id=portfolio_item.fund.id, date=date).nav

    unit_alloted__sum = models.FundOrderItem.objects.filter(
        portfolio_item=portfolio_item, is_verified=True).aggregate(Sum('unit_alloted'))['unit_alloted__sum']
    if unit_alloted__sum == None:
        unit_alloted__sum = 0.0
    unit_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item=portfolio_item, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if unit_redeemed__sum == None:
        unit_redeemed__sum = 0.0

    if include_unverified:
        # Subtracts all unverified amount redeem requested
        unverified_amount_redeemed__sum = models.FundRedeemItem.objects.filter(
            portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False
        ).aggregate(Sum('redeem_amount'))['redeem_amount__sum']
        if unverified_amount_redeemed__sum == None:
            unverified_amount_redeemed__sum = 0.0

        # Subtracts all unverified unit redeem requested
        unverified_units_redeemed__sum = models.FundRedeemItem.objects.filter(
            portfolio_item_id=portfolio_item.id, is_verified=False, is_cancelled=False
        ).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
        if unverified_units_redeemed__sum == None:
            unverified_units_redeemed__sum = 0.0

        return (unit_alloted__sum - unit_redeemed__sum - unverified_units_redeemed__sum) * nav - unverified_amount_redeemed__sum
    return (unit_alloted__sum - unit_redeemed__sum) * nav


def units_invested_in_portfolio_item(portfolio_item):
    """
    :param portfolio_item:
    :return:
    """
    unit_alloted__sum = models.FundOrderItem.objects.filter(
        portfolio_item=portfolio_item, is_verified=True).aggregate(Sum('unit_alloted'))['unit_alloted__sum']
    if unit_alloted__sum == None:
        unit_alloted__sum = 0.0
    unit_redeemed__sum = models.FundRedeemItem.objects.filter(
        portfolio_item=portfolio_item, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if unit_redeemed__sum == None:
        unit_redeemed__sum = 0.0

    return unit_alloted__sum - unit_redeemed__sum


def generate_units_allotment():
    """
    generates units of fund order and redeem items
    :return: frequency of fund order and redeem items whose units have to be alloted
    """
    historical_fund_data_objects = models.HistoricalFundData.objects.order_by('fund_id__id', '-date').distinct('fund_id__id').select_related('fund_id')
    historical_fund_id = {historical_object.fund_id.id: historical_object.date for historical_object in historical_fund_data_objects}

    debug_logger.debug("The Fund Order items whose units were alloted are\n")
    # Add units alloted on FundOrderItem Level
    fund_order_items = models.FundOrderItem.objects.filter(~Q(allotment_date=None) & Q(unit_alloted=None) & Q(is_cancelled=False)).select_related('portfolio_item')
    for fund_order_item in  fund_order_items:
        if fund_order_item.allotment_date <= historical_fund_id[fund_order_item.portfolio_item.fund.id]:
            nav = models.HistoricalFundData.objects.get(date=fund_order_item.allotment_date, fund_id=fund_order_item.portfolio_item.fund).nav
            unit_alloted = round(fund_order_item.order_amount / nav, 3)
            fund_order_item.unit_alloted = unit_alloted
            fund_order_item.is_verified = True
            if not fund_order_item.orderdetail_set.all()[0].is_lumpsum:
                next_allotment_date = models.get_next_allotment_date_or_start_date(fund_order_item)
                fund_order_item.next_allotment_date = next_allotment_date
            fund_order_item.save()
            debug_logger.debug("ID " + str(fund_order_item.id) + " for user " +
                               str(fund_order_item.portfolio_item.portfolio.user.email))

    debug_logger.debug("The Fund Redeem items whose units are alloted are\n")
    # Add units redeemed on FundRedeemItem Level
    redeem_items = models.FundRedeemItem.objects.filter(~Q(redeem_date=None) & (Q(unit_redeemed=None) | Q(unit_redeemed=0.0)) & Q(is_cancelled=False)).select_related('portfolio_item')
    for redeem_item in redeem_items:
        if redeem_item.redeem_date <= historical_fund_id[redeem_item.portfolio_item.fund.id]:
            nav = models.HistoricalFundData.objects.get(date=redeem_item.redeem_date, fund_id=redeem_item.portfolio_item.fund).nav
            unit_redeemed = round(redeem_item.redeem_amount / nav, 3)
            redeem_item.unit_redeemed = unit_redeemed
            redeem_item.is_verified = True
            redeem_item.save()
            debug_logger.debug("ID " + str(redeem_item.id) + " for user " + str(
                redeem_item.portfolio_item.portfolio.user.email))

    debug_logger.debug("The Redeem details whose units are alloted are\n")
    redeem_details = models.RedeemDetail.objects.filter(~Q(redeem_date=None) & (Q(unit_redeemed=None) | Q(unit_redeemed=0.0)) & Q(is_cancelled=False))
    # Adds units redeemed at RedeemDetail level
    for redeem_detail in redeem_details:
        if redeem_detail.redeem_date <= historical_fund_id[redeem_detail.fund.id]:
            nav = models.HistoricalFundData.objects.get(date=redeem_detail.redeem_date, fund_id=redeem_detail.fund).nav
            unit_redeemed = round(redeem_detail.redeem_amount / nav, 3)
            redeem_detail.unit_redeemed = unit_redeemed
            redeem_detail.is_verified = True
            redeem_detail.save()
            debug_logger.debug("ID " + str(redeem_detail.id) + " for user " + str(redeem_detail.user.email))


    debug_logger.debug("The Redeem details whose amounts verified are\n")
    redeem_details_new = models.RedeemDetail.objects.filter(is_cancelled=False, is_verified=False, redeem_amount=0.00
                                                            ).exclude(unit_redeemed=None)
    # Adds redeem_amount at RedeemDetail level
    for redeem_detail in redeem_details_new:
        if redeem_detail.redeem_date and redeem_detail.redeem_date <= historical_fund_id[redeem_detail.fund.id]:
            nav_on_redeem_date = models.HistoricalFundData.objects.get(fund_id=redeem_detail.fund,
                                                                       date=redeem_detail.redeem_date)
            redeem_detail.redeem_amount = redeem_detail.unit_redeemed * nav_on_redeem_date.nav
            redeem_detail.is_verified = True
            redeem_detail.save()
            debug_logger.debug("ID " + str(redeem_detail.id) + " for user " + str(redeem_detail.user.email))

    debug_logger.debug("The Fund Redeem items whose redeem amount are alloted are\n")
    redeem_items_new = models.FundRedeemItem.objects.filter(is_cancelled=False, is_verified=False, redeem_amount=0.00
                                                            ).exclude(unit_redeemed=None)
    # Adds redeem_amount at FundRedeemItem level
    for redeem_item in redeem_items_new:
        if redeem_item.redeem_date and redeem_item.redeem_date <= historical_fund_id[redeem_item.portfolio_item.fund.id]:
            nav_on_redeem_date = models.HistoricalFundData.objects.get(fund_id=redeem_item.portfolio_item.fund,
                                                                       date=redeem_item.redeem_date)
            redeem_item.redeem_amount = redeem_item.unit_redeemed * nav_on_redeem_date.nav
            redeem_item.is_verified = True
            redeem_item.save()
            debug_logger.debug("ID " + str(redeem_item.id) + " for user " + str(redeem_item.portfolio_item.portfolio.user.email))

    return len(fund_order_items) + len(redeem_items) + len(redeem_details) + len(redeem_items_new) + len(redeem_details_new)


def generate_user_graph(user):
    """
    :param user:
    :return: the points to be plotted on y-axis
    """
    earliest_user_portfolio = models.Portfolio.objects.filter(user=user).order_by('created_at')[0]
    # get the earliest portfolio associated with user
    earliest_date = earliest_user_portfolio.created_at.date()

    # returns latest nav date for funds/indices and category
    last_date = get_latest_date()
    return generate_graph_for_portfolio(user, earliest_date, last_date)


def generate_graph_for_portfolio(user, earliest_date, last_date):
    """
    :param user:
    :return: the normalised points to be plotted on y-axis for portfolio between earliest and last date
    """
    fund_order_items = models.FundOrderItem.objects.filter(portfolio_item__portfolio__user=user, is_verified=True)
    fund_redeem_items = models.FundRedeemItem.objects.filter(portfolio_item__portfolio__user=user, is_verified=True)
    order_detail_units, points = {}, []
    order_detail_units = defaultdict(lambda: 0, order_detail_units)

    # associates unit alloted to fund id in order detail units dictionary
    for fund_order_item in fund_order_items:
        order_detail_units[fund_order_item.portfolio_item.fund.id] += fund_order_item.unit_alloted

    for fund_redeem_item in fund_redeem_items:
        order_detail_units[fund_redeem_item.portfolio_item.fund.id] -= fund_redeem_item.unit_redeemed

    # generates final nav value associated with each date
    if len(fund_order_items) > 0:
        while earliest_date <= last_date:
            final_amount = 0
            for key, value in order_detail_units.items():
                nav = models.HistoricalFundData.objects.get(fund_id=key, date=earliest_date).nav
                final_amount += (nav * value)
            points.append((earliest_date, final_amount))
            earliest_date += timedelta(1)

        # unique dates sorted in ascending order
        all_dates = set()
        amt, amt_final = {}, {}
        amt = defaultdict(lambda: 0, amt)
        amt_final = defaultdict(lambda: 0, amt_final)

        # associates allotment date with order amount
        fund_order_items = fund_order_items.order_by('allotment_date')
        for j in fund_order_items:
            amt[j.allotment_date] += j.order_amount
            all_dates.add(j.allotment_date)

        # associates allotment date with redeem amount
        fund_redeem_items = fund_redeem_items.order_by('redeem_date')
        for j in fund_redeem_items:
            amt[j.redeem_date] -= j.redeem_amount
            all_dates.add(j.redeem_date)

        # associates each date with net amount
        all_dates = sorted(all_dates)
        prev_amt = None
        for dates in all_dates:
            if prev_amt is None:
                amt_final[dates] = amt[dates]
                prev_amt = amt_final[dates]
            else:
                amt_final[dates] = prev_amt + amt[dates]
                prev_amt = amt_final[dates]

        list_all_dates = [i for i in all_dates]
        ypoints = []

        # find all nav(s) existing between two dates and then normalize them by dividing with net amount
        for i in range(len(list_all_dates)):
            if i + 1 == len(list_all_dates):
                break
            start_date = list_all_dates[i]
            end_date = list_all_dates[i + 1]
            for point in points:
                if point[0] >= start_date and point[0] < end_date:
                    ypoints.append(round(point[1] / amt_final[start_date], 3))
        i = len(list_all_dates) - 1
        for point in points:
            if point[0] >= list_all_dates[i] and point[0] < last_date:
                ypoints.append(round(point[1] / amt_final[list_all_dates[i]], 3))
        return ypoints
    return []


def calculate_sip_lumpsum_category_wise_for_a_portfolio(portfolio):
    """
    utility to calculate sip and lumpsum category wise (equity/elss/debt)  for a portfolio

    :param portfolio: portfolio of a user
    :return: a dict with keys as categories whose value is a dict containing keys - lumpsum and sip and their amount
    as respective values
    """
    category_sip_lumpsum_map = {
        constants.EQUITY: {constants.LUMPSUM: 0, constants.SIP: 0, constants.SIP_COUNT: 0, constants.LUMPSUM_COUNT: 0},
        constants.DEBT: {constants.LUMPSUM: 0, constants.SIP: 0, constants.SIP_COUNT: 0, constants.LUMPSUM_COUNT: 0},
        constants.ELSS: {constants.LUMPSUM: 0, constants.SIP: 0, constants.SIP_COUNT: 0, constants.LUMPSUM_COUNT: 0}
    }

    # loop through all portfolio items of a portfolio and increase category sip/lumpsum if portfolio item's fund type is
    # as category
    for portfolio_item in portfolio.portfolioitem_set.all():
        sip_lump = category_sip_lumpsum_map[portfolio_item.fund.get_type_of_fund_display().lower()]
        if portfolio_item.lumpsum > 0:
            sip_lump[constants.LUMPSUM] += portfolio_item.lumpsum
            sip_lump[constants.LUMPSUM_COUNT] += 1
            
        if portfolio_item.sip > 0:
            sip_lump[constants.SIP] += portfolio_item.sip
            sip_lump[constants.SIP_COUNT] += 1

    return category_sip_lumpsum_map


def change_portfolio(category_sip_lumpsum_map, user_portfolio, fund_id_map):
    """
    utility to delete old portfolio items and create new portfolio items based on the fund id map

    :param category_sip_lumpsum_map: a map of sip and lumpsum in each category
    :param user_portfolio: the user portfolio object
    :param fund_id_map: a map for fund ids in each category
    :return:
    """
    # utility to calculate number of funds according to lumpsum and debt
    number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip, \
    number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum, is_error, \
    errors = get_number_of_funds(category_sip_lumpsum_map)

    # compare and evaluate the minimum of new funds length and number of funds received from above
    # the minimum of the two will be used to allocate sum investment in each fund
    number_of_fund_map = calculate_minimum_number_of_funds_for_category(
        fund_id_map, number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip,
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum)

    # create new portfolio items
    for category in constants.FUND_CATEGORY_LIST:
        if fund_id_map[category]:
            get_funds_to_allocate_to_user(
                category,
                number_of_fund_map[category][constants.SIP],
                number_of_fund_map[category][constants.LUMPSUM],
                category_sip_lumpsum_map,
                user_portfolio,
                fund_id_map[category])


def calculate_minimum_number_of_funds_for_category(
        fund_id_map, number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip,
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum):
    """
    calculates the minimum number of funds for each category and returns it as a dict

    :param fund_id_map:a map of fund ids for each category
    :param number_of_equity_funds_by_sip: number of equity funds by sip according to user answers
    :param number_of_equity_funds_by_lumpsum: number of equity funds by lumpsum according to user answers
    :param number_of_debt_funds_by_sip: number of debt funds by sip according to user answers
    :param number_of_debt_funds_by_lumpsum: number of debt funds by lumpsum according to user answers
    :param number_of_elss_funds_by_sip: number of elss funds by sip according to user answers
    :param number_of_elss_funds_by_lumpsum: number of elss funds by lumpsum according to user answers
    :return:
    """
    number_of_funds_map ={
        constants.EQUITY: {
            constants.SIP: min(number_of_equity_funds_by_sip, len(fund_id_map[constants.EQUITY])),
            constants.LUMPSUM: min(number_of_equity_funds_by_lumpsum, len(fund_id_map[constants.EQUITY]))
        },
        constants.DEBT: {
            constants.SIP: min(number_of_debt_funds_by_sip, len(fund_id_map[constants.DEBT])),
            constants.LUMPSUM: min(number_of_debt_funds_by_lumpsum, len(fund_id_map[constants.DEBT]))
        },
        constants.ELSS: {
            constants.SIP: min(number_of_elss_funds_by_sip, len(fund_id_map[constants.ELSS])),
            constants.LUMPSUM: min(number_of_elss_funds_by_lumpsum, len(fund_id_map[constants.ELSS]))
        }
    }

    return number_of_funds_map


def generate_xirr(simple_return, number_of_days):
    """
    generates xirr based on simple return and days

    :param simple_return: simple return in number_of_days
    :param days: the number of days
    :return:
    """
    if number_of_days <= 0:
        return 0
    else:
        r1 = ((1 + simple_return) ** (1 / number_of_days)) - 1
        return ((1 + r1) ** (365)) - 1




def find_funds_with_sip_lower_than_minimum_sip(total_category_sip, sip_count, fund_ids):
    """
    checks if sip investment for each fund is more than its minimum sip investment
    :param total_category_sip: the total sip allotted to a category
    :param sip_count: the number of funds to which the amount is to be distributed
    :param fund_ids: the fund ids to which the amount is to be distributed
    :return:
    """
    defected_funds = ''

    if sip_count == 0:
        sip_count = len(fund_ids)
        
    sip_count = min(sip_count, len(fund_ids))
        
    logger = logging.getLogger('django.debug')
    logger.debug("find_funds_with_sip_lower_than_minimum_sip: SIP count: " + str(sip_count))

    # loop through the new funds selected and check the minimum sip condition
    sip_allocation_to_each_fund = total_category_sip / sip_count
    user_selected_funds = models.Fund.objects.filter(id__in=fund_ids)
    for index, fund in enumerate(user_selected_funds):
        if index >= sip_count:
            logger.debug("find_funds_with_sip_lower_than_minimum_sip: Break at SIP count: " + str(sip_count))
            break
        if fund.minimum_sip_investment > sip_allocation_to_each_fund:
            defected_funds += '\n' + fund.legal_name

    return defected_funds[1:]


def generate_total_xirr_for_particular_user(user):
    """
    generates xirr for particular user
    :param user
    :return: xirr for particular user
    """
    try:
        user_portfolio = models.Portfolio.objects.get(has_invested=False, user=user)
        fund_data = get_all_fund_data(user_portfolio.user)
        cashflows, final_amount, total_cashflow = xirr_calculation(fund_data, user_portfolio.created_at, datetime.now())
        cashflows.sort(key=lambda tup: tup[0])
        xirr.xirr(cashflows)
    except models.Portfolio.DoesNotExist:
        print("Portfolio for such user does not exist")


def get_fund_id_map(all_investments_of_user):
    """
    returns mapping of fund id to their order amount
    :param: all_investement_of_user
    """
    fund_id_dict = {}
    fund_id_dict = defaultdict(lambda: 0, fund_id_dict)
    for fundorderitem in all_investments_of_user:
        fund_id_dict[fundorderitem.portfolio_item.fund.id] += fundorderitem.order_amount

    return fund_id_dict


def get_asset_dict(fund_name, sum_invested, total_amount):
    """
    returns a new asset of particular fund type
    :param: fund_nam
    :param: sum_invested
    :param: total_amount
    """
    category_overview = {
            constants.NAME: fund_name,
            constants.HOLDING_PERCENTAGE: round(sum_invested * 100 / total_amount),
            constants.CURRENT_VALUE: round(sum_invested),
            constants.INVESTED: sum_invested,
            constants.GAIN: 0,
            constants.GAIN_PERCENTAGE: 0,
            constants.IS_GAIN: True
        }
    return category_overview


def modify_asset(portfolio_detail, index, total_amount, asset_amount):
    """
    returns portfolio detail after modifying hold percentage, current value, invested amount of fund of particular type
    :param: portfolio_detil
    :param: index
    :param: total_amount
    :param: asset_amount
    """
    portfolio_detail[constants.ASSET_CLASS_OVERVIEW][index][constants.INVESTED] += asset_amount
    portfolio_detail[constants.ASSET_CLASS_OVERVIEW][index][constants.CURRENT_VALUE] += asset_amount
    deno = portfolio_detail[constants.ASSET_CLASS_OVERVIEW][index][constants.INVESTED]
    hold_perc = round(total_amount * 100 / deno)
    portfolio_detail[constants.ASSET_CLASS_OVERVIEW][index][constants.HOLDING_PERCENTAGE] = hold_perc

    return portfolio_detail


def add_order_amount_to_portofolio(portfolio_detail, fund_id_dict):
    """
    returns portfolio detail after adding order amount
    :param: portfolio_detail
    :param: fund_id_dict
    """
    equity_type_id = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[constants.EQUITY]).values('id')
    debt_type_id = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[constants.DEBT]).values('id')
    elss_type_id = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[constants.ELSS]).values('id')
    total_amount, equity_amount, debt_amount, elss_amount = 0, 0, 0, 0
    for equity in equity_type_id:
        equity_amount += fund_id_dict[equity['id']]
        total_amount += fund_id_dict[equity['id']]
    for debt in debt_type_id:
        debt_amount += fund_id_dict[debt['id']]
        total_amount += fund_id_dict[debt['id']]
    for elss in equity_type_id:
        elss_amount += fund_id_dict[elss['id']]
        total_amount += fund_id_dict[elss['id']]

    portfolio_detail[constants.PORTFOLIO_OVERVIEW][constants.INVESTED] += total_amount
    current_value = round(portfolio_detail[constants.PORTFOLIO_OVERVIEW][constants.CURRENT_VALUE][constants.VALUE] + total_amount, 2)
    portfolio_detail[constants.PORTFOLIO_OVERVIEW][constants.CURRENT_VALUE][constants.VALUE] = current_value

    try:
        equity_index = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW]) if d[constants.NAME] == constants.EQUITY)
        portfolio_detail = modify_asset(portfolio_detail, equity_index, total_amount, equity_amount)
    except:
        portfolio_detail[constants.ASSET_CLASS_OVERVIEW].append(get_asset_dict(constants.EQUITY, total_amount, equity_amount))

    try:
        debt_index = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW]) if d[constants.NAME] == constants.DEBT)
        portfolio_detail = modify_asset(portfolio_detail, debt_index, total_amount, debt_amount)
    except:
        portfolio_detail[constants.ASSET_CLASS_OVERVIEW].append(get_asset_dict(constants.DEBT, total_amount, debt_amount))

    try:
        elss_index = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW]) if d[constants.NAME] == constants.ELSS)
        portfolio_detail = modify_asset(portfolio_detail, elss_index, total_amount, elss_amount)
    except:
        portfolio_detail[constants.ASSET_CLASS_OVERVIEW].append(get_asset_dict(constants.ELSS, total_amount, elss_amount))

    return portfolio_detail


def modify_portfolio_for_scheme(portfolio_detail, ids, total_amount, fund_id_dict):
    """
    """
    for index in ids:
        try:
            fund_id = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW][equity_index][constants.VALUE]) if d[constants.ID] == index['id'])
            portfolio_detail[constants.ASSET_CLASS_OVERVIEW][equity_index][constants.VALUE][fund_id][constants.CURRENT_VALUE] += fund_id_dict[index['id']]
            portfolio_detail[constants.ASSET_CLASS_OVERVIEW][equity_index][constants.VALUE][fund_id][constants.INVESTED_VALUE] += fund_id_dict[index['id']]
            invested_amount = portfolio_detail[constants.ASSET_CLASS_OVERVIEW][equity_index][constants.VALUE][fund_id][constants.INVESTED_VALUE]
            fund_per = (total_amount * 100 / invested_amount)
            portfolio_detail[constants.ASSET_CLASS_OVERVIEW][equity_index][constants.VALUE][fund_id][constants.FUND_PERCENTAGE] = fund_per 
            fund_id_dict.pop(index['id'])
        except:
            pass

    return portfolio_detail, fund_id_dict


def get_total_amount(fund_id_dict):
    """
    returns sum of all order amounts of all funds
    :param: fund_id_dict
    """
    total_amount = 0
    for key, value in fund_id_dict:
        total_amount += value

    return total_amount


def create_portfolio_detail_dict(key, value, total_amount):
    """
    returns a portfolio detail dictionary
    :param: key
    :param: value
    :parama: total_amount
    """
    fund_name = models.Fund.objects.get(id=key).fund_name
    portfolio_detail_dict = {constants.FUND_NAME: fund_name,
                             constants.CURRENT_VALUE: round(value),
                             constants.RETURN_PERCENTAGE: 0,
                             constants.IS_GAIN: True ,
                             constants.FUND_PERCENTAGE: round(total_amount * 100 / value, 2),
                             constants.GAIN: 0,
                             constants.INVESTED_VALUE: value,
                             constants.ID: key}

    return portfolio_detail_dict


def add_order_amount_to_schemes(portfolio_detail, fund_id_dict):
    """
    adds order amount to schemes
    :params: portfolio_detail
    :params: fund_id_dict
    """
    equity_type_id = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[constants.EQUITY]).values('id')
    debt_type_id = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[constants.DEBT]).values('id')
    elss_type_id = models.Fund.objects.filter(type_of_fund=constants.FUND_MAP[constants.ELSS]).values('id')
    total_amount = get_total_amount(fund_id_dict)

    equity_index = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW]) if d[constants.KEY] == constants.EQUITY)
    debt_index = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW]) if d[constants.KEY] == constants.DEBT)
    elss_index = next(index for (index, d) in enumerate(portfolio_detail[constants.ASSET_CLASS_OVERVIEW]) if d[constants.KEY] == constants.ELSS)

    portfolio_detail, fund_id_dict = modify_portfolio_for_scheme(portfolio_detail, equity_type_id, total_amount, fund_id_dict)
    portfolio_detail, fund_id_dict = modify_portfolio_for_scheme(portfolio_detail, debt_type_id, total_amount, fund_id_dict)
    portfolio_detail, fund_id_dict = modify_portfolio_for_scheme(portfolio_detail, elss_type_id, total_amount, fund_id_dict)

    for key, value in fund_id_dict:
        try:
            index = next(index for (index, d) in enumerate(equity_type_id) if d['id'] == key)
            portfolio_detail[constants.ASSET_CLASS_OVERVIEW][equity_index][constants.VALUE].append(create_portfolio_detail_dict(key, value, total_amount))
            continue
        except:
            pass

        try:
            index = next(index for (index, d) in enumerate(debt_type_id) if d['id'] == key)
            portfolio_detail[constants.ASSET_CLASS_OVERVIEW][debt_index][constants.VALUE].append(create_portfolio_detail_dict(key, value, total_amount))
            continue
        except:
            pass

        try:
            index = next(index for (index, d) in enumerate(elss_type_id) if d['id'] == key)
            portfolio_detail[constants.ASSET_CLASS_OVERVIEW][elss_index][constants.VALUE].append(create_portfolio_detail_dict(key, value, total_amount))
        except:
            pass


def get_dashboard_version_two(transaction_fund_map, today_portfolio, portfolios_to_be_considered,
                              is_transient_dashboard):
    """
    utility to return data required for dashboard page

    :param transaction_fund_map:a dict with keys as fund objects and values as transactions made by a user for those
           funds
    :param today_portfolio: a boolean whose value is
           -False if at least one fund order item exists for a user whose allotment date is earlier than todays date
           -True if all fund order items of a user are of todays date
    :param portfolios_to_be_considered: user portfolios to be considered for financial goal card
    :param is_transient_dashboard: a boolean to specify if dashboard is transient
    :return:
    """
    portfolio_overview, asset_class_overview, yesterday_changes, port_date = \
        make_xirr_calculations_for_dashboard_version_two(transaction_fund_map, constants.DASHBOARD, today_portfolio,
                                                         is_transient_dashboard)

    financial_goal_status = calculate_financial_goal_status(asset_class_overview, portfolios_to_be_considered)

    
    return {constants.FINANCIAL_GOAL_STATUS: financial_goal_status,
            constants.ASSET_CLASS_OVERVIEW: asset_class_overview, 
            constants.PORTFOLIO_OVERVIEW: portfolio_overview,
            constants.YESTERDAY_CHANGE: yesterday_changes, 
            constants.DATE: get_dashboard_change_date(),
            constants.IS_VIRTUAL: False}
    

def convert_dashboard_to_leaderboard(dashboard_data):
    """
    utility to convert dashboard data of a user to leaderboard data
    :param dashboard_data: the dashboard data of a user
    :return:
    """
    dashboard_data.pop(constants.CURRENT_PORTFOLIO)
    asset_class_overview = dashboard_data[constants.ASSET_CLASS_OVERVIEW]
    for category_overview in asset_class_overview:
        for funds in category_overview[constants.VALUE]:
            funds.pop(constants.CURRENT_VALUE)
            funds.pop(constants.GAIN)
            funds.pop(constants.INVESTED_VALUE)
    return dashboard_data


def make_xirr_calculations_for_dashboard_version_two(transaction_fund_map, api_type, today_portfolio,
                                                     is_transient_dashboard=False):
    """
    utility to make calculations for dashboard version two

    :param transaction_fund_map: a dict with keys as fund objects and values as transactions made by a user for those
           funds
    :param api_type: the api type for which response is to be sent(dashboard)
    :param today_portfolio: a boolean whose value is
           -False if at least one fund order item exists for a user whose allotment date is earlier than todays date
           -True if all fund order items of a user are of today's date
    :param is_transient_dashboard: a boolean to specify if dashboard is transient
    :return:
    """
    portfolio_current_value, portfolio_invested_value, previous_day_value_of_a_portfolio = 0, 0, 0
    array_for_portfolio_gain_calculation, date_for_portfolio = [], date.today()
    asset_class_overview = [
        {constants.KEY: constants.EQUITY, constants.VALUE: []},
        {constants.KEY: constants.DEBT, constants.VALUE: []},
        {constants.KEY: constants.ELSS, constants.VALUE: []}
    ]
    portfolio_current_value_for_yesterday_change, previous_day_value_of_a_portfolio_for_yesterday_change = 0, 0
    portfolio_current_verified_value = 0
    # a dict for category sum invested, category current value, category current verified value and
    # category gain calculation array
    # it has keys as - elss, debt and equity and value as an array whose first value is sum invested in the category
    # second value is current value of the category and third value is an array for gain calculation for that category
    category_dashboard_map = OrderedDict([
        (constants.EQUITY, [0, 0, 0, [], False]), (constants.DEBT, [0, 0, 0, [], False]),
        (constants.ELSS, [0, 0, 0, [], False])
    ])

    latest_date = get_dashboard_change_date()
    # loop through each fund in transaction_fund_map and calculate gain for the fund
    for fund in transaction_fund_map:
        # get the latest fund data and one previous fund data(for yesterday change card)
        latest_fund_data, fund_one_previous_nav = calculate_latest_and_one_previous_nav(fund, latest_date)
        if isinstance(latest_fund_data, models.FundDataPointsChangeDaily):
            latest_fund_data_nav = latest_fund_data.day_end_nav
            if latest_fund_data.day_end_date < date_for_portfolio:
                date_for_portfolio = latest_fund_data.day_end_date
        else:
            latest_fund_data_nav = latest_fund_data.nav
            if latest_fund_data.date < date_for_portfolio:
                date_for_portfolio = latest_fund_data.date

        # utility to get sum invested, current value, one previous day value and array for gain calculation for that
        # fund and then calculate gain percenatge and gain based on these
        sum_invested_in_the_fund, current_value_of_a_fund, previous_day_value_of_a_fund, \
        array_for_fund_gain_calculation, current_value_of_a_fund_for_yesterday_change, \
        previous_day_value_of_fund_for_yesterday_change, current_verified_value_of_fund = get_current_value_of_a_fund(
            transaction_fund_map[fund], latest_fund_data_nav, fund_one_previous_nav)

        # add these to portfolio current value portfolio sum invested and array for portfolio gain calculation
        # also based on the type of fund add them to respective categories(elss/debt/equity)
        portfolio_current_value += current_value_of_a_fund
        previous_day_value_of_a_portfolio += previous_day_value_of_a_fund
        portfolio_current_value_for_yesterday_change += current_value_of_a_fund_for_yesterday_change
        previous_day_value_of_a_portfolio_for_yesterday_change += previous_day_value_of_fund_for_yesterday_change
        portfolio_invested_value += sum_invested_in_the_fund
        # 0 corresponds to sum invested in the category
        category_dashboard_map[constants.FUND_MAP_REVERSE[fund.type_of_fund]][0] += sum_invested_in_the_fund
        # 1 corresponds to current value of the category
        category_dashboard_map[constants.FUND_MAP_REVERSE[fund.type_of_fund]][1] += current_value_of_a_fund
        category_dashboard_map[constants.FUND_MAP_REVERSE[fund.type_of_fund]][4] = True
        if array_for_fund_gain_calculation:
            portfolio_current_verified_value += current_verified_value_of_fund
            array_for_portfolio_gain_calculation += array_for_fund_gain_calculation
            # 2 corresponds to category verified current value
            category_dashboard_map[constants.FUND_MAP_REVERSE[fund.type_of_fund]][2] += current_verified_value_of_fund
            # 3 corresponds to array for category gain calculation
            category_dashboard_map[constants.FUND_MAP_REVERSE[fund.type_of_fund]][3] += array_for_fund_gain_calculation
            array_for_fund_gain_calculation.append((get_dashboard_change_date(), -current_verified_value_of_fund))
            try:
                gain_percentage_of_a_fund = xirr.xirr(array_for_fund_gain_calculation)
            except Exception as e:
                print("XIRR failed for following input")
                print(array_for_fund_gain_calculation)
                gain_percentage_of_a_fund = 0.0
        else:
            gain_percentage_of_a_fund = 0
        
        debug_logger.debug("gain percent: " + str(gain_percentage_of_a_fund))
        # make asset class overview for portfolio details
        for category in asset_class_overview:
            if category.get(constants.KEY) == constants.FUND_MAP_REVERSE[fund.type_of_fund]:
                category.get(constants.VALUE).append(make_fund_dict_for_portfolio_detail(
                    fund.fund_name, current_value_of_a_fund, gain_percentage_of_a_fund, sum_invested_in_the_fund, fund.id))

    if api_type == constants.DASHBOARD:
        portfolio_overview = make_portfolio_overview_new(
            portfolio_current_value, portfolio_invested_value, array_for_portfolio_gain_calculation,
            portfolio_current_verified_value)
        financial_goal_status = make_asset_class_overview_new(category_dashboard_map, portfolio_current_value)
        yesterday_changes = make_yesterday_change_dashboard(
            previous_day_value_of_a_portfolio_for_yesterday_change, portfolio_current_value_for_yesterday_change,
            today_portfolio, latest_date, is_transient_dashboard)
        return portfolio_overview, financial_goal_status, yesterday_changes, date_for_portfolio
    elif api_type == constants.PORTFOLIO_DETAILS:
        current_portfolio = make_current_portfolio_for_dashboard(
            portfolio_current_value, array_for_portfolio_gain_calculation, portfolio_current_verified_value)
        asset_class_overview = calculate_fund_holding_percentage(asset_class_overview, portfolio_current_value)
        return {constants.CURRENT_PORTFOLIO: current_portfolio, constants.ASSET_CLASS_OVERVIEW: asset_class_overview}


def calculate_fund_holding_percentage(asset_class_overview, portfolio_current_value):
    """
    calculates holding percentage for each fund
    :param asset_class_overview: a list for funds divided by categories
    :param portfolio_current_value:the current value of portfolio
    :return:
    """
    for category in asset_class_overview:
        if category.get(constants.VALUE):
            for fund in category.get(constants.VALUE):
                if portfolio_current_value == 0:
                    fund_holding_percentage = 0
                else:
                    fund_holding_percentage = round(fund[constants.CURRENT_VALUE] * 100 / portfolio_current_value, 1)
                fund.update({constants.FUND_PERCENTAGE: fund_holding_percentage})
    return asset_class_overview


def make_current_portfolio_for_dashboard(portfolio_current_value, array_for_portfolio_gain_calculation,
                                         portfolio_current_verified_value):
    """
    utility to make current portfolio card for dashboard
    :param portfolio_current_value: current value of portfolio
    :param array_for_portfolio_gain_calculation: arrar for gain calculation of portfolio
    :param portfolio_current_verified_value: current verified value of portfolio
    :return:
    """
    if array_for_portfolio_gain_calculation:
        array_for_portfolio_gain_calculation.append((get_dashboard_change_date(), -portfolio_current_verified_value))
        try:
            gain = round(xirr.xirr(array_for_portfolio_gain_calculation) * 100, 1)
        except Exception as e:
            gain = 0
            print("XIRR failed for the following")
            print(array_for_portfolio_gain_calculation)
    else:
        gain = 0
    current_portfolio = {
        constants.CORPUS: round(portfolio_current_value),
        constants.GAIN: gain,
        constants.IS_GAIN: True if gain >= 0 else False
    }
    return current_portfolio


def make_portfolio_overview_new(portfolio_current_value, portfolio_invested_value, array_for_portfolio_gain_calculation,
                                portfolio_current_verified_value):
    """
    utility to make portfolio overiew dict for dashboard
    :param portfolio_current_value: current day value of portfolio
    :param portfolio_invested_value: sum invested in the portfolio
    :param array_for_portfolio_gain_calculation: an array for portfolio gain calculation
    :param portfolio_current_verified_value: the current value of portflio according to only verified order items
    :return:
    """
    if array_for_portfolio_gain_calculation:
        array_for_portfolio_gain_calculation.append((get_dashboard_change_date(), -portfolio_current_verified_value))
        try:
            gain = round(xirr.xirr(array_for_portfolio_gain_calculation) * 100, 1)
        except Exception as e:
            gain = 0
            print("XIRR failed for the following")
            print(array_for_portfolio_gain_calculation)
    else:
        gain = 0
    portfolio_overview = {
        constants.INVESTED: round(portfolio_invested_value),
        constants.CURRENT_RETURNS: round(portfolio_current_value - portfolio_invested_value),
        constants.CURRENT_VALUE:{
            constants.VALUE: round(portfolio_current_value),
            constants.GAIN_PERCENTAGE: gain,
            constants.IS_GAIN: True if round(portfolio_current_value - portfolio_invested_value) >= 0 else False
        }
    }
    return portfolio_overview


def make_asset_class_overview_new(category_dashboard_map, portfolio_current_value):
    """
    a utility to make a dict for asset class overview for dashboard
    :param category_dashboard_map: a dict with keys as - elss, debt and equity and value as an array
           whose first value is sum invested in the category second value is current value of the category and
           third value is an array for gain calculation for that category
    :param portfolio_current_value: current value of the portfolio
    :return:
    """
    asset_class_overview = []
    for category in category_dashboard_map:
        # 0 corresponds to invested value of category
        category_invested_value = round(category_dashboard_map[category][0])
        # 1 corresponds to current value of category
        current_value_of_category = round(category_dashboard_map[category][1])
        # 2 corresponds to current verified value of a category
        current_verified_value_of_category = category_dashboard_map[category][2]
        # 3 corresponds to array for gain calculation
        array_for_category_gain_calculation = category_dashboard_map[category][3]
        if array_for_category_gain_calculation:
            array_for_category_gain_calculation.append((get_dashboard_change_date(), -current_verified_value_of_category))
            try:
                category_gain_percentage = round(xirr.xirr(array_for_category_gain_calculation) * 100, 1)
            except Exception as e:
                category_gain_percentage = 0
                print("XIRR failed for the following")
                print(array_for_category_gain_calculation)
        else:
            category_gain_percentage = 0
        # 4 corresponds to whether category is to be shown or not
        if category_dashboard_map[category][4]:
            category_overview = {
                constants.NAME: category,
                constants.HOLDING_PERCENTAGE: round(current_value_of_category * 100 / portfolio_current_value,
                                                    1) if portfolio_current_value != 0 else 0.0,
                constants.INVESTED: category_invested_value,
                constants.CURRENT_VALUE: current_value_of_category,
                constants.GAIN: current_value_of_category - category_invested_value,
                constants.GAIN_PERCENTAGE: category_gain_percentage,
                constants.IS_GAIN: True if (current_value_of_category - category_invested_value) >= 0 else False
            }
            asset_class_overview.append(category_overview)
    return asset_class_overview


def get_current_value_of_a_fund(transactions_in_a_fund, latest_fund_data_nav, fund_one_previous_nav):
    """
    Utility to get array for gain calculations for a fund, the current value of a fund, invested value in a fund

    loops through the transactions made in a fund by a user.
    If the transaction is an instance of fund order item the order amount is added to sum invested else if transaction
    is an instance of fund redeem item the redeem amount is deducted from sum invested

    If the transaction is verified the current value is added or deducted(for fund order item or fund redeem item
    respectively) as units allotted * fund current nav else if the transaction if not verified the order maount is
    simply added or deducted from current value(for fund order item/fund redeem item respectively))

    :param transactions_in_a_fund:the transactions(investments and redeems) in a fund
    :param latest_fund_data: the latest fund data entry
    :param fund_one_previous_nav: one previous day nav of fund
    :return:
    """
    sum_invested_in_the_fund, current_value_of_a_fund, previous_day_value_of_fund = 0, 0, 0
    array_for_fund_gain_calculation = []
    current_value_of_a_fund_for_yesterday_change, previous_day_value_of_fund_for_yesterday_change = 0, 0
    current_verified_value_of_fund = 0

    # loop through each transaction made in a fund
    for transaction in transactions_in_a_fund:
        # if the transaction is an investment
        if isinstance(transaction, models.FundOrderItem):
            sum_invested_in_the_fund += transaction.order_amount
            # if transaction is verified it will be used for gain calculation and current value will be units alloted
            # multiplied by current day nav
            if transaction.is_verified:
                current_value_of_a_fund += transaction.unit_alloted * latest_fund_data_nav
                previous_day_value_of_fund += transaction.unit_alloted * fund_one_previous_nav
                current_verified_value_of_fund += transaction.unit_alloted * latest_fund_data_nav
                array_for_fund_gain_calculation.append((transaction.allotment_date, transaction.order_amount))
                if transaction.allotment_date < date.today():
                    current_value_of_a_fund_for_yesterday_change += transaction.unit_alloted * \
                                                                    latest_fund_data_nav
                    previous_day_value_of_fund_for_yesterday_change += transaction.unit_alloted * fund_one_previous_nav
            # if transaction is not verified it will not be used for gain calculation and current value will be equal
            # to invested amount
            else:
                current_value_of_a_fund += transaction.order_amount
                previous_day_value_of_fund += transaction.order_amount
                current_value_of_a_fund_for_yesterday_change += transaction.order_amount
                previous_day_value_of_fund_for_yesterday_change += transaction.order_amount
        # same as above just deduct the respective amounts rather than adding them
        elif isinstance(transaction, models.FundRedeemItem):
            sum_invested_in_the_fund -= transaction.invested_redeem_amount
            if transaction.is_verified:
                current_verified_value_of_fund -= transaction.unit_redeemed * latest_fund_data_nav
                current_value_of_a_fund -= transaction.unit_redeemed * latest_fund_data_nav
                previous_day_value_of_fund -= transaction.unit_redeemed * fund_one_previous_nav
                array_for_fund_gain_calculation.append((transaction.redeem_date, -transaction.redeem_amount))
                if transaction.redeem_date < date.today():
                    current_value_of_a_fund_for_yesterday_change -= transaction.unit_redeemed * \
                                                                    latest_fund_data_nav
                    previous_day_value_of_fund_for_yesterday_change -= transaction.unit_redeemed * fund_one_previous_nav
            else:
                current_value_of_a_fund -= transaction.redeem_amount
                previous_day_value_of_fund -= transaction.redeem_amount
                current_value_of_a_fund_for_yesterday_change -= transaction.redeem_amount
                previous_day_value_of_fund_for_yesterday_change -= transaction.redeem_amount

    return sum_invested_in_the_fund, current_value_of_a_fund, previous_day_value_of_fund,\
           array_for_fund_gain_calculation, current_value_of_a_fund_for_yesterday_change, \
           previous_day_value_of_fund_for_yesterday_change, current_verified_value_of_fund


def has_redeemable_funds(user):
    """
    :param user:
    :return: True id redeem is allowed
    """
    if models.FundOrderItem.objects.filter(portfolio_item__portfolio__user=user, is_verified=True).count() > 0:
       return True
    return False


def get_current_invested_value_date(date, user):
    """
    :param user:
    :param date:
    :return: current and invested amount for a particular user on a specific date
    """
    fund_id_to_user_map, fund_id_to_nav = {}, {}
    cashflows = []
    fund_id_to_user_map = defaultdict(lambda: 0, fund_id_to_user_map)
    current_amount, invested_amount = 0, 0

    minimum_date = get_latest_date_funds_only()
    if date.date() <= minimum_date:
        minimum_date = date.date()

    order_details = models.OrderDetail.objects.filter(user=user, created_at__lte=date)
    fund_order_items = [order_detail.fund_order_items.filter(is_verified=True, allotment_date__lte=date.date()).all() for order_detail in order_details]
    for order_items in fund_order_items:
        for fund_order_item in order_items:
            fund_id = fund_order_item.portfolio_item.fund.id
            if fund_order_item.unit_alloted:
                fund_id_to_user_map[fund_id] += fund_order_item.unit_alloted
            fund_id_to_nav[fund_id] = models.HistoricalFundData.objects.get(fund_id=fund_id, date=minimum_date).nav
            invested_amount += fund_order_item.order_amount
            cashflows.append((fund_order_item.allotment_date, fund_order_item.order_amount))


    redeem_details = models.RedeemDetail.objects.filter(user=user, created_at__lte=date)
    fund_redeem_items = [redeem_detail.fund_redeem_items.filter(is_verified=True, redeem_date__lte=date.date()).all() for redeem_detail in redeem_details]
    for redeem_items in fund_redeem_items:
        for fund_redeem_item in redeem_items:
            if fund_redeem_item.unit_redeemed:
                fund_id_to_user_map[fund_redeem_item.portfolio_item.fund.id] -= fund_redeem_item.unit_redeemed
            invested_amount -= fund_redeem_item.invested_redeem_amount
            cashflows.append((fund_redeem_item.redeem_date, -fund_redeem_item.redeem_amount))


    for key, value in fund_id_to_nav.items():
        current_amount += fund_id_to_user_map[key] * value

    cashflows.append((date.date(), -current_amount))
    try:
        calc_xirr = xirr.xirr(cashflows)
    except Exception:
        print("XIRR failed for following case")
        print(cashflows)
        calc_xirr = 0.0

    return {"invested_amount": invested_amount,
            "current_amount": current_amount,
            "xirr": calc_xirr}


def tracking_funds_bse_nse():
    """
    :return: Iterates over latest values of funds and also returns data for BSE and NSE
    """
    logger_response = 'The latest values of Funds, BSE and NSE are - \n'
    mail_logger = logging.getLogger('django.debug')

    count = 0
    historical_fund_objects_by_max_date = models.Fund.objects.annotate(max_date=Max('historicalfunddata__date'))
    for i in historical_fund_objects_by_max_date:
        count += 1
        logger_response += str(i.legal_name) + " is updated till date " + str(i.max_date) + "\n"

    NSE = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[0])
    NSE_date = models.HistoricalIndexData.objects.filter(index=NSE).order_by('-date')[0].date
    logger_response += str(NSE.index_name) + " is updated till date " + str(NSE_date) + "\n"
    BSE = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[1])
    BSE_date = models.HistoricalIndexData.objects.filter(index=BSE).order_by('-date')[0].date
    logger_response += str(BSE.index_name) + " is updated till date " + str(BSE_date) + "\n"
    mail_logger.debug(logger_response)

    return count + 2


def add_redeem_details_by_amount(redeem_fund, user):
    """
    :param redeem_fund: a list of objects of form {"fund_id" : xx, "redeem_amount": yy}
    :param user: user who wants to redeem
    :return: returns a list having RedeemDetail object created via this function
    Creates FundRedeemItem and RedeemDetail for a funds in redeem_fund
    """
    redeem_detail_list = []

    for i in redeem_fund:
        fund_redeem_items = []
        portfolio_items = [i.portfolio_item for i in models.FundOrderItem.objects.filter(
            portfolio_item__fund_id=i["fund_id"], orderdetail__user__in=[user], is_verified=True
        ).distinct('portfolio_item')]

        redeem = {}

        # Get the total value invested for a fund for a person
        total = 0.0
        for portfolio_item in portfolio_items:
            sum = sum_invested_in_portfolio_item(portfolio_item, True)
            redeem[portfolio_item.id] = sum
            total += sum

        # Creates FundRedeemItem equal to number of portfolios
        for portfolio_item in portfolio_items:
            redeem_amount = round(i["redeem_amount"]*redeem[portfolio_item.id]/total, 4)
            fund_redeem_item = models.FundRedeemItem.objects.create(portfolio_item=portfolio_item,
                                                                    redeem_amount=redeem_amount)
            fund_redeem_items.append(fund_redeem_item)

        # Adds all fund_redeem_item of one fund to one redeem detail
        redeem_detail = models.RedeemDetail.objects.create(user=user, fund_id=i["fund_id"],
                                                           redeem_amount=i["redeem_amount"])
        redeem_detail.fund_redeem_items.add(*fund_redeem_items)
        redeem_detail_list.append(redeem_detail)

    return redeem_detail_list


def add_redeem_details_by_units(all_units, user, redeem_detail_list):
    """

    :param all_units:
    :param user: user who wants to redeem
    :param redeem_detail_list: a list of redeem_detail_list
    :return: returns an updated list having RedeemDetail object created via this function
    Creates FundRedeemItem and RedeemDetail for a funds in all_units
    """
    for i in all_units:
        fund_redeem_items = []
        portfolio_items = [i.portfolio_item for i in models.FundOrderItem.objects.filter(
            portfolio_item__fund_id=i["fund_id"], orderdetail__user__in=[user], is_verified=True
        ).distinct('portfolio_item')]

        # Creates FundRedeemItem equal to number of portfolios
        for portfolio_item in portfolio_items:
            fund_redeem_item = models.FundRedeemItem.objects.create(portfolio_item=portfolio_item,
                                                                    unit_redeemed=0.0, is_all_units_redeemed=True)
            fund_redeem_items.append(fund_redeem_item)

        # Adds all fund_redeem_item of one fund to one redeem detail
        redeem_detail = models.RedeemDetail.objects.create(user=user, fund_id=i["fund_id"], is_all_units_redeemed=True,
                                                           unit_redeemed=0.0)
        redeem_detail.fund_redeem_items.add(*fund_redeem_items)
        redeem_detail_list.append(redeem_detail)

    return redeem_detail_list


def get_xirr_value_from_dashboard_response(dashboard_response):
    """
    :param dashboard_respons:
    :return: Parse the dashboard response to get overall xirr
    """
    return dashboard_response[constants.PORTFOLIO_OVERVIEW][constants.CURRENT_VALUE][constants.GAIN_PERCENTAGE]


def find_if_not_eligible_for_display(redeem_response, user):
    """
    :param redeem_response:
    :return:
    """
    if redeem_response['return_value'] == 0:
        return True
    units_redeemed = models.FundRedeemItem.objects.filter(
        portfolio_item__fund_id=redeem_response['fund_id'], portfolio_item__portfolio__user=user, is_verified=False,
        is_cancelled=False, is_all_units_redeemed=True,).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
    if units_redeemed is not None:
        if units_redeemed == 0:
            return True


def store_most_popular_fund_data():
    """
    :return:
    """
    cases = {'E': 'equity', 'D': 'debt', 'T': 'elss'}
    popular_funds = dict()
    for k, v in cases.items():
        popular_funds[v] = dict(data=get_most_popular_funds(k))

    models.CachedData.objects.update_or_create(key=constants.MOST_POPULAR_FUND,
                                               defaults={"value":{constants.MOST_POPULAR_FUND: str(popular_funds)}})
    return 0

        
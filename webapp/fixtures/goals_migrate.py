from rest_framework import serializers
from django.db.models import Sum
from webapp.apps import random_with_N_digits
from profiles.models import User
from core.models import Goal, OrderDetail
from core.models import Portfolio, PortfolioItem, FundOrderItem
from core.models import Answer
from core.models import PlanAssestAllocation
from core import constants, goals_helper
from api import utils as api_utils
from django.conf import settings
import os


def calculate_duration(user, answers, portfolio, category):
    duration = 0
    if category == constants.RETIREMENT:
        duration = api_utils.age_calculator(answers, portfolio)
    else:
        try:
            answer = answers.filter(question__question_id='term', portfolio=portfolio)
            if answer:
                duration = int(answer[0].text)
        except:
            duration = 0

    if duration is None:
        duration = 0
    return duration

def get_category_answers(user, question_for, portfolio=None):
    """
    Works for any category that does not have multi text questions
    presently works for - retirement, wedding, other event, buy property, tax, invest, education
    :param user: the user whose answers are to be returned
    :param question_for: category for which answers ar to be returned
    :return:  dict of category related answers by user
    """
    
    category_related_answers = Answer.objects.filter(
        user=user, question__question_for=constants.MAP[question_for], portfolio=portfolio).select_related('question')

    category = question_for + "_allocation"
    try:
        category_allocation = getattr(PlanAssestAllocation.objects.get(user=user, portfolio=portfolio), category)
    except PlanAssestAllocation.DoesNotExist:
        category_allocation = constants.EMPTY_ALLOCATION
        
    return category_related_answers, category_allocation

def migrateAll():
    users = User.objects.all()
    for u in users:
        print("Migrating for user: " + u.email)
        goal_names = {constants.INVEST:1, constants.RETIREMENT:1, constants.TAX_SAVING: 1, constants.OTHER_EVENT:1,
                      constants.BUY_PROPERTY:1, constants.WEDDING: 1, constants.EDUCATION: 1}
        try:
            portfolios = Portfolio.objects.filter(user=u, has_invested=True)
            for p in portfolios:
                for c in constants.ALLOCATION_LIST:
                    answers, allocation = get_category_answers(u, c, p)
                    if answers and len(answers) > 0:
                        cat = constants.MAP[c]
                        duration = calculate_duration(u, answers, p, cat)
                        name = str(constants.ASSET_ALLOCATION_MAP[cat][2]) + str(goal_names[cat])
                        goal_names[cat] += 1
                        goal, created = Goal.objects.update_or_create(user=u, category=cat, name=name, portfolio=p, defaults={'asset_allocation':allocation, 'duration':duration})
                        answers.all().update(goal=goal)
            
            for c in constants.ALLOCATION_LIST:
                answers, allocation = get_category_answers(u, c)
                if answers and len(answers) > 0:
                    cat = constants.MAP[c]
                    duration = calculate_duration(u, answers, None, cat)
                    try:
                        p = Portfolio.objects.get(user=u, has_invested=False)
                    except:
                        p = None
                    name = str(constants.ASSET_ALLOCATION_MAP[cat][2]) + str(goal_names[cat])
                    goal_names[cat] += 1
                    goal, created = Goal.objects.update_or_create(user=u, category=cat, name=name, portfolio=p, defaults={'asset_allocation':allocation, 'duration':duration})
                    answers.all().update(goal=goal)
        except Exception as e:
            print('Error for user: ' + u.email + ' : ' + str(e))

def get_goals_with_asset_type(goals, asset_type):
    goal_list = []
    for g in goals:
        if float(g.asset_allocation[asset_type]) > 0:
            goal_list.append(g)
            
def match_portfolio_with_lumpsum_goal(portfolio_items, goal_list, asset_type):
    goals_done = []
    for g in goal_list:
        goal_object = goals_helper.GoalBase.get_goal_instance(g)
        allocation = goal_object.get_asset_allocation_amount()
        goal_sip = allocation[asset_type][constants.SIP]
        goal_lumpsum = allocation[asset_type][constants.LUMPSUM]
        
        if goal_lumpsum > 0 and goal_sip == 0:
            portfolio_index = []
            for p in portfolio_items:
                if p.lumpsum > 0:
                    if p.sip == 0:
                        p.update(goal=g)
                        portfolio_index.append(p)
                    else:
                        kwargs = {}
                        kwargs["broad_category_group"] = p.fund.type_of_fund
                        kwargs[constants.SIP] = 0
                        kwargs[constants.LUMPSUM] = p.lumpsum
                        kwargs['sum_invested'] = p.lumpsum
                        p_new, created = PortfolioItem.objects.update_or_create(portfolio_id=p.portfolio.id, goal=g, fund_id=p.fund.id, defaults=kwargs)
                        p.update(lumpsum = 0)
                        foi = FundOrderItem.objects.get(portfolio_item=p, orderdetail__is_lumpsum=True)
                        foi_new = FundOrderItem.objects.create(portfolio_item=p_new,
                                                              order_amount=p.lumpsum,
                                                              agreed_sip=0,
                                                              agreed_lumpsum=p.lumpsum,
                                                              internal_ref_no="FIN" + str(random_with_N_digits(7)),
                                                              folio_number=foi.folio_number,
                                                              allotment_date=foi.allotment_date,
                                                              is_verified=foi.is_verified,
                                                              unit_alloted=foi.unit_alloted,
                                                              bse_transaction_id=foi.bse_transaction_id)
                        order_detail = foi.orderdetail_set.all()[0]
                        order_detail.fund_order_items.add(foi_new)
                        foi.update(agreed_lumpsum=0, order_amount=0)
            for p in portfolio_index:
                portfolio_items.remove(p)
            goals_done.append(g)
            continue
    
    return portfolio_items, goals_done

def match_portfolio_with_goal(portfolio_items, goals, asset_type):
    goal_list = get_goals_with_asset_type(goals, asset_type)
    
    portfolio_items, goals_done = match_portfolio_with_lumpsum_goal(portfolio_items, goal_list, asset_type)
    for g in goal_list:
        if g in goals_done:
            continue
        
        goal_object = goals_helper.GoalBase.get_goal_instance(g)
        allocation = goal_object.get_asset_allocation_amount()
        goal_sip = allocation[asset_type][constants.SIP]
        goal_lumpsum = allocation[asset_type][constants.LUMPSUM]

        direct_allocation = None
        for p in portfolio_items:
            if p.sip == goal_sip and p.lumpsum == goal_lumpsum:
                p.update(goal=g)
                direct_allocation = p
                break
        
        if direct_allocation:
            portfolio_items.remove(direct_allocation)
            goals_done.append(g)
            continue
        
        for p in portfolio_items:
            if p.lumpsum <= goal_lumpsum and p.sip <= goal_sip:
                p.update(goal=g)
                goal_lumpsum -= p.lumpsum
                goal_sip -= p.sip
        
        if goal_sip <= 0 and goal_lumpsum <= 0:
            goals_done.append(g)
    
    print("Goals Done: " + asset_type)
    for g in goals_done:
        print(str(g))
    return goals_done

def migrate_portfolio():
    users = User.objects.all()
    for u in users:
        print("Migrating for user: " + u.email)
        try:
            p = Portfolio.objects.get(user=u, has_invested=False)
            u.rebuild_portfolio = True
        except:
            pass
    
        portfolios = Portfolio.objects.filter(user=u, has_invested=True, is_deleted=False)
        for p in portfolios:
            
            goals = Goal.objects.filter(portfolio=p)
            if len(goals) > 1:
                portfolio_items_elss = PortfolioItem.objects.filter(portfolio=p, broad_category_group=constants.FUND_MAP[constants.ELSS])
                for g in goals:
                    if g.category == constants.TAX_SAVING:
                        portfolio_items_elss.update(goal=g)

                portfolio_items_equity = PortfolioItem.objects.filter(portfolio=p, broad_category_group=constants.FUND_MAP[constants.EQUITY])
                portfolio_items_debt = PortfolioItem.objects.filter(portfolio=p, broad_category_group=constants.FUND_MAP[constants.DEBT])
                
                match_portfolio_with_goal(portfolio_items_equity, goals, constants.EQUITY)                
                match_portfolio_with_goal(portfolio_items_debt, goals, constants.DEBT)
            else:
                p.portfolioitem_set.all().update(goal=goals[0])
                    
                
        orders = OrderDetail.objects.filter(user=u, is_lumpsum=True, fund_order_items__agreed_sip__gt=0)
        for o in orders:
            portfolio_item = o.fund_order_items[0].portfolio_item
            o_sip = OrderDetail.objects.filter(user=u, is_lumpsum=False, fund_order_items__portfolio_item=portfolio_item).order_by('created_at').first()
            if o_sip:
                o.fund_order_items.update(agreed_sip=0)
                o.add(o_sip.fund_order_items)
                o_sip.delete() 
    
migrateAll()

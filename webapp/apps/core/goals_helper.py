from django.db.models import Q
from datetime import date
from abc import ABC
import logging
from core import models
from core import utils, helpers
from core import serializers, constants



class GoalBase(ABC):
    error_logger = logging.getLogger('django.error')
    
    def __init__(self, goal_object=None):
        super(GoalBase, self).__init__()
        self.goal_object = goal_object

    @staticmethod
    def get_current_goal(user, goal_type):
        try:
            return models.Goal.objects.get(Q(user=user), Q(category=goal_type), Q(portfolio=None) | (Q(portfolio__has_invested=False) & Q(portfolio__is_deleted=False)))
        except:
            return None

    @staticmethod
    def get_current_goals(user):
        return models.Goal.objects.filter(Q(user=user), Q(portfolio=None) | (Q(portfolio__has_invested=False) & Q(portfolio__is_deleted=False)))

    @staticmethod
    def get_portfolio_goals(user, portfolio):
        return models.Goal.objects.filter(user=user, portfolio=portfolio)

    @staticmethod
    def get_goal(user, goal_id):
        try:
            return models.Goal.objects.get(id=goal_id, user=user)
        except:
            return None

    @staticmethod
    def get_invested_goals(user):
        return models.Goal.objects.filter(user=user, portfolio__has_invested=True, portfolio__is_deleted=False)
    
    @staticmethod
    def get_goal_instance(goal_object):
        if goal_object.category == constants.INVEST:
            return QuickInvestGoal(goal_object)
        elif goal_object.category == constants.TAX_SAVING:
            return TaxGoal(goal_object)
        elif goal_object.category == constants.RETIREMENT:
            return RetirementGoal(goal_object)
        elif goal_object.category == constants.LIQUID_GOAL:
            return LiquidGoal(goal_object)
        else:
            return GenericGoal(goal_object)

    @staticmethod        
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
                lumpsum_equity, lumpsum_debt = helpers.roundTo100(lumpsum_equity, lumpsum_debt)
                    
        if sip_equity > 0 and sip_debt > 0:
            if sip_amount%100 == 0 and sip_equity%100 > 0:
                sip_equity, sip_debt = helpers.roundTo100(sip_equity, sip_debt)
                
        return lumpsum_equity, lumpsum_debt, sip_equity, sip_debt

    def get_sip_amount(self, data=None):
        sip = 0
        if data:
            sip = data.get('sip')
        else:
            if self.goal_object:
                try:
                    answer = self.goal_object.answer_set.get(question__question_id="sip")
                    if answer:
                        sip = float(answer.text)
                except Exception:
                    pass
        
        if sip is None:
            sip = 0
        return sip
    
    def get_sip_growth(self):
        if self.goal_object:
            try:
                answer = self.goal_object.answer_set.get(question__question_id="grow_sip")
                if answer:
                    return float(answer.text)
            except Exception as e:
                pass
              
        return 0
        
    def get_lumpsum_amount(self, data=None):
        lumpsum = 0
        if data:
            lumpsum = data.get('lumpsum')
        else:
            if self.goal_object:
                try:
                    answer = self.goal_object.answer_set.get(question__question_id="lumpsum")
                    if answer:
                        lumpsum = float(answer.text)
                except:
                    pass

        if lumpsum is None:
            lumpsum = 0
                          
        return lumpsum
        
    def get_duration(self, data=None):
        if data and data.get("term"):
            return data.get("term")
        else: 
            if self.goal_object:
                return self.goal_object.duration
        return 0

    def get_default_term(self):
        if self.goal_object:
            return self.goal_object.duration
        return 0
    
    def get_allocation(self, data):
        if data:
            return data.get('allocation')
        
        if self.goal_object:
            return self.goal_object.asset_allocation
    
    def get_answer_value(self, key, value):
        return value, None


    def get_default_goalname(self, goal_type):
        return ""
     
    def create_or_update_goal(self, user, data, goal_type, goal_name=None):

        allocation = self.get_allocation(data)
        allocation_dict = utils.make_allocation_dict(self.get_sip_amount(data), self.get_lumpsum_amount(data), allocation)

        equity_sip, equity_lumpsum, debt_sip, debt_lumpsum, elss_sip, elss_lumpsum, is_error, errors,liquid_sip, liquid_lumpsum= \
            utils.get_number_of_funds(allocation_dict)
        if is_error:
            return is_error, errors

        if not goal_name:
            goal_name = self.get_default_goalname(goal_type)
            
        if data.get('allocation'):
            data.pop('allocation')
            
        goal_serializer = serializers.GoalSerializer(data={'user':user.id, 'category':goal_type, 'name':goal_name, 'asset_allocation':allocation})
        if goal_serializer.is_valid():
            goal_name = goal_serializer.validated_data.get("name")
            allocation = goal_serializer.validated_data.get('asset_allocation')
            duration = self.get_duration(data)

            goal = self.get_current_goal(user, goal_type)
            
            if goal:
                goal.name = goal_name
                goal.asset_allocation = allocation
                goal.duration = duration
                goal.save()
            else:
                goal = models.Goal.objects.create(user=user, category=goal_type, name=goal_name, asset_allocation=allocation, duration=duration)
                            
            for key, value in data.items():
                value, option_id = self.get_answer_value(key, value)
                if option_id:
                    option_selected = models.Option.objects.get(option_id=option_id, question__question_id=key,
                                                                question__question_for=goal_type)
                    defaults = {'option': option_selected}
                else:
                    defaults = {'text': str(value)}

                question = models.Question.objects.get(question_id=key, question_for=goal_type)
                models.Answer.objects.update_or_create(
                        question_id=question.id, user=user, goal=goal, portfolio=None, defaults=defaults)

        else:
            is_error = True
            errors = {"serializerError": str(goal_serializer.errors)}
        return is_error, errors

    def get_asset_allocation_amount(self):
        '''
        Given a lumpsum and sip amount calculate the amounts allocated per asset class.  
        '''
        if not self.goal_object:
            return 0, 0, 0, 0, 0, 0
        
        lumpsum_amount = self.get_lumpsum_amount()
        sip_amount = self.get_sip_amount()
        
        allocation = self.goal_object.asset_allocation
        
        elss_lumpsum, elss_sip, liquid_lumpsum, liquid_sip = 0, 0, 0, 0
        
        if float(allocation[constants.ELSS]):
            elss_lumpsum = round((lumpsum_amount * float(allocation[constants.ELSS])) / 100)
            elss_sip = round((sip_amount * float(allocation[constants.ELSS])) / 100)

        if allocation.get(constants.LIQUID) and float(allocation[constants.LIQUID]):
            liquid_lumpsum += round((lumpsum_amount * float(allocation[constants.LIQUID])) / 100)
            liquid_sip += round((sip_amount * float(allocation[constants.LIQUID])) / 100)
            
        equity_lumpsum, debt_lumpsum, equity_sip, debt_sip = self.calculate_asset_allocation(lumpsum_amount, sip_amount, float(allocation[constants.EQUITY]), float(allocation[constants.DEBT]))

        return {constants.EQUITY: {constants.LUMPSUM: equity_lumpsum, constants.SIP: equity_sip},
                constants.DEBT: {constants.LUMPSUM: debt_lumpsum, constants.SIP: debt_sip},
                constants.ELSS: {constants.LUMPSUM: elss_lumpsum, constants.SIP: elss_sip},
                constants.LIQUID: {constants.LUMPSUM: liquid_lumpsum, constants.SIP: liquid_sip}} 

    def get_expected_corpus(self):
        term = self.get_duration()
            
        actual_term = term
        if self.goal_object.category == constants.INVEST and term == 0:
            term = constants.INVEST_MINIMUM_TERM

        sip_amount = self.get_sip_amount()
        lumpsum_amount = self.get_lumpsum_amount()
        category_allocation = self.goal_object.asset_allocation
        growth = self.get_sip_growth()
        corpus = utils.new_expected_corpus(sip_amount, lumpsum_amount,
                             float(category_allocation[constants.DEBT]) / 100,
                             float(category_allocation[constants.EQUITY]) / 100, actual_term, term,
                             growth / 100)
        return corpus, term

    def get_investment_till_date(self):
        from core import portfolio_helper, funds_helper
        
        if not self.goal_object or not self.goal_object.portfolio:
            return 
        
        invested_amount = 0
        investment_value = 0    
        latest_date = funds_helper.FundsHelper.get_dashboard_change_date()
        asset_values = {constants.DEBT: 0, constants.EQUITY: 0, constants.ELSS: 0, constants.LIQUID: 0}
        
        # virtual portfolio
        if not self.goal_object.portfolio.has_invested:
            for portfolio_item in self.goal_object.portfolioitem_set.all():
                portfolio_item.set_values()
                investment_value += portfolio_item.returns_value
                invested_amount += portfolio_item.sum_invested
                asset_values[constants.FUND_MAP_REVERSE[portfolio_item.fund.type_of_fund]] += portfolio_item.returns_value
        else:
            for portfolio_item in self.goal_object.portfolioitem_set.all():
                transactions = portfolio_helper.PortfolioHelper.get_all_transactions(portfolio_item)
                latest_fund_data_nav, latest_fund_data_nav_date, fund_one_previous_nav = funds_helper.FundsHelper.calculate_latest_and_one_previous_nav(portfolio_item.fund, latest_date)
                fund_current_values = utils.get_current_value_of_a_fund(transactions, latest_fund_data_nav, fund_one_previous_nav)
                invested_amount += fund_current_values[0]
                investment_value += fund_current_values[1]
                asset_values[constants.FUND_MAP_REVERSE[portfolio_item.fund.type_of_fund]] += fund_current_values[1]
        
        return_value = { constants.DEBT: asset_values[constants.DEBT],
                        constants.EQUITY: asset_values[constants.EQUITY],
                        constants.ELSS: asset_values[constants.ELSS],
                        constants.LIQUID: asset_values[constants.LIQUID],
                        constants.INVESTED_VALUE: invested_amount, constants.CURRENT_VALUE: investment_value}
        return return_value
        
class GenericGoal(GoalBase):
    def __init__(self, goal_object=None):
        super(GenericGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(GenericGoal, self).create_or_update_goal(user, data, constants.MAP[goal_type], goal_name)

    def get_default_goalname(self, goal_type):
        return constants.CATEGORY_CHOICE_REVERSE[goal_type]

class TaxGoal(GoalBase):
    def __init__(self, goal_object=None):
        super(TaxGoal, self).__init__(goal_object)

    def get_lumpsum_amount(self, data=None):
        lumpsum = 0
        if data:
            lumpsum = data.get('amount_invested')
        else:
            if self.goal_object:
                try:
                    answer = self.goal_object.answer_set.get(question__question_id="amount_invested")
                    if answer:
                        lumpsum = float(answer.text)
                except Exception as e:
                    pass

        if lumpsum is None:
            lumpsum = 0
        
        return lumpsum

    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(TaxGoal, self).create_or_update_goal(user, data, constants.TAX_SAVING, goal_name)

    def get_answer_value(self, key, value):
        option_id = None
        if key == "estimate_needed":
            option_id = "op1" if value else "op2"

        return value, option_id

    def get_default_term(self):
        return constants.TAX_DEFAULT_TERM
    
    def get_expected_corpus(self):
        term = constants.TAX_DEFAULT_TERM
        sip_amount = self.get_sip_amount()
        lumpsum_amount = self.get_lumpsum_amount()
        category_allocation = self.goal_object.asset_allocation
        growth = self.get_sip_growth()
        corpus = utils.new_expected_corpus(sip_amount, lumpsum_amount,
                             float(category_allocation[constants.DEBT]) / 100,
                             float(category_allocation[constants.ELSS]) / 100, term, term,
                             growth / 100)
        return corpus, term

    def get_default_goalname(self, goal_type):
        return "TAX"

    def get_allocation(self, data):
        return constants.TAX_ALLOCATION

class QuickInvestGoal(GoalBase):
    def __init__(self, goal_object=None):
        super(QuickInvestGoal, self).__init__(goal_object)

    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(QuickInvestGoal, self).create_or_update_goal(user, data, constants.INVEST, goal_name)
        
    def get_answer_value(self, key, value):
        option_id = None
        if key == "floating_sip":
            option_id = "op1" if value else "op2"
        return value, option_id
    
    def get_default_goalname(self, goal_type):
        return "INV"
    
class RetirementGoal(GoalBase):
    def __init__(self, goal_object=None):
        super(RetirementGoal, self).__init__(goal_object)

    def get_sip_amount(self, data=None):
        sip = 0
        if data:
            sip = data.get('monthly_investment')
        else:
            if self.goal_object:
                try:
                    answer = self.goal_object.answer_set.get(question__question_id="monthly_investment")
                    if answer:
                        sip = float(answer.text)
                except Exception as e:
                    self.error_logger.error("Error retrieving sip amount: " + str(e))

        if sip is None:
            sip = 0              
        return sip
    
    def get_duration(self, data=None):
        if data and data.get('current_age') and data.get('retirement_age'):
            retirement_age = int(data.get('retirement_age'))
            current_age = int(data.get('current_age'))
            return retirement_age - current_age
        else: 
            if self.goal_object:
                return self.goal_object.duration
        return 0

    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(RetirementGoal, self).create_or_update_goal(user, data, constants.RETIREMENT, goal_name)

    def get_answer_value(self, key, value):
        option_id = None
        if key == "floating_sip":
            option_id = "op1" if value else "op2"
        return value, option_id

    def get_default_goalname(self, goal_type):
        return "RET"
    
    
class LiquidGoal(GoalBase):
    def __init__(self, goal_object=None):
        super(LiquidGoal, self).__init__(goal_object)

    def get_lumpsum_amount(self, data=None):
        lumpsum = 0
        if data:
            lumpsum = data.get('amount_invested')
        else:
            if self.goal_object:
                try:
                    answer = self.goal_object.answer_set.get(question__question_id="amount_invested")
                    if answer:
                        lumpsum = float(answer.text)
                except Exception as e:
                    pass

        if lumpsum is None:
            lumpsum = 0
        
        return lumpsum

    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(LiquidGoal, self).create_or_update_goal(user, data, constants.LIQUID_GOAL, goal_name)

    def get_answer_value(self, key, value):
        option_id = None
        if key == "estimate_needed":
            option_id = "op1" if value else "op2"

        return value, option_id

    def get_default_term(self):
        return constants.LIQUID_DEFAULT_TERM
    
    def get_expected_corpus(self):
        term = constants.LIQUID_DEFAULT_TERM
        sip_amount = self.get_sip_amount()
        lumpsum_amount = self.get_lumpsum_amount()
        category_allocation = self.goal_object.asset_allocation
        growth = self.get_sip_growth()
        corpus = utils.new_expected_corpus(sip_amount, lumpsum_amount,
                             float(category_allocation[constants.LIQUID]) / 100,
                             float(category_allocation[constants.EQUITY]) / 100, term, term,
                             growth / 100)
        return corpus, term

    def get_default_goalname(self, goal_type):
        return "LIQUID"

    def get_allocation(self, data):
        return constants.LIQUID_ALLOCATION

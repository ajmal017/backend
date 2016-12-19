from django.db.models import Q
from datetime import date
from abc import ABC
import logging
from core import models
from core import utils, helpers
from core import serializers, constants
import math
from django.db.models import Avg, Max, Sum, Q




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
        elif goal_object.category == constants.EDUCATION:
            return EducationGoal(goal_object)
        elif goal_object.category == constants.BUY_PROPERTY:
            return PropertyGoal(goal_object)
        elif goal_object.category == constants.AUTO_MOBILE:
            return AutomobileGoal(goal_object)
        elif goal_object.category == constants.VACATION:
            return VacationGoal(goal_object)
        elif goal_object.category == constants.WEDDING:
            return WeddingGoal(goal_object)
        elif goal_object.category == constants.JEWELLERY:
            return JewelleryGoal(goal_object)
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

        equity_sip, equity_lumpsum, debt_sip, debt_lumpsum, elss_sip, elss_lumpsum, liquid_sip, liquid_lumpsum,\
         is_error, errors = utils.get_number_of_funds(allocation_dict)
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

        liquid_percentage = 0
        if allocation.get(constants.LIQUID) and float(allocation[constants.LIQUID]):
            liquid_percentage = float(allocation[constants.LIQUID])
            liquid_lumpsum += round((lumpsum_amount * float(allocation[constants.LIQUID])) / 100)
            liquid_sip += round((sip_amount * float(allocation[constants.LIQUID])) / 100)
            
        equity_lumpsum, debt_lumpsum, equity_sip, debt_sip = self.calculate_asset_allocation(lumpsum_amount, sip_amount, float(allocation[constants.EQUITY]), float(allocation[constants.DEBT]))

        return {constants.EQUITY: {constants.LUMPSUM: equity_lumpsum, constants.SIP: equity_sip, 'percentage': float(allocation[constants.EQUITY])},
                constants.DEBT: {constants.LUMPSUM: debt_lumpsum, constants.SIP: debt_sip, 'percentage': float(allocation[constants.DEBT])},
                constants.ELSS: {constants.LUMPSUM: elss_lumpsum, constants.SIP: elss_sip, 'percentage': float(allocation[constants.ELSS])},
                constants.LIQUID: {constants.LUMPSUM: liquid_lumpsum, constants.SIP: liquid_sip, 'percentage': liquid_percentage}} 

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
                portfolio_item.set_values(latest_date)
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
    
    def calculate_goal_estimation(self,data,user):
        return self.calculate_balance_corpus_required(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        return None 
        
class GenericGoal(GoalBase):
    def __init__(self, goal_object=None):
        super(GenericGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(GenericGoal, self).create_or_update_goal(user, data, constants.MAP[goal_type], goal_name)

    def get_default_goalname(self, goal_type):
        return constants.CATEGORY_CHOICE_REVERSE[goal_type]
    
    def get_answer_value(self, key, value):
        option_id = None
        if key == "location" or key == "estimate_selection_type" or key == "goal_plan_type":
            option_id = value
        return value, option_id
    
    def calculate_goal_estimation(self,data,user):
        return super(GenericGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        for estimate in constants.ESTIMATION_TYPE:
            balance_corpus_required = 0
            
            future_value_for_goal = self.calculate_future_value(data['current_price'],constants.INFLATION_PERCENTAGE["op1"]/100,data['term'])
            amount_self_funded = round(future_value_for_goal * data['prop_of_purchase_cost']/100)
            amount_budgeted_for_goal = round(future_value_for_goal*constants.GENERIC_ESTIMATE_PERCENTAGE[estimate]/100)
            total_amount_required = round(amount_self_funded +amount_budgeted_for_goal)
            
            alrady_saved_corpus = self.calculate_future_value(data['amount_saved'],constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100,data['term'])
            
            if alrady_saved_corpus < total_amount_required:
                balance_corpus_required = total_amount_required - alrady_saved_corpus
            
            estimation_data.append({"estimate_type":estimate,"corpus":balance_corpus_required})
            
        return estimation_data
        
    def calculate_future_value(self,current_value,inflation,term):
        return round(current_value * math.pow((1+inflation),term))
        
    
class EducationGoal(GenericGoal):
    def __init__(self, goal_object=None):
        super(EducationGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(EducationGoal, self).create_or_update_goal(user, data, constants.EDUCATION_TYPE, goal_name)
    
    def get_default_goalname(self, goal_type):
        return "EDU"
    
    def get_answer_value(self, key, value):
        option_id = None
        if key == "location" or key == "field" or key == "estimate_selection_type" or key == "goal_plan_type":
            option_id = value
        return value, option_id
    
    def calculate_goal_estimation(self,data,user):
        return super(EducationGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        for estimate in constants.ESTIMATION_TYPE:
            
            amount_required_current_value =  round((constants.EDUCATION_ESTIMATE_PERCENTAGE[estimate] * \
                                             constants.EDUCATION_COST_ESTIMATE[data['field']][data['location']] )/100)   
     
            
            amount_required_future_value = round(amount_required_current_value * \
                                           math.pow((1+ (constants.INFLATION_PERCENTAGE[data['location']])/100),data['term']))
            
            already_saved_corpus = round(data['amount_saved']* math.pow((1+(constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100)),data['term']))
            
            if already_saved_corpus > amount_required_future_value:
                balance_corpus_required = 0
            else:
                balance_corpus_required = amount_required_future_value - already_saved_corpus
            
            estimation_data.append({"estimate_type":estimate,"corpus":balance_corpus_required})
            
        return estimation_data
    
    
class PropertyGoal(GenericGoal):
    def __init__(self, goal_object=None):
        super(PropertyGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(PropertyGoal, self).create_or_update_goal(user, data, constants.PROPERTY_TYPE, goal_name)
    
    def get_default_goalname(self, goal_type):
        return "PRO"
    
    def calculate_goal_estimation(self,data,user):
        return super(PropertyGoal, self).calculate_goal_estimation(data,user) 
     
     
class AutomobileGoal(GenericGoal):
    def __init__(self, goal_object=None):
        super(AutomobileGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(AutomobileGoal, self).create_or_update_goal(user, data, constants.AUTO_MOBILE_TYPE, goal_name)
    
    def get_default_goalname(self, goal_type):
        return "AUT"
    
    def calculate_goal_estimation(self,data,user):
        return super(AutomobileGoal, self).calculate_goal_estimation(data,user)


class VacationGoal(GenericGoal):
    def __init__(self, goal_object=None):
        super(VacationGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(VacationGoal, self).create_or_update_goal(user, data, constants.VACATION_TYPE, goal_name)
    
    def get_default_goalname(self, goal_type):
        return "VAC"
    
    def calculate_goal_estimation(self,data,user):
        return super(VacationGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        for estimate in constants.ESTIMATION_TYPE:
            balance_corpus_required = 0
            
            number_of_rooms_required = math.trunc((data['number_of_members']/3) + 0.5)
            travel_cost = data['number_of_members'] * constants.VACATION_TRAVEL_COST[data['location']][estimate]
            hotel_cost = number_of_rooms_required * data['number_of_days'] * constants.VACATION_HOTEL_COST[data['location']][estimate]
            total_cost = travel_cost + hotel_cost
            other_cost = total_cost/2
            total_cost += other_cost
            
            required_corpus = self.calculate_future_value(total_cost,constants.INFLATION_PERCENTAGE[data['location']]/100,data['term'])
            already_saved_corpus = self.calculate_future_value(data['amount_saved'],constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100,data['term'])
            
            if already_saved_corpus < required_corpus:
                balance_corpus_required = required_corpus - already_saved_corpus
            
            estimation_data.append({"estimate_type":estimate,"corpus":balance_corpus_required})
            
        return estimation_data
        
    def calculate_future_value(self,current_value,inflation,term):
        return round(current_value * math.pow((1+inflation),term))

class WeddingGoal(GenericGoal):
    def __init__(self, goal_object=None):
        super(WeddingGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(WeddingGoal, self).create_or_update_goal(user, data, constants.WEDDING_TYPE, goal_name)
    
    def get_default_goalname(self, goal_type):
        return "WED"
    
    def calculate_goal_estimation(self,data,user):
        return super(WeddingGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        for estimate in constants.ESTIMATION_TYPE:
            balance_corpus_required = 0
            travel_cost = 0
            stay_cost = 0
            
            catering_cost = data['expected_people']*constants.WEDDING_EXPENSE['catering_cost'][estimate]
            venue_cost = constants.WEDDING_EXPENSE['venue_cost'][estimate]
            decor_cost = constants.WEDDING_EXPENSE['decor_cost'][estimate]
            if data["location"] == constants.OUTSTATION:
                travel_cost = constants.WEDDING_EXPENSE['travel_cost'][estimate]*constants.WEDDING_EXPENSE['no_of_family'][estimate]
                stay_cost = constants.WEDDING_EXPENSE['stay_cost'][estimate]*constants.WEDDING_EXPENSE['no_of_family'][estimate]
            clothing_cost = constants.WEDDING_EXPENSE['no_of_family'][estimate] * constants.WEDDING_EXPENSE['clothing_cost'][estimate]
            bride_groom_cost = constants.WEDDING_EXPENSE['bride_groom_cost'][estimate]
            
            total_cost = round(catering_cost + venue_cost + decor_cost + travel_cost + stay_cost + clothing_cost + bride_groom_cost)
            gifting_cost = round(total_cost/3)
            total_cost += gifting_cost
            
            total_amount_required = self.calculate_future_value(total_cost*(data['sharing_percentage']/100),constants.INFLATION_PERCENTAGE["op1"]/100,data['term'])
            already_saved_corpus = self.calculate_future_value(data['amount_saved'],constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100,data['term'])
            if already_saved_corpus < total_amount_required:
                balance_corpus_required = total_amount_required - already_saved_corpus
            
            estimation_data.append({"estimate_type":estimate,"corpus":balance_corpus_required})
            
        return estimation_data
        
    def calculate_future_value(self,current_value,inflation,term):
        return round(current_value * math.pow((1+inflation),term))
    


class JewelleryGoal(GenericGoal):
    def __init__(self, goal_object=None):
        super(JewelleryGoal, self).__init__(goal_object)
        
    def create_or_update_goal(self, user, data, goal_type, goal_name=""):
        return super(JewelleryGoal, self).create_or_update_goal(user, data, constants.JEWELLERY_TYPE, goal_name)
    
    def get_default_goalname(self, goal_type):
        return "JEW"
    
    def calculate_goal_estimation(self,data,user):
        return super(JewelleryGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        for estimate in constants.ESTIMATION_TYPE:
            balance_corpus_required = 0
            
            future_jewellery_value = self.calculate_future_value(data['current_price'],constants.INFLATION_PERCENTAGE["op1"]/100,data['term'])
            base_amount = round(future_jewellery_value * (constants.JEWELLERY_ESTIMATE_PERCENTAGE[estimate]/100))
            delta_amount = round(base_amount * (constants.JEWELLERY_ESTIMATE_PERCENTAGE[estimate]/100 - 1))
            amount_required = base_amount + delta_amount
            
            already_saved_corpus = self.calculate_future_value(data['amount_saved'], constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100, data['term'])
            if already_saved_corpus < amount_required:
                balance_corpus_required = amount_required - already_saved_corpus
            estimation_data.append({"estimate_type":estimate,"corpus":balance_corpus_required}) 
        return estimation_data
        
    def calculate_future_value(self,current_value,inflation,term):
        return round(current_value * math.pow((1+inflation),term))
    


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
            option_id = value

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
    
    def calculate_goal_estimation(self,data,user):
        return super(TaxGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        
        total_investment = round(data['pff']+ data['loan']+data['insurance']+ data['elss'])
        further_eligibility = max(150000 - total_investment,0)
        potential_tax_benfit = round(further_eligibility * 30.9/100)
        
        estimation_data.append({"further_eligibility":further_eligibility,"potential_tax_benfit":potential_tax_benfit}) 
        return estimation_data
        
    
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
        if key == "estimate_selection_type" or key == "goal_plan_type":
            option_id = value
        return value, option_id

    def get_default_goalname(self, goal_type):
        return "RET"
    
    def calculate_goal_estimation(self,data,user):
        return super(RetirementGoal, self).calculate_goal_estimation(data,user)
    
    def calculate_balance_corpus_required(self,data,user):
        """
        calculate the amount required for current and future
        """ 
        estimation_data = []
        for estimate in constants.ESTIMATION_TYPE:
            balance_corpus_required = 0
            term = data['retirement_age'] - data['current_age']
            
            annual_income = data['monthly_income']*12
            
            total_income_at_retirement = round(annual_income * (math.pow((1+constants.INFLATION_PERCENTAGE["op1"]/100),term)))
            total_expense_at_retirement = round(total_income_at_retirement * constants.RETIREMENT_ESTIMATE_PERCENTAGE[estimate]/100)
            
            assess_answer = utils.get_assess_answer(user)
            gender = assess_answer["A7"]
            
            if data['retirement_age'] < 61:
                life_expectency = 80 if gender == 'op1' else (85)
            else:
                life_expectency = int(data['retirement_age']) + 20
                
            life_expectency_post_retirement = max(life_expectency-data['retirement_age'],20)
            inflation_adjust_returns = round((1+constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100)/(1+constants.INFLATION_PERCENTAGE["op1"]/100)-1 , 4)
            corpus_required_for_retirement = round(total_expense_at_retirement * ((1- math.pow((1+inflation_adjust_returns),(-life_expectency_post_retirement)))/inflation_adjust_returns))
            
            investments_already_made = data.get("amount_saved",0)
            
            already_saved_corpus = round(investments_already_made * math.pow(1+constants.RETURN_ON_EXIST_INVEST_PERCENTAGE/100,term))
            
            if already_saved_corpus < corpus_required_for_retirement:
                balance_corpus_required = corpus_required_for_retirement - already_saved_corpus
            
            estimation_data.append({"estimate_type":estimate,"corpus":balance_corpus_required})
            
        return estimation_data
    
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
        return "LIQ"

    def get_allocation(self, data):
        return constants.LIQUID_ALLOCATION

from django.db.models import Q
from datetime import datetime
from abc import ABC
import logging
from core import models
from core import utils
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
    def get_goal_instance(goal_object):
        if goal_object.category == constants.INVEST:
            return QuickInvestGoal(goal_object)
        elif goal_object.category == constants.TAX_SAVING:
            return TaxGoal(goal_object)
        elif goal_object.category == constants.RETIREMENT:
            return RetirementGoal(goal_object)
        else:
            return GenericGoal(goal_object)
        
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
    
    def get_allocation(self, data):
        return data.get('allocation')
    
    def get_answer_value(self, key, value):
        return value, None

    def get_default_goalname(self, goal_type):
        return ""
     
    def create_or_update_goal(self, user, data, goal_type, goal_name=None):
        allocation = self.get_allocation(data)
        allocation_dict = utils.make_allocation_dict(self.get_sip_amount(data), self.get_lumpsum_amount(data), allocation)

        equity_sip, equity_lumpsum, debt_sip, debt_lumpsum, elss_sip, elss_lumpsum, is_error, errors = \
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

    def get_expected_corpus(self, actual_term, term):
        sip_amount = self.get_sip_amount()
        lumpsum_amount = self.get_lumpsum_amount()
        category_allocation = self.goal_object.asset_allocation
        growth = self.get_sip_growth()
        corpus = utils.new_expected_corpus(sip_amount, lumpsum_amount,
                             float(category_allocation[constants.DEBT]) / 100,
                             float(category_allocation[constants.EQUITY]) / 100, actual_term, term,
                             growth / 100)
        return corpus

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

    def get_expected_corpus(self, actual_term, term):
        sip_amount = self.get_sip_amount()
        lumpsum_amount = self.get_lumpsum_amount()
        category_allocation = self.goal_object.asset_allocation
        growth = self.get_sip_growth()
        corpus = utils.new_expected_corpus(sip_amount, lumpsum_amount,
                             float(category_allocation[constants.DEBT]) / 100,
                             float(category_allocation[constants.ELSS]) / 100, actual_term, term,
                             growth / 100)
        return corpus

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

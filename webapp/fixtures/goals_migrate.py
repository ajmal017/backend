from rest_framework import serializers
from profiles.models import User
from core.models import Goal
from core.models import Portfolio
from core.models import Answer
from core.models import PlanAssestAllocation
from core import constants
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

migrateAll()

from django.shortcuts import render
from django.http import HttpResponseRedirect, QueryDict
from django.core.urlresolvers import reverse
from django.conf import settings
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response as WebResponse

from . import models, serializers, constants, utils, xirr, new_xirr
from api import utils as api_utils
from payment import billdesk
from webapp.apps import generate_error_message
from profiles import constants as cons
from profiles import models as profile_models
from profiles import helpers as profiles_helpers

from dateutil.relativedelta import relativedelta
from datetime import timedelta, datetime, date
import logging
import copy

from profiles.utils import is_investable
from django.views.generic import View
from django.http import HttpResponse
from external_api import constants as external_constants
from external_api import helpers as external_helpers

from django.db.models import Count
from external_api import utils as external_utils
from core import goals_helper, funds_helper



def index(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/index.html')


def my_custom_page_not_found_view(request):
    """
    :param request:
    :return: 404 webpage
    """
    return render(request, 'base/404.html', status=404)


def server_error(request):
    """
    :param request:
    :return: 500 webpage
    """
    return render(request, 'base/500.html', status=500)


def blank(request):
    """
    :param request:
    :return: blank webpage
    """
    fund_houses = models.FundHouse.objects.all().values('name', 'url1', 'url2')
    context = {"fundhouses": fund_houses}
    return render(request, 'base/blank.html', context)

def deprecate_v1_0(request):
    """
    :param request:
    :return: 404 webpage
    """
    deprecateMessage = "Please update the FinAskus application to continue."
    return api_utils.response({"message": deprecateMessage, "login_error": "deprecateMessage"}, status.HTTP_404_NOT_FOUND, deprecateMessage)

def privacy(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/privacy_policy.html')


def faq(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/faqs.html')

def indexnew(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/index-new.html')

def mfbasics(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/mutual-fund-basics.html')


def commission(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/commission.html')

def mfprimer(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/mutual-fund-primer.html')

def deeplinking(request, *args, **kwargs):
    """
    :param request:
    :return:
    """
    customScheme = request.GET.get('customScheme', None)
    if customScheme is None and 'schemeUri' in kwargs:
        customScheme = kwargs.get('schemeUri')
        if not customScheme:
            customScheme = "finaskus.define.financial.goals"
        if customScheme:
            return redirect(reverse('deeplinking', kwargs={'schemeUri':''}) + '?customScheme=' + customScheme)
    return render(request, 'base/deeplinking.html')


def whymf(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/why-invest-in-mutual-funds.html')

def debtfundsrisk(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/debt-funds-risk-free.html')

def sipintime(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/a-sip-in-time-saves-nine.html')

def retirementplanning(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/retirement-planning.html')

def blog(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/blog.html')


def mfarticles(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/mutual-fund-articles.html')

def mailer1(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/MarketingEmailer1.html')

def aboutus(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/aboutus.html')


def terms(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/terms_conditions.html')


def disclaimer(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/disclaimer.html')


def robots(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/robots.txt')


def sitemap(request):
    """
    :param request:
    :return:
    """
    return render(request, 'base/sitemap.xml')


def get_all_portfolio_detail():
    return_value = utils.get_portfolio_dashboard()
    return return_value
   
class VersionInfo(APIView):
    
    def get(self, request):
        logger = logging.getLogger('django.debug')

        try:
            version_id = request.GET.get('versionID', None)
            if version_id:
                ver = float(version_id)
                if ver >= 1.2:
                    country_phone_code = external_utils.get_country_phone_code()
                    return api_utils.response({"status": "true","country_phone_code":country_phone_code}, status.HTTP_200_OK)
                else:
                    return api_utils.response({"status": "false"}, status.HTTP_200_OK)
        except Exception as e:
            logger.debug("VersionInfo Exception: " + str(e))
        
        return api_utils.response({"message": "Bad Request"}, status.HTTP_400_BAD_REQUEST)


class DeprecateAPI(APIView):
    def generateResponse(self):
        deprecateMessage = "Please visit Play Store and update the FinAskus application to continue."
        return api_utils.response({"message": deprecateMessage, "login_error": deprecateMessage}, status.HTTP_401_UNAUTHORIZED, deprecateMessage)
        
    def post(self, request):
        return self.generateResponse()

    def get(self, request):
        return self.generateResponse()
        

class RiskProfile(APIView):
    """
    API to get risk profile
    """
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        API to get details of risk profiles
        :param request:
        :return:
        """
        risk_profiles = models.RiskProfile.objects.all().order_by('id')
        serializer = serializers.RiskProfileSerializer(risk_profiles, many=True)
        if serializer.is_valid:
            return api_utils.response(serializer.data, status.HTTP_200_OK)
        return api_utils.response(serializer.errors, status.HTTP_404_NOT_FOUND, constants.RISK_PROFILES_ERROR)

class GoalRecommendedPortfolio(APIView):
    """
    API to return the recommended portfolio for a user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, goal_type):
        """

        :param request:
        :return: overall allocation for a user and the recommended schemes for the user
        """
        goal = goals_helper.GoalBase.get_current_goal(request.user, constants.MAP[goal_type])
        if not goal:
            return api_utils.response({constants.MESSAGE: constants.USER_GOAL_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_GOAL_NOT_PRESENT)

        overall_allocation, sip_lumpsum_allocation, status_summary = utils.calculate_overall_allocation(request.user)
        
        portfolio_items, errors = utils.get_portfolio_items_per_goal(request.user, overall_allocation, goal)
        if portfolio_items is not None:
            overall_allocation.pop("summary")
            portfolio_items.update(overall_allocation)
            request.user.rebuild_portfolio = False
            request.user.save()
            msg=api_utils.response(portfolio_items, status.HTTP_200_OK)
            return msg
        else:
            return api_utils.response({constants.MESSAGE: errors},
                                      status.HTTP_400_BAD_REQUEST, api_utils.create_error_message(errors))
    
class RecommendedPortfolios(APIView):
    """
    API to return the recommended portfolio for a user
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """

        :param request:
        :return: overall allocation for a user and the recommended schemes for the user
        """
        overall_allocation, sip_lumpsum_allocation, status_summary = utils.calculate_overall_allocation(request.user)
        portfolio_items, errors = utils.get_portfolio_items(request.user.id, overall_allocation, sip_lumpsum_allocation)
        if portfolio_items is not None:
            portfolio_items.update(overall_allocation)
            request.user.rebuild_portfolio = False
            request.user.save()
            msg=api_utils.response(portfolio_items, status.HTTP_200_OK)
            return msg
        else:
            return api_utils.response({constants.MESSAGE: errors},
                                      status.HTTP_400_BAD_REQUEST, api_utils.create_error_message(errors))
        
        
             
         
class ReviewCard(APIView):
    """
    API to return the goal summary
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return: overall allocation for a user
        """
        overall_allocation, sip_lumpsum_allocation, status_summary = utils.calculate_overall_allocation(request.user)
        portfolio_items, errors = utils.get_portfolio_items(request.user.id, overall_allocation, sip_lumpsum_allocation)
        if portfolio_items is not None:
            return api_utils.response(portfolio_items, status.HTTP_200_OK)
        else:
            return api_utils.response({constants.MESSAGE: errors},
                                      status.HTTP_400_BAD_REQUEST, errors)

class ReviewCart_v3(APIView):
    """
    API to return the goal summary
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return: overall allocation for a user
        """
        overall_allocation, sip_lumpsum_allocation, status_summary = utils.calculate_overall_allocation(request.user)
        portfolio_items, errors = utils.get_portfolio_items_per_goal(request.user.id, overall_allocation)
        if portfolio_items is not None:
            return api_utils.response(portfolio_items, status.HTTP_200_OK)
        else:
            return api_utils.response({constants.MESSAGE: errors},
                                      status.HTTP_400_BAD_REQUEST, errors)

class AssessAnswer(APIView):
    """
    New API v2 to manage answers
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.AssessSerializer(data=request.data)
        if serializer.is_valid() and utils.process_assess_answer(request) is not None:
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))
        
        
class AssessAnswer_v3(APIView):
    """
    New API v3 to manage answers
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.AssessSerializer_v3(data=request.data)
        if serializer.is_valid():
            risk_score = utils.process_assess_answer(request)
            if risk_score is not None:
                return api_utils.response({"message": "success","risk_score":risk_score}, status.HTTP_200_OK)
            else:
                return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  "Unable to calculate risk score")
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))
        

class AssessAnswer_Unregistered_User_v3(APIView):
    """
    New API v3 to manage answers for non registered users
    """
    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.AssessSerializer_v3(data=request.data)
        if serializer.is_valid():
            risk_score = utils.process_assess_answer_unregistered_users(request)
            if risk_score is not None:
                return api_utils.response({"message": "success","risk_score":risk_score}, status.HTTP_200_OK)
            else:
                return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  "Unable to calculate risk score")
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))


class PlanAnswer(APIView):
    """
    Save plan data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.PlanSerializer(data=request.data)
        if serializer.is_valid() and utils.process_plan_answer(request):
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))


class TaxAnswer(APIView):
    """
    Save tax data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.TaxSerializer(data=request.data)
        if serializer.is_valid():
            goal_object = goals_helper.TaxGoal()
            is_error, errors = goal_object.create_or_update_goal(request.user, serializer.data, None, request.data.get('goal_name')) 
    
            if is_error:
                return api_utils.response({constants.MESSAGE: errors}, status.HTTP_400_BAD_REQUEST,
                                          api_utils.create_error_message(errors))
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))


class LiquidAnswer(APIView):
    """
    Save Liquid data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.LiquidSerializer(data=request.data)
        if serializer.is_valid():
            goal_object = goals_helper.LiquidGoal()
            is_error, errors = goal_object.create_or_update_goal(request.user, serializer.data, None, request.data.get('goal_name')) 
    
            if is_error:
                return api_utils.response({constants.MESSAGE: errors}, status.HTTP_400_BAD_REQUEST,
                                          api_utils.create_error_message(errors))
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))




class RetirementAnswer(APIView):
    """
    Save retirement data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.RetirementSerializer(data=request.data)
        if serializer.is_valid():
            goal_object = goals_helper.RetirementGoal()
            is_error, errors = goal_object.create_or_update_goal(request.user, serializer.data, None, request.data.get('goal_name')) 
            if is_error:
                return api_utils.response({constants.MESSAGE: errors}, status.HTTP_400_BAD_REQUEST,
                                          api_utils.create_error_message(errors))
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))


class GenericGoalAnswer(APIView):
    """
    Save generic goal data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, goal_type):
        """

        :param request:
        :param type: the category for which answers ar being stored
        :return: a success or error message
        """
        serializer = serializers.GenericGoalSerializer(data=request.data)
        if serializer.is_valid():
            goal_object = goals_helper.GenericGoal()
            is_error, errors = goal_object.create_or_update_goal(request.user, serializer.data, goal_type, request.data.get('goal_name')) 
            if is_error:
                return api_utils.response({constants.MESSAGE: errors}, status.HTTP_400_BAD_REQUEST,
                                          api_utils.create_error_message(errors))
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))


class InvestAnswer(APIView):
    """
    Save invest data
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        API to save answer for a particular question
        :param request:
        :return:
        """
        serializer = serializers.InvestSerializer(data=request.data)
        if serializer.is_valid():
            goal_object = goals_helper.QuickInvestGoal()
            is_error, errors = goal_object.create_or_update_goal(request.user, serializer.data, None, request.data.get('goal_name')) 
            if is_error:
                return api_utils.response({constants.MESSAGE: errors}, status.HTTP_400_BAD_REQUEST,
                                          api_utils.create_error_message(errors))
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                  generate_error_message(serializer.errors))


class SwapFunds(APIView):
    """
    An api to swap funds for portfolio
    """
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):
        """
        To change the portfolio items funds
        :param request:
        :return:
        """
        real_fund = request.data.get("real_fund", None)
        swapped_fund = request.data.get("swapped_fund", None)
        try:
            user_portfolio_item = models.PortfolioItem.objects.get(fund=real_fund, portfolio__user=request.user,
                                                                   portfolio__has_invested=False)
        except models.PortfolioItem.DoesNotExist:
            return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                      constants.FUND_NOT_IN_PORTFOLIO)
        try:
            models.PortfolioItem.objects.get(fund=swapped_fund, portfolio__user=request.user,
                                             portfolio__has_invested=False)
            return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                      constants.FUND_ALREADY_IN_PORTFOLIO)
        except models.PortfolioItem.DoesNotExist:
            pass
        try:
            swapped_fund_object = models.Fund.objects.get(id=swapped_fund)
        except models.Fund.DoesNotExist:
            return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST, constants.NO_SUCH_FUND)

        if user_portfolio_item.sip != 0 and user_portfolio_item.sip < swapped_fund_object.minimum_sip_investment:
            return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST, constants.MINIMUM_SIP_ERROR)

        if user_portfolio_item.lumpsum !=0 and user_portfolio_item.lumpsum < swapped_fund_object.minimum_investment:
            return api_utils.response({"message": "error"}, status.HTTP_400_BAD_REQUEST,
                                      constants.MINIMUM_LUMPSUM_ERROR)

        serializer = serializers.SwapFundsSerializer(user_portfolio_item, data=request.data)
        if serializer.is_valid():
            user_portfolio_item.fund_id = swapped_fund
            # TODO: change yesterday gain function debt funds have it store a x and equity funds at y thus need to
            # figure out later
            user_portfolio_item.save()
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(serializer.errors))


class SchemaFactSheet(APIView):
    """
    API to return data for schema fact sheet
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, fund_id):
        """
        Returns data for schema factsheet
        :param request:
        :param fund_id: the id of fund we will return data for
        :return: a dictionary of all data related to that fund
        """
        fact_sheet = {}
        fund = models.Fund.objects.get(id=fund_id)
        monthly_data_points = models.FundDataPointsChangeMonthly.objects.get(fund=fund_id)
        daily_data_points = models.FundDataPointsChangeDaily.objects.get(fund=fund_id)
        fact_sheet[constants.SCHEME_DETAILS] = utils.get_scheme_details(fund, monthly_data_points, daily_data_points)
        fact_sheet[constants.TYPE_OF_FUND] = constants.FUND_MAP_REVERSE[fund.type_of_fund]
        fact_sheet[constants.ANALYSIS] = fund.analysis
        key_performance, investment_strategy = utils.get_key_performance(fund, monthly_data_points, daily_data_points)
        fact_sheet[constants.KEY_PERFORMANCE] = key_performance
        fact_sheet[constants.INVESTMENT_STRATEGY] = investment_strategy
        if fund.type_of_fund == constants.FUND_MAP[constants.DEBT]:
            debt_data_points = models.DebtFunds.objects.get(fund=fund_id)
            fact_sheet[constants.PORTFOLIO] = utils.get_debt_portfolio(debt_data_points)
            return api_utils.response(fact_sheet, status.HTTP_200_OK)
        else:
            equity_data_points = models.EquityFunds.objects.get(fund=fund_id)
            sector_data_points = models.TopThreeSectors.objects.get(equity_fund_id=equity_data_points.id)
            fact_sheet[constants.PORTFOLIO] = utils.get_equity_portfolio(equity_data_points, sector_data_points)
            return api_utils.response(fact_sheet, status.HTTP_200_OK)


class SaveEmail(APIView):
    """
    API to save email if someone enters on finaskus website
    """

    def post(self, request):
        """
        saves email of user entered on finaskus website
        :param request:
        :return: success code if email is saved or bad request error if email was in wrong format
        """
        serializer = serializers.UserEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return api_utils.response({"message": "success"}, status.HTTP_200_OK)
        return WebResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundsDividedIntoCategories(APIView):
    """
    API to return funds divided into equity, elss and debt each having two subsections -
    other recommended and those in user portfolio items
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Returns the funds clubbed according to their type(elss, debt or equity)
        :param request:
        :return: serialized data of all funds
        """
        funds_divided = {}
        # get funds for each category via utility
        equity_funds, debt_funds, elss_funds, user_equity_funds, user_debt_funds, user_elss_funds,liquid_funds,user_liquid_funds =\
            utils.get_recommended_and_scheme_funds(request.user.id)

        # function to find max allowed for each cases
        overall_allocation, sip_lumpsum_allocation, status_summary = utils.calculate_overall_allocation(request.user)
        number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip, \
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum, is_error, \
        errors,number_of_liquid_funds_by_sip, number_of_liquid_funds_by_lumpsum = utils.get_number_of_funds(sip_lumpsum_allocation)

        # serializes all categories of funds
        user_equity_fund = serializers.FundSerializerForFundDividedIntoCategory(user_equity_funds, many=True)
        equity_fund = serializers.FundSerializerForFundDividedIntoCategory(equity_funds, many=True)
        debt_fund = serializers.FundSerializerForFundDividedIntoCategory(debt_funds, many=True)
        user_debt_fund = serializers.FundSerializerForFundDividedIntoCategory(user_debt_funds, many=True)
        elss_fund = serializers.FundSerializerForFundDividedIntoCategory(elss_funds, many=True)
        user_elss_fund = serializers.FundSerializerForFundDividedIntoCategory(user_elss_funds, many=True)
        liquid_fund = serializers.FundSerializerForFundDividedIntoCategory(liquid_funds, many=True)
        user_liquid_fund = serializers.FundSerializerForFundDividedIntoCategory(user_liquid_funds, many=True)
        # if serializers are valid return funds_divided else return serializer errors
        if equity_fund.is_valid and debt_fund.is_valid and elss_fund.is_valid and liquid_fund.is_valid and user_elss_fund.is_valid \
            and user_debt_fund.is_valid and user_elss_fund.is_valid and user_liquid_fund.is_valid:
            funds_divided[constants.EQUITY] = {constants.SCHEME: user_equity_fund.data, constants.OTHER_RECOMMENDED: equity_fund.data}
            funds_divided[constants.DEBT] = {constants.SCHEME: user_debt_fund.data, constants.OTHER_RECOMMENDED: debt_fund.data}
            funds_divided[constants.ELSS] = {constants.SCHEME: user_elss_fund.data, constants.OTHER_RECOMMENDED: elss_fund.data}
            funds_divided[constants.LIQUID] = {constants.SCHEME: user_liquid_fund.data, constants.OTHER_RECOMMENDED: liquid_fund.data}
            funds_divided["elss_max"] = max(number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum)
            funds_divided["equity_max"] = max(number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum)
            funds_divided["debt_max"] = max(number_of_debt_funds_by_sip, number_of_debt_funds_by_lumpsum)
            funds_divided["liquid_max"] = max(number_of_liquid_funds_by_sip, number_of_liquid_funds_by_lumpsum)
            return api_utils.response(funds_divided, status.HTTP_200_OK)
        return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(equity_fund.errors))

class FundsDividedIntoCategoriesForGoal(APIView):
    """
    API to return funds divided into equity, elss and debt each having two subsections -
    other recommended and those in user portfolio items
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, goal_type):
        """
        Returns the funds clubbed according to their type(elss, debt or equity)
        :param request:
        :return: serialized data of all funds
        """
        funds_divided = {}
        
        goal = goals_helper.GoalBase.get_current_goal(request.user, constants.MAP[goal_type])
        if not goal:
            return api_utils.response({constants.MESSAGE: constants.USER_GOAL_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_GOAL_NOT_PRESENT)

        # get funds for each category via utility
        equity_funds, debt_funds, elss_funds, user_equity_funds, user_debt_funds, user_elss_funds =\
            utils.get_recommended_and_scheme_funds(request.user.id, goal)

        # function to find max allowed for each cases
        sip_lumpsum_allocation = utils.get_sip_lumpsum_for_goal(request.user, goal).allocation
        number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip, \
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum, is_error, \
        errors = utils.get_number_of_funds(sip_lumpsum_allocation)

        # serializes all categories of funds
        user_equity_fund = serializers.FundSerializerForFundDividedIntoCategory(user_equity_funds, many=True)
        equity_fund = serializers.FundSerializerForFundDividedIntoCategory(equity_funds, many=True)
        debt_fund = serializers.FundSerializerForFundDividedIntoCategory(debt_funds, many=True)
        user_debt_fund = serializers.FundSerializerForFundDividedIntoCategory(user_debt_funds, many=True)
        elss_fund = serializers.FundSerializerForFundDividedIntoCategory(elss_funds, many=True)
        user_elss_fund = serializers.FundSerializerForFundDividedIntoCategory(user_elss_funds, many=True)
        # if serializers are valid return funds_divided else return serializer errors
        if equity_fund.is_valid and debt_fund.is_valid and elss_fund.is_valid and user_elss_fund.is_valid \
            and user_debt_fund.is_valid and user_elss_fund.is_valid:
            funds_divided[constants.EQUITY] = {constants.SCHEME: user_equity_fund.data, constants.OTHER_RECOMMENDED: equity_fund.data}
            funds_divided[constants.DEBT] = {constants.SCHEME: user_debt_fund.data, constants.OTHER_RECOMMENDED: debt_fund.data}
            funds_divided[constants.ELSS] = {constants.SCHEME: user_elss_fund.data, constants.OTHER_RECOMMENDED: elss_fund.data}
            funds_divided["elss_max"] = max(number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum)
            funds_divided["equity_max"] = max(number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum)
            funds_divided["debt_max"] = max(number_of_debt_funds_by_sip, number_of_debt_funds_by_lumpsum)
            return api_utils.response(funds_divided, status.HTTP_200_OK)
        return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(equity_fund.errors))
    
class FundsComparedData(APIView):
    """
    API o return data for fund comaprison.
    All the funds have o be of same type(elss, equity or debt)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        Returns the data for fund comparison in two categories -
        - compared fund
        - elss/debt/equity data(category related fund)
        :param request:
        :return:
        """
        flag, compared_funds_data = utils.get_compared_data(request.data['fund_ids'])
        if flag:
            return api_utils.response(compared_funds_data, status.HTTP_200_OK)
        else:
            return api_utils.response({constants.FUND_TYPES_NOT_SAME}, status.HTTP_400_BAD_REQUEST,
                                      constants.FUND_TYPES_NOT_SAME)


class PortfolioPerformance(APIView):
    """
    API to return data for portfolio performance 1, 3, 5 year annualized returns
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Calculates and returns portfolio performance over 1 year, 2 year and 3 years
        :param request:
        :return:
        """
        try:
            portfolio = models.Portfolio.objects.get(user_id=request.user, has_invested=False)
        except models.Portfolio.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)
        portfolio_items = models.PortfolioItem.objects.filter(portfolio=portfolio).order_by('fund_id')
        portfolio_items_fund_ids = [portfolio_item.fund_id for portfolio_item in portfolio_items]
        latest_date = funds_helper.FundsHelper.get_latest_nav_date_for_funds()
        latest_dashboard_date = funds_helper.FundsHelper.get_dashboard_change_date()
        if latest_dashboard_date < latest_date:
            latest_date = latest_dashboard_date
        nav_dates = utils.get_dates_for_nav(latest_date)
        nav_list = models.HistoricalFundData.objects.filter(
            fund_id__in=portfolio_items_fund_ids, date__in=nav_dates).order_by('fund_id_id', '-date')
        index_id = models.Indices.objects.get(index_name=constants.INDEX_NAME).id
        nav_list_for_indices = models.HistoricalIndexData.objects.filter(
            index=index_id, date__in=nav_dates).order_by('-date').values_list(constants.NAV, flat=True)
        # get annualized returns for categories and portfolio
        annualised_returns = utils.get_annualised_return(portfolio_items, nav_list)
        annualised_returns.append(utils.get_annualised_return_for_index(nav_list_for_indices))
        return api_utils.response(annualised_returns, status.HTTP_200_OK)


class FundHistoricPerformance(APIView):
    """
    API to return historic performance of a fund and the related benchmark to that fund
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        to send historic data for funds
        """
        fund_id = request.data.get('fund_id')
        try:
            fund = models.Fund.objects.get(id=fund_id)
        except models.Fund.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.FUND_NOT_PRESENT}, status.HTTP_400_BAD_REQUEST,
                                      constants.FUND_NOT_PRESENT)
        latest_date = utils.get_latest_date()
        start_dates, is_modified, message = utils.get_start_date([fund], fund.mapped_benchmark.index_name, latest_date)
        historic_data = {'five_year': utils.get_fund_historic_data([fund], start_dates[0], latest_date, True,
                                                                   fund.mapped_benchmark.index_name, fund.category_code)}
        historic_data.update({'three_year': utils.get_fund_historic_data([fund], start_dates[1], latest_date, True,
                                                                         fund.mapped_benchmark.index_name,
                                                                         fund.category_code)})
        historic_data.update({'one_year': utils.get_fund_historic_data([fund], start_dates[2], latest_date, True,
                                                                       fund.mapped_benchmark.index_name,
                                                                       fund.category_code)})
        historic_data.update({'one_month': utils.get_fund_historic_data([fund], start_dates[4], latest_date, True,
                                                                        fund.mapped_benchmark.index_name,
                                                                        fund.category_code)})
        historic_data.update({'three_month': utils.get_fund_historic_data([fund], start_dates[3], latest_date, True,
                                                                          fund.mapped_benchmark.index_name,
                                                                          fund.category_code)})
        historic_data.update({'is_modified': is_modified})
        historic_data.update({'message': message})
        return api_utils.response(historic_data, status.HTTP_200_OK)


class FundsHistoricComparison(APIView):
    """
    API to return historic performance of a fund and the related benchmark to that fund
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        to send historic data for funds
        """
        fund_id_list = request.data.get(constants.FUND_ID_LIST)
        funds = models.Fund.objects.filter(id__in=fund_id_list)
        if len(funds) < len(fund_id_list):
            return api_utils.response({constants.MESSAGE: constants.FUND_LIST_INCORRECT}, status.HTTP_400_BAD_REQUEST,
                                      constants.FUND_LIST_INCORRECT)
        latest_date = utils.get_latest_date()
        start_dates, is_modified, message = utils.get_start_date(funds, constants.INDEX_NAME, latest_date)
        historic_data = {'five_year': utils.get_fund_historic_data(funds, start_dates[0], latest_date)}
        historic_data.update({'three_year': utils.get_fund_historic_data(funds, start_dates[1], latest_date)})
        historic_data.update({'one_year': utils.get_fund_historic_data(funds, start_dates[2], latest_date)})
        historic_data.update({'one_month': utils.get_fund_historic_data(funds, start_dates[4], latest_date)})
        historic_data.update({'three_month': utils.get_fund_historic_data(funds, start_dates[3], latest_date)})
        historic_data.update({'is_modified': is_modified})
        historic_data.update({'message': message})
        return api_utils.response(historic_data, status.HTTP_200_OK)


class BilldeskComplete(APIView):
    """
    API to return the goal summary
    """
    def create_query_params(self, dict):
        """
        :param dict:
        :return:
        """
        qdict = QueryDict('',mutable=True)
        qdict.update(dict)
        return qdict.urlencode()

    def post(self, request):
        """
        :param request:
        :return: demo message
        """
        logger = logging.getLogger('django.info')
        logger.info(request)
        logger.info(request.data)
        # msg =  [
        # "FINASKUS|76|FIDB4397665607|86815116|00000002.00|IDB|NA|01|INR|DIRECT|NA|NA|NA|04-04-2016 18:56:23|0300|NA|NA|NA|ARN-87554|BSE-NA|LIQUID|RESIDENT-BSE-NA-L-NA-NA|1459776388435-2.00-0.00|NA|Y|C3742EAC9CEA6C9D086A1DD37CCDCB2FFA8DA23D197971A45720B90E1ECC5B72"
        # ]
        # msg = msg[0]
        msg = request.data.get('msg',[])
        order_id, ref_no, txn_amount, auth_status, txn_time  = billdesk.parse_billdesk_response(msg)
        txn_time_dt = None
        if txn_time:
            try:
                txn_time_dt = datetime.strptime(txn_time, '%d-%m-%Y %H:%M:%S')
            except:
                logger.info("Billdesk response: Error parsing transaction time: " + txn_time)
        if billdesk.verify_billdesk_checksum(msg):
            if auth_status == "0399":
                txn = billdesk.update_transaction_failure(order_id, ref_no, float(txn_amount), auth_status, msg, txn_time_dt)
                query_params = {"txn_amount" :txn_amount, "auth_status": auth_status, "order_id": ref_no,
                                "message" : msg.split("|")[24] # as error message is the 24th pipe seperated in the string
                                }
                query_params_string = self.create_query_params(query_params)
                full_url = reverse("api_urls:core_urls:billdesk-fail") + "?" + query_params_string
            
            elif auth_status == "0300":
                txn = billdesk.update_transaction_success(order_id, ref_no, float(txn_amount), auth_status, msg, txn_time_dt)
                active_exchange_vendor = external_helpers.get_exchange_vendor_helper().get_active_vendor()
                utils.convert_to_investor(txn, active_exchange_vendor)
                query_params = {"txn_amount" :txn_amount, "auth_status": auth_status, "order_id": ref_no,
                                "message": "Payment successful"}
                query_params_string = self.create_query_params(query_params)
                full_url = reverse("api_urls:core_urls:billdesk-success") + "?" + query_params_string
            
            else:
                txn = billdesk.update_transaction_ongoing(order_id, ref_no, float(txn_amount), auth_status, msg, txn_time_dt)
                query_params = {"txn_amount" :txn_amount, "auth_status": auth_status, "order_id": ref_no,
                                "message" : msg.split("|")[24] # as error message is the 24th pipe seperated in the string
                                }
                query_params_string = self.create_query_params(query_params)
                full_url = reverse("api_urls:core_urls:billdesk-ongoing") + "?" + query_params_string
                
        else:
            txn = billdesk.update_transaction_checksum_failure(order_id, ref_no, float(txn_amount), auth_status, msg, txn_time_dt)
            query_params = {"txn_amount" :txn_amount, "auth_status": auth_status, "order_id": ref_no,
                                "message" : msg.split("|")[24] # as error message is the 24th pipe seperated in the string
                                }
            query_params_string = self.create_query_params(query_params)
            full_url = reverse("api_urls:core_urls:billdesk-fail") + "?" + query_params_string
            
        return HttpResponseRedirect(full_url)


class Billdesk(APIView):
    """
    API to return the goal summary
    """
    def get(self, request):
        """
        :param request:
        :return: demo message
        """
        return render(request, 'base/billdesk_status.html')


class PopularFunds(APIView):
    """
    API to return most popular funds of among the funds
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :returns: a list of most popular funds of among all the funds
        """
        popular_funds = eval(models.CachedData.objects.get(key=constants.MOST_POPULAR_FUND).value[
                               constants.MOST_POPULAR_FUND])
        return api_utils.response(popular_funds, status.HTTP_200_OK)


class PortfolioHistoricPerformance(APIView):
    """
    API to send historic performance of Portfolio
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        portfolio_items = models.PortfolioItem.objects.filter(portfolio__user=request.user,
                                                              portfolio__has_invested=False).select_related('portfolio')
        if len(portfolio_items) == 0:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)
        portfolio_funds = [portfolio_item.fund for portfolio_item in portfolio_items]
        latest_date = funds_helper.FundsHelper.get_latest_nav_date_for_funds()
        historic_data = {
            'five_year':
                utils.get_portfolio_historic_data(utils.get_fund_historic_data(
                    portfolio_funds, latest_date - relativedelta(years=5), latest_date, False), portfolio_items)}
        historic_data.update({
            'three_year':
                utils.get_portfolio_historic_data(utils.get_fund_historic_data(
                    portfolio_funds, latest_date - relativedelta(years=3), latest_date, False), portfolio_items)})
        historic_data.update({
            'one_year':
                utils.get_portfolio_historic_data(utils.get_fund_historic_data(
                    portfolio_funds, latest_date - relativedelta(years=1), latest_date, False), portfolio_items)})
        historic_data.update({
            'one_month':
                utils.get_portfolio_historic_data(utils.get_fund_historic_data(
                    portfolio_funds, latest_date - relativedelta(months=1), latest_date, False), portfolio_items)})
        historic_data.update({
            'three_month':
                utils.get_portfolio_historic_data(utils.get_fund_historic_data(
                    portfolio_funds, latest_date - relativedelta(months=3), latest_date, False), portfolio_items)})
        historic_data.update({'is_modified': False})
        historic_data.update({'message': ''})
        return api_utils.response(historic_data, status.HTTP_200_OK)


class LeaderBoard(APIView):
    """

    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        returns the leaderboard ranking

        Top 10 investors according to the filter value.

        income legend:
        ---------------------------------
        (constants.LEVEL_1, '< 1 Lakh'),
        (constants.LEVEL_2, '1-5 Lakhs'),
        (constants.LEVEL_3, '5-10 Lakhs'),
        (constants.LEVEL_4, '10-25 Lakhs'),
        (constants.LEVEL_5, '25-100 Lakhs'),
        (constants.LEVEL_6, '> 100 Lakhs')

        occupations_legend:
        ------------------------------------
        '3' Salaried:
                Private Sector Service
                Public Sector Service
                Government Service
        '0' Self-Employed:
                Business
                Professional (Self-Employed)
                Agriculturist
                Forex Dealer
        '1' Retired:
                Retired
        '2' Housewife/Other:
                Housewife
                Student
                Other (please specify)

        sample data:
        {
          "lage": 20,
          "hage": 40,
          "lsal": "0",
          "hsal": "4",
          "lscore": 6,
          "hscore": 8,
          "gender": "M",
          "occupation_choice": 0
        }

        :param request:
        :return:
        """

        leader_list = None

        occupation_choices = {0: [cons.BUSINESS, cons.PROFESSIONAL, cons.AGRICULTURE, cons.FOREX_DEALER],
                              1: [cons.RETIRED, ],
                              2: [cons.HOUSEWIFE, cons.STUDENT, cons.OTHER],
                              3: [cons.PRIVATE_SECTOR, cons.PUBLIC_SECTOR, cons.GOVERNMENT]}

        lage = request.data.get('lage', constants.DEFAULT_LOW_AGE)
        hage = request.data.get('hage', constants.DEFAULT_HIGH_AGE)
        sal = request.data.get('sal', constants.DEFAULT_SAL)
        lscore = request.data.get('lscore', constants.DEFAULT_LOW_SCORE)
        hscore = request.data.get('hscore', constants.DEFAULT_HIGH_SCORE)
        gender = request.data.get('gender', constants.DEFAULT_GENDER)
        occupation_choice = request.data.get('occupation_choice', constants.DEFAULT_OCCUPATION)
        date_choice = request.data.get('date_choice',None)  # date params

        try:
            investor_portfolio = profile_models.AggregatePortfolio.objects.get(user=request.user)
            print (request.user)
        except profile_models.AggregatePortfolio.DoesNotExist:
            portfolio = models.Portfolio.objects.get(user=request.user, has_invested=False)
            fund_data = utils.get_all_fund_data(request.user)
            try:
                cashflows, final_amount, total_cashflow = utils.xirr_calculation(
                    fund_data, portfolio.created_at.date(), datetime.now().date())
                print(cashflows)
                total_xirr = new_xirr.new_xirr(cashflows)
            except Exception as e:
                print("XIRR failed for following input")
                total_xirr = 0.00

            total_xirr = 0.0 if type(total_xirr) == complex else total_xirr * 100
            investor_portfolio, created = profile_models.AggregatePortfolio.objects.update_or_create(user=request.user,
                                 defaults = {"total_xirr":round(total_xirr, 1), "update_date":datetime.now().date()})

        query = {}
        if lage != constants.DEFAULT_LOW_AGE:
            query["user__age__gte"] =  lage
        if hage != constants.DEFAULT_HIGH_AGE:
            query["user__age__lte"] = hage
        if lscore != constants.DEFAULT_LOW_SCORE:
            query["user__risk_score__gte"] = lscore
        if hscore != constants.DEFAULT_HIGH_SCORE:
            query["user__risk_score__lte"] =  hscore
        if gender != constants.DEFAULT_GENDER:
            query["user__gender"] = gender
        if sal != constants.DEFAULT_SAL:
            query["user__investorinfo__income"] = sal
        """  
        Adding date filter to the leader board filter
        """ 
        if date_choice != constants.FILTER_DATE_NOT_SELECTED  and date_choice is not None:
        
            hdate = datetime.now()

            if date_choice == constants.FILTER_DATE_ONE_WEEK:
                ldate = hdate - timedelta(days=7)
            
            elif date_choice == constants.FILTER_DATE_ONE_MONTH:
                ldate = hdate - relativedelta(months=1)
            
            elif date_choice == constants.FILTER_DATE_THREE_MONTH:
                ldate = hdate - relativedelta(months=3)
            
            if ldate is not None and hdate is not None:   
                portfolios = models.Portfolio.objects.filter(investment_date__lte = ldate).values('user').annotate(count = Count('user'))  
                users =[]
                for portfolio in portfolios:
                    users.append(portfolio['user'])
                query["user_id__in"] = users

        if occupation_choice != constants.DEFAULT_OCCUPATION:
            if type(occupation_choice) == list:
                occupation = []
                for occ in occupation_choice:
                    occupation += occupation_choices[occ]
            else:
                occupation = occupation_choices[occupation_choice]
            query["user__investorinfo__occupation_type__in"] = occupation
            

        leader_list = profile_models.AggregatePortfolio.objects.filter(**query).order_by('-total_xirr')

        if len(leader_list) > 10:
            leader_list = leader_list[:10]
        leader_list_serializer = serializers.LeaderBoardSerializer(leader_list, many=True)
        leader_board_investor = serializers.LeaderBoardUserSerializer(investor_portfolio)
        return_data = dict()
        if leader_list_serializer.is_valid:
            return_data["top_ten"] = leader_list_serializer.data
            return_data["investor"] = leader_board_investor.data
            return api_utils.response(return_data, status.HTTP_200_OK)
        return api_utils.response({}, status.HTTP_400_BAD_REQUEST)


# class GetGoals(APIView):
#     """
#     API to get goals for redemption
#     """
#     permission_classes = [permissions.IsAuthenticated]
#
#     def get(self, request):
#         """
#
#         :param request:
#         :return: the goals of the user
#         """
#         answers = models.Answer.objects.filter(user=request.user).select_related("question")
#         goals = set()
#         for answer in answers:
#             goals.add(constants.CATEGORY_CHOICE_REVERSE[answer.question.question_for])
#         return api_utils.response(goals, status.HTTP_200_OK)


class GetInvestedFundReturn(APIView):
    """
    API to get fund name and return value
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:the return value of fund
        """
        fund_order_items = models.FundOrderItem.objects.filter(portfolio_item__portfolio__user=request.user,
            portfolio_item__portfolio__has_invested=True, portfolio_item__portfolio__is_deleted=False, is_verified=True,
            is_cancelled=False).distinct('portfolio_item').select_related('portfolio_item')
        portfolio_items = [fund_order_item.portfolio_item for fund_order_item in fund_order_items]
        equity_funds, debt_funds, elss_funds, liquid_funds = [], [], [],[]
        equity_funds_id, debt_funds_id, elss_funds_id, liquid_funds_id= [], [], [],[]
        for portfolio_item in portfolio_items:
            if portfolio_item.fund.type_of_fund == 'E':
                if(portfolio_item.fund.id in equity_funds_id):
                    equity_funds = utils.update_funds_list(equity_funds, portfolio_item)
                else:
                    equity_funds.append(utils.get_fund_detail(portfolio_item))
                    equity_funds_id.append(portfolio_item.fund.id)
            elif portfolio_item.fund.type_of_fund == 'D':
                if(portfolio_item.fund.id in debt_funds_id):
                    debt_funds = utils.update_funds_list(debt_funds, portfolio_item)
                else:
                    debt_funds.append(utils.get_fund_detail(portfolio_item))
                    debt_funds_id.append(portfolio_item.fund.id)
            elif portfolio_item.fund.type_of_fund == 'T':
                if(portfolio_item.fund.id in elss_funds_id):
                    elss_funds = utils.update_funds_list(elss_funds, portfolio_item)
                else:
                    elss_funds.append(utils.get_fund_detail(portfolio_item))
                    elss_funds_id.append(portfolio_item.fund.id)
            elif portfolio_item.fund.type_of_fund == 'L':
                if(portfolio_item.fund.id in liquid_funds_id):
                    liquid_funds = utils.update_funds_list(liquid_funds, portfolio_item)
                else:
                    liquid_funds.append(utils.get_fund_detail(portfolio_item))
                    liquid_funds_id.append(portfolio_item.fund.id)
        invested_fund_return = [{"key": constants.EQUITY, "value": equity_funds},
                                {"key": constants.DEBT, "value": debt_funds},
                                {"key": constants.ELSS, "value": elss_funds},
                                {"key": constants.LIQUID, "value": liquid_funds}
                                ]

        invested_fund_return_new = copy.deepcopy(invested_fund_return)
        for index in range(3):
            for fund_object in invested_fund_return[index][constants.VALUE]:
                if utils.find_if_not_eligible_for_display(fund_object, request.user):
                    invested_fund_return_new[index][constants.VALUE].remove(fund_object)
        return api_utils.response(invested_fund_return_new, status.HTTP_200_OK)

class GetInvestedFundReturn_v3(APIView):
    """
    API to get fund name and return value
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:the return value of fund
        """
        user_goals = goals_helper.GoalBase.get_invested_goals(request.user)
        if not user_goals:
            api_utils.response({}, status.HTTP_400_BAD_REQUEST)
        
        goal_fund_data = []
        for goal in user_goals:
            equity_funds, debt_funds, elss_funds = [], [], []
            for portfolio_item in goal.portfolioitem_set.all(): #TODO subquery for valid foi
                fund_order_item_count = models.FundOrderItem.objects.filter(portfolio_item=portfolio_item, is_verified=True, is_cancelled=False).count()
                if fund_order_item_count > 0:
                    if portfolio_item.fund.type_of_fund == 'E':
                        equity_funds.append(utils.get_fund_detail(portfolio_item))
                    elif portfolio_item.fund.type_of_fund == 'D':
                        debt_funds.append(utils.get_fund_detail(portfolio_item))
                    elif portfolio_item.fund.type_of_fund == 'T':
                        elss_funds.append(utils.get_fund_detail(portfolio_item))
            
            invested_fund_return = [{"key": constants.EQUITY, "value": equity_funds},
                        {"key": constants.DEBT, "value": debt_funds},
                        {"key": constants.ELSS, "value": elss_funds}]

            invested_fund_return_new = copy.deepcopy(invested_fund_return)
            for index in range(3):
                for fund_object in invested_fund_return[index][constants.VALUE]:
                    if utils.find_if_not_eligible_for_display(fund_object, request.user):
                        invested_fund_return_new[index][constants.VALUE].remove(fund_object)
         
            if len(invested_fund_return_new[0][constants.VALUE]) > 0  or len(invested_fund_return_new[1][constants.VALUE]) > 0 or len(invested_fund_return_new[2][constants.VALUE]) > 0:
                goal_data = {"goal_id": goal.id, "goal_name": goal.name, 
                             "investment_date": goal.portfolio.investment_date.strftime('%d-%m-%y'),
                             "funds": invested_fund_return_new}
                goal_fund_data.append(goal_data)
                                                      
        return api_utils.response(goal_fund_data, status.HTTP_200_OK)

class TransactionDetail(APIView):
    """
    API to get details of previous redemption
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """

        :param request:
        :return:the detail of previous redemption
        """
        redeem_data = []
        redeem_details = models.RedeemDetail.objects.filter(user=request.user).prefetch_related('fund_redeem_items')
        for redeem_detail in redeem_details:
            equity_funds = []
            debt_funds = []
            elss_funds = []
            liquid_funds = []
            for item in redeem_detail.fund_redeem_items.all():
                fund_redeem_items = models.FundRedeemItem.objects.filter(id=item.id).select_related('portfolio_item')
                for fund_redeem_item in fund_redeem_items:
                    if fund_redeem_item.portfolio_item.fund.type_of_fund == 'E':
                        equity_funds.append(utils.get_redeem_fund(fund_redeem_item))
                    elif fund_redeem_item.portfolio_item.fund.type_of_fund == 'D':
                        debt_funds.append(utils.get_redeem_fund(fund_redeem_item))
                    elif fund_redeem_item.portfolio_item.fund.type_of_fund == 'T':
                        elss_funds.append(utils.get_redeem_fund(fund_redeem_item))
                    elif fund_redeem_item.portfolio_item.fund.type_of_fund == 'L':
                        liquid_funds.append(utils.get_redeem_fund(fund_redeem_item))
            redeem_fund_detail = {'redeem_id': redeem_detail.redeem_id,
                                  'redeem_status': redeem_detail.redeem_status, constants.EQUITY: equity_funds,
                                  constants.DEBT: debt_funds, "ELSS": elss_funds,constants.LIQUID: liquid_funds}
            redeem_data.append(redeem_fund_detail)
        return api_utils.response(redeem_data, status.HTTP_200_OK)


class TransactionHistoryNew(APIView):
    """
    API to get details of fund order item
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:the detail of fund order items
        """
        txn_history = []
        order_details = models.OrderDetail.objects.filter(user=request.user)
        fund_order_details = models.FundOrderItem.objects.filter(
            orderdetail__in=order_details).exclude(order_amount=0).order_by('-created_at')
        order_serializer = serializers.FundOrderItemSerializer(fund_order_details, many=True)
        if order_serializer.is_valid:
            txn_history = order_serializer.data
        else:
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(order_serializer.errors))

        redeem_details = models.RedeemDetail.objects.filter(user=request.user).order_by('-created_at')
        # fund_redeem_details = models.FundRedeemItem.objects.filter(redeemdetail__in=redeem_details).order_by('-created_at')
        # redeem_serializer = serializers.FundRedeemItemSerializer(fund_redeem_details, many=True)
        redeem_serializer = serializers.RedeemDetailSerializer(redeem_details, many=True)

        if redeem_serializer.is_valid:
            txn_history += redeem_serializer.data
        else:
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(redeem_serializer.errors))

        # portfolio_items = models.PortfolioItem.objects.filter(
        #     portfolio__user=request.user, portfolio__has_invested=True, portfolio__is_deleted=False)
        fund_order_items_list = models.FundOrderItem.objects.filter(portfolio_item__portfolio__user=request.user,
            portfolio_item__portfolio__has_invested=True, portfolio_item__portfolio__is_deleted=False, is_verified=True,
            is_cancelled=False).distinct('portfolio_item').select_related('portfolio_item')
        portfolio_items = [fund_order_item.portfolio_item for fund_order_item in fund_order_items_list]
        latest_fund_order_item = []
        if portfolio_items:
            for portfolio_item in portfolio_items:
                fund_order_items = portfolio_item.fundorderitem_set.filter(is_cancelled=False, agreed_sip__gt=0).order_by('-created_at')
                for fund_order_item in fund_order_items:
                    if fund_order_item.is_future_sip_cancelled == False:
                        latest_fund_order_item.append(fund_order_item)
                    break
                    
            if len(latest_fund_order_item) > 0:
                future_fund_order_item_serializer = serializers.FutureFundOrderItemSerializer(latest_fund_order_item, many=True)

                if future_fund_order_item_serializer.is_valid:
                    txn_history += future_fund_order_item_serializer.data
                else:
                    return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(future_fund_order_item_serializer.errors))

        sorted_txn_history = sorted(txn_history, key=lambda k: k['transaction_date'], reverse=True)
        return api_utils.response(sorted_txn_history, status.HTTP_200_OK)

class TransactionHistory_v3(APIView):
    """
    API to get details of fund order item
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:the detail of fund order items
        """
        txn_history = []
        order_details = models.OrderDetail.objects.filter(user=request.user)
        fund_order_details = models.FundOrderItem.objects.filter(
            orderdetail__in=order_details).exclude(order_amount=0).order_by('-created_at')
        order_serializer = serializers.FundOrderItemSerializer_v3(fund_order_details, many=True)
        if order_serializer.is_valid:
            txn_history = order_serializer.data
        else:
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(order_serializer.errors))

        redeem_details = models.FundRedeemItem.objects.filter(portfolio_item__portfolio__user=request.user).order_by('-created_at')
        # fund_redeem_details = models.FundRedeemItem.objects.filter(redeemdetail__in=redeem_details).order_by('-created_at')
        # redeem_serializer = serializers.FundRedeemItemSerializer(fund_redeem_details, many=True)
        redeem_serializer = serializers.FundRedeemItemSerializer_v3(redeem_details, many=True)

        if redeem_serializer.is_valid:
            txn_history += redeem_serializer.data
        else:
            return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(redeem_serializer.errors))

        # portfolio_items = models.PortfolioItem.objects.filter(
        #     portfolio__user=request.user, portfolio__has_invested=True, portfolio__is_deleted=False)
        fund_order_items_list = models.FundOrderItem.objects.filter(portfolio_item__portfolio__user=request.user,
            portfolio_item__portfolio__has_invested=True, portfolio_item__portfolio__is_deleted=False, is_verified=True,
            is_cancelled=False).distinct('portfolio_item').select_related('portfolio_item')
        portfolio_items = [fund_order_item.portfolio_item for fund_order_item in fund_order_items_list]
        latest_fund_order_item = []
        if portfolio_items:
            for portfolio_item in portfolio_items:
                fund_order_items = portfolio_item.fundorderitem_set.filter(is_cancelled=False, agreed_sip__gt=0).order_by('-created_at')
                for fund_order_item in fund_order_items:
                    if fund_order_item.is_future_sip_cancelled == False:
                        latest_fund_order_item.append(fund_order_item)
                    break
                    
            if len(latest_fund_order_item) > 0:
                future_fund_order_item_serializer = serializers.FutureFundOrderItemSerializer(latest_fund_order_item, many=True)

                if future_fund_order_item_serializer.is_valid:
                    txn_history += future_fund_order_item_serializer.data
                else:
                    return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(future_fund_order_item_serializer.errors))

        sorted_txn_history = sorted(txn_history, key=lambda k: k['transaction_date'], reverse=True)
        return api_utils.response(sorted_txn_history, status.HTTP_200_OK)

class FundRedeem(APIView):
    """
    For this api the expected data structure is sent is
    {"data": [{"fund_id": 3, "redeem_amount": 1300}], "all_units":[{"fund_id": 2}]}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        """
        :param request:
        :return:
        """
        serializer = serializers.NewRedeemAddSerializer(data=request.data)
        if serializer.is_valid():
            # processes funds in data
            redeem_detail_list = utils.add_redeem_details_by_amount(request.data.get('data', []), request.user)
            # process funds in all_units
            redeem_detail_list = utils.add_redeem_details_by_units(request.data.get('all_units', []), request.user,
                                                                 redeem_detail_list)

            # creates groupedredeemdetail with redeem details created above added
            grouped_redeem_detail = models.GroupedRedeemDetail.objects.create(user=request.user)
            grouped_redeem_detail.redeem_details.add(*redeem_detail_list)

            # Sends a email informing admin of a new groupredeem item creation
            profiles_helpers.send_redeem_completed_email(grouped_redeem_detail, use_https=settings.USE_HTTPS)
            return api_utils.response({constants.MESSAGE: "success"})
        else:
            return api_utils.response({constants.MESSAGE: serializer.errors}, status.HTTP_400_BAD_REQUEST,
                                      generate_error_message(serializer.errors))

class GoalRedeem(APIView):
    """
    For this api the expected data structure is sent is
    {"data": [{"goal_id": 1, "amount" : [{"fund_id": 3, "redeem_amount": 1300}], "all_units":[{"fund_id": 2}]}]}
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self,request):
        """
        :param request:
        :return:
        """
        serializer = serializers.RedeemAddSerializer_v3(data=request.data)
        if serializer.is_valid():
            grouped_redeem_detail = utils.process_redeem_request(request.user, request.data.get('data', []))

            if grouped_redeem_detail:
                # Sends a email informing admin of a new groupredeem item creation
                profiles_helpers.send_redeem_completed_email(grouped_redeem_detail, use_https=settings.USE_HTTPS)
                return api_utils.response({constants.MESSAGE: "success"})
            else:
                return api_utils.response({}, status.HTTP_400_BAD_REQUEST)
        else:
            return api_utils.response({constants.MESSAGE: serializer.errors}, status.HTTP_400_BAD_REQUEST,
                                      generate_error_message(serializer.errors))


class DashboardPortfolioHistoricPerformance(APIView):
    """
    API for portfolio historic performance since inception for dashboard
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return: historic performance of portfolio and corresponding historic performance of
        benchmark(S&P BSE SENSEX India INR)
        """
        portfolio_items = models.PortfolioItem.objects.filter(portfolio__user=request.user).select_related('portfolio')
        if len(portfolio_items) == 0:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)
        portfolio_funds = [portfolio_item.fund for portfolio_item in portfolio_items]
        latest_date = utils.get_latest_date()
        inception_date = portfolio_items[0].portfolio.investment_date if \
            portfolio_items[0].portfolio.has_invested == True else portfolio_items[0].portfolio.created_at.date()
        if latest_date < inception_date:
            return api_utils.response({constants.PORTFOLIO: constants.EMPTY_PORTFOLIO_HISTORIC_DATA},
                                      status.HTTP_200_OK)
        portfolio_data = utils.get_portfolio_historic_data(utils.get_fund_historic_data(
            portfolio_funds, inception_date, latest_date, False), portfolio_items)
        portfolio_data.update({constants.INVESTED_VALUE: portfolio_items[0].portfolio.total_sum_invested})
        portfolio_data.update({constants.IS_EMPTY: False})
        return api_utils.response(portfolio_data, status.HTTP_200_OK)


class AnswerDelete(APIView):
    """
    API to delete a goal for a user based on the type
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, question_for):
        """
        :param request:
        :param question_for:the goal which has to be deleted
        :return:
        """
        is_last_goal = True
        current_goal = goals_helper.GoalBase.get_current_goal(request.user, constants.MAP[question_for])
        
        if current_goal:
            portfolio = current_goal.portfolio 
            current_goal.delete()
            current_goals = goals_helper.GoalBase.get_current_goals(request.user)
            
            if len(current_goals) > 0:
                is_last_goal = False
            if is_last_goal and portfolio:
                portfolio.delete()

            request.user.rebuild_portfolio = True
            request.user.save()
        return api_utils.response({constants.MESSAGE: constants.SUCCESS}, status.HTTP_200_OK)


class GetCategorySchemes(APIView):
    """
    API to reset current portfolio items of a user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        # get the category for which reset is being done
        reset = request.query_params.get('reset')
        overall_allocation, sip_lumpsum_allocation, status_summary = utils.calculate_overall_allocation(request.user)
        number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip, \
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum, is_error, \
        errors,number_of_liquid_funds_by_sip, number_of_liquid_funds_by_lumpsum = utils.get_number_of_funds(sip_lumpsum_allocation)
        RANK_MAP = {
            constants.EQUITY: max(number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum),
            constants.DEBT: max(number_of_debt_funds_by_sip, number_of_debt_funds_by_lumpsum),
            constants.ELSS: max(number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum),
            constants.LIQUID: max(number_of_liquid_funds_by_sip, number_of_liquid_funds_by_lumpsum)
        }

        for category in constants.FUND_CATEGORY_LIST:
            if reset == category:
                # serializes all categories of funds
                if reset == constants.EQUITY and RANK_MAP[reset] == constants.MAX_NUMBER_EQUITY_FUNDS:
                    
                    user_category_fund_list = utils.recommendedPortfolio_equity(reset)
                    
                else:    
                    user_category_fund_list = models.Fund.objects.filter(
                        is_enabled=True, type_of_fund=constants.FUND_MAP[reset]).order_by("fund_rank")[:RANK_MAP[reset]]
                user_category_fund_list_ids = [i.id for i in user_category_fund_list]
                other_category_fund_list = models.Fund.objects.filter(
                    type_of_fund=constants.FUND_MAP[reset]).exclude(
                    id__in=user_category_fund_list_ids).exclude(is_enabled=False).order_by('fund_rank')

                user_category_fund = serializers.FundSerializerForFundDividedIntoCategory(
                    user_category_fund_list, many=True)
                other_category_fund = serializers.FundSerializerForFundDividedIntoCategory(
                    other_category_fund_list, many=True)

                # if serializers are valid return funds_divided else return serializer errors
                if user_category_fund.is_valid and other_category_fund.is_valid:
                    funds_divided_by_category = {constants.SCHEME: user_category_fund.data,
                                                 constants.OTHER_RECOMMENDED: other_category_fund.data}
                    return api_utils.response(funds_divided_by_category, status.HTTP_200_OK)
                return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(
                    user_category_fund.errors))

class GetCategorySchemesForGoal(APIView):
    """
    API to reset current portfolio items of a user
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, goal_type):
        """
        :param request:
        :return:
        """
        
        goal = goals_helper.GoalBase.get_current_goal(request.user, constants.MAP[goal_type])
        if not goal:
            return api_utils.response({constants.MESSAGE: constants.USER_GOAL_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_GOAL_NOT_PRESENT)

        # get the category for which reset is being done
        reset = request.query_params.get('reset')
        sip_lumpsum_allocation = utils.get_sip_lumpsum_for_goal(request.user, goal).allocation
        
        number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum, number_of_debt_funds_by_sip, \
        number_of_debt_funds_by_lumpsum, number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum, is_error, \
        errors = utils.get_number_of_funds(sip_lumpsum_allocation)
        RANK_MAP = {
            constants.EQUITY: max(number_of_equity_funds_by_sip, number_of_equity_funds_by_lumpsum),
            constants.DEBT: max(number_of_debt_funds_by_sip, number_of_debt_funds_by_lumpsum),
            constants.ELSS: max(number_of_elss_funds_by_sip, number_of_elss_funds_by_lumpsum)
        }

        for category in constants.FUND_CATEGORY_LIST:
            if reset == category:
                # serializes all categories of funds
                if reset == constants.EQUITY and RANK_MAP[reset] == constants.MAX_NUMBER_EQUITY_FUNDS:
                    
                    user_category_fund_list = utils.recommendedPortfolio_equity(reset)
                    
                else:    
                    user_category_fund_list = models.Fund.objects.filter(
                        is_enabled=True, type_of_fund=constants.FUND_MAP[reset]).order_by("fund_rank")[:RANK_MAP[reset]]
                user_category_fund_list_ids = [i.id for i in user_category_fund_list]
                other_category_fund_list = models.Fund.objects.filter(
                    type_of_fund=constants.FUND_MAP[reset]).exclude(
                    id__in=user_category_fund_list_ids).exclude(is_enabled=False).order_by('fund_rank')

                user_category_fund = serializers.FundSerializerForFundDividedIntoCategory(
                    user_category_fund_list, many=True)
                other_category_fund = serializers.FundSerializerForFundDividedIntoCategory(
                    other_category_fund_list, many=True)

                # if serializers are valid return funds_divided else return serializer errors
                if user_category_fund.is_valid and other_category_fund.is_valid:
                    funds_divided_by_category = {constants.SCHEME: user_category_fund.data,
                                                 constants.OTHER_RECOMMENDED: other_category_fund.data}
                    return api_utils.response(funds_divided_by_category, status.HTTP_200_OK)
                return api_utils.response({}, status.HTTP_404_NOT_FOUND, generate_error_message(
                    user_category_fund.errors))

class ChangePortfolio(APIView):
    """
    API to change portfolio for swap funds

    Receives three lists corresponding to fund ids user want to have in his portfolio for each category.
    Based on the above three lists it deletes / replaces the funds in his portfolio.
    The number of new funds can be equal to or less than(not zero for each category if initially not zero) the number of
    funds originally present in his portfolio for each category but cannot be more than that.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """
        # check if a portfolio of user for which he has not invested is present. If not send an error message
        #print(request.data)
        #request.data['liquid'] = [27,49,53]

        try:
            user_portfolio = models.Portfolio.objects.get(user=request.user, has_invested=False)
        except models.Portfolio.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)

        # if portfolio is present get ids of new funds user wants to keep from request
        fund_id_map = {constants.EQUITY: [], constants.DEBT: [], constants.ELSS: [],constants.LIQUID: []}
        for category in constants.FUND_CATEGORY_LIST:
            fund_id_map[category] = request.data.get(category)

        # calculate sip and lumpsum for each category based on old portfolio
        category_sip_lumpsum_map = utils.calculate_sip_lumpsum_category_wise_for_a_portfolio(user_portfolio)

        if fund_id_map[constants.EQUITY]:
            if category_sip_lumpsum_map[constants.EQUITY][constants.SIP] !=0:
                defected_funds = utils.find_funds_with_sip_lower_than_minimum_sip(
                    category_sip_lumpsum_map[constants.EQUITY][constants.SIP], category_sip_lumpsum_map[constants.EQUITY][constants.SIP_COUNT], fund_id_map[constants.EQUITY])

                if defected_funds != '':
                    # string_to_return = constants.CHECK_PORTFOLIO_DISTRIBUTION_MESSAGE.format(defected_funds)
                    return api_utils.response({}, status.HTTP_400_BAD_REQUEST, defected_funds)

        # add the new funds as portfolio items and allocate them sip and lumpsum based on category_sip_lumpsum_map
        utils.change_portfolio(category_sip_lumpsum_map, user_portfolio, fund_id_map)
        return api_utils.response({constants.MESSAGE: constants.SUCCESS}, status.HTTP_200_OK)

class ChangeGoalPortfolio(APIView):
    """
    API to change portfolio for swap funds

    Receives three lists corresponding to fund ids user want to have in his portfolio for each category.
    Based on the above three lists it deletes / replaces the funds in his portfolio.
    The number of new funds can be equal to or less than(not zero for each category if initially not zero) the number of
    funds originally present in his portfolio for each category but cannot be more than that.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, goal_type):
        """
        :param request:
        :return:
        """
        # check if a portfolio of user for which he has not invested is present. If not send an error message
        try:
            user_portfolio = models.Portfolio.objects.get(user=request.user, has_invested=False)
        except models.Portfolio.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)

        goal = goals_helper.GoalBase.get_current_goal(request.user, constants.MAP[goal_type])
        if not goal:
            return api_utils.response({constants.MESSAGE: constants.USER_GOAL_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_GOAL_NOT_PRESENT)

        # if portfolio is present get ids of new funds user wants to keep from request
        fund_id_map = {constants.EQUITY: [], constants.DEBT: [], constants.ELSS: []}
        for category in constants.FUND_CATEGORY_LIST:
            fund_id_map[category] = request.data.get(category)

        
        # calculate sip and lumpsum for each category based on old portfolio
        category_sip_lumpsum_map = utils.calculate_sip_lumpsum_category_wise_for_a_portfolio(user_portfolio, goal)

        if fund_id_map[constants.EQUITY]:
            if category_sip_lumpsum_map[constants.EQUITY][constants.SIP] !=0:
                defected_funds = utils.find_funds_with_sip_lower_than_minimum_sip(
                    category_sip_lumpsum_map[constants.EQUITY][constants.SIP], category_sip_lumpsum_map[constants.EQUITY][constants.SIP_COUNT], fund_id_map[constants.EQUITY])

                if defected_funds != '':
                    # string_to_return = constants.CHECK_PORTFOLIO_DISTRIBUTION_MESSAGE.format(defected_funds)
                    return api_utils.response({}, status.HTTP_400_BAD_REQUEST, defected_funds)

        # add the new funds as portfolio items and allocate them sip and lumpsum based on category_sip_lumpsum_map
        utils.change_portfolio(category_sip_lumpsum_map, user_portfolio, fund_id_map, goal)
        return api_utils.response({constants.MESSAGE: constants.SUCCESS}, status.HTTP_200_OK)

class FundsDistributionValidate(APIView):
    """
    API to check if funds distribution is valid.
    The sip allotted to each fund should be more than or equal to its minimum sip amount
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        :param request:
        :return:
        """

        # check if a portfolio of user for which he has not invested is present. If not send an error message
        try:
            user_portfolio = models.Portfolio.objects.get(user=request.user, has_invested=False)
        except models.Portfolio.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)

        # ids of funds selected by user
        equity_funds = request.data.get(constants.EQUITY)

        # calculate sip and lumpsum for each category based on old portfolio
        category_sip_lumpsum_map = utils.calculate_sip_lumpsum_category_wise_for_a_portfolio(user_portfolio)
        if equity_funds:
            if category_sip_lumpsum_map[constants.EQUITY][constants.SIP] !=0:
                defected_funds = utils.find_funds_with_sip_lower_than_minimum_sip(
                    category_sip_lumpsum_map[constants.EQUITY][constants.SIP], category_sip_lumpsum_map[constants.EQUITY][constants.SIP_COUNT], equity_funds)

                if defected_funds != '':
                    # string_to_return = constants.CHECK_PORTFOLIO_DISTRIBUTION_MESSAGE.format(defected_funds)
                    return api_utils.response({'valid': False}, status.HTTP_400_BAD_REQUEST, defected_funds)
        return api_utils.response({'valid': True}, status.HTTP_200_OK)

class FundsDistributionValidateForGoal(APIView):
    """
    API to check if funds distribution is valid.
    The sip allotted to each fund should be more than or equal to its minimum sip amount
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, goal_type):
        """
        :param request:
        :return:
        """

        # check if a portfolio of user for which he has not invested is present. If not send an error message
        try:
            user_portfolio = models.Portfolio.objects.get(user=request.user, has_invested=False)
        except models.Portfolio.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)

        goal = goals_helper.GoalBase.get_current_goal(request.user, constants.MAP[goal_type])
        if not goal:
            return api_utils.response({constants.MESSAGE: constants.USER_GOAL_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_GOAL_NOT_PRESENT)

        # ids of funds selected by user
        equity_funds = request.data.get(constants.EQUITY)

        # calculate sip and lumpsum for each category based on old portfolio
        category_sip_lumpsum_map = utils.calculate_sip_lumpsum_category_wise_for_a_portfolio(user_portfolio, goal)
        if equity_funds:
            if category_sip_lumpsum_map[constants.EQUITY][constants.SIP] !=0:
                defected_funds = utils.find_funds_with_sip_lower_than_minimum_sip(
                    category_sip_lumpsum_map[constants.EQUITY][constants.SIP], category_sip_lumpsum_map[constants.EQUITY][constants.SIP_COUNT], equity_funds)

                if defected_funds != '':
                    # string_to_return = constants.CHECK_PORTFOLIO_DISTRIBUTION_MESSAGE.format(defected_funds)
                    return api_utils.response({'valid': False}, status.HTTP_400_BAD_REQUEST, defected_funds)
        return api_utils.response({'valid': True}, status.HTTP_200_OK)

class DashboardVersionTwo(APIView):
    """
    API for dashboard version two

    If even a single fund order item exists for user a real dashboard will be shown
    Else a virtual dashboard will be shown
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        is_transient_dashboard = False
        # query all fund_order_items of a user
        all_investments_of_user = models.FundOrderItem.objects.filter(
            portfolio_item__portfolio__user=request.user, is_cancelled=False)

        # for real and transient dashboard
        if all_investments_of_user:
            # for real dashboard
            if all_investments_of_user.filter(is_verified=True):
                # query all redeems of user
                all_redeems_of_user = models.FundRedeemItem.objects.filter(portfolio_item__portfolio__user=request.user)
                # club all investments and redeems of a user according to the funds
                transaction_fund_map, today_portfolio, portfolios_to_be_considered = \
                    utils.club_investment_redeem_together(
                        all_investments_of_user.filter(is_verified=True), all_redeems_of_user.filter(is_verified=True))
            # for transient dashboard
            else:
                user_portfolios = models.Portfolio.objects.filter(user=request.user, is_deleted=False).order_by('created_at')
                transactions_to_be_considered = all_investments_of_user.filter(
                    portfolio_item__portfolio=user_portfolios[0])
                transaction_fund_map, today_portfolio, portfolios_to_be_considered = \
                    utils.club_investment_redeem_together(transactions_to_be_considered, [])
                is_transient_dashboard = True

            # utility to get the json response for the api and change user flag
            portfolio_overview = utils.get_dashboard_version_two(
                transaction_fund_map, today_portfolio, portfolios_to_be_considered, is_transient_dashboard)
            request.user.is_real_seen = True
            request.user.save()
            total_xirr = utils.get_xirr_value_from_dashboard_response(portfolio_overview)
            profile_models.AggregatePortfolio.objects.update_or_create(
            user=request.user, defaults={'total_xirr': round(total_xirr, 1), 'update_date': datetime.now()})
            return api_utils.response(portfolio_overview, status.HTTP_200_OK)

        # for virtual dashboard
        portfolio_items = models.PortfolioItem.objects.filter(
            portfolio__user=request.user, portfolio__has_invested=False, portfolio__is_deleted=False).select_related(
            'portfolio','fund')
        if not portfolio_items:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)
        portfolio_overview = utils.get_portfolio_overview(portfolio_items)
        request.user.is_virtual_seen = True
        request.user.save()
        total_xirr = utils.get_xirr_value_from_dashboard_response(portfolio_overview)
        profile_models.AggregatePortfolio.objects.update_or_create(
            user=request.user ,defaults={'total_xirr': round(total_xirr, 1), 'update_date': datetime.now()})
        return api_utils.response(portfolio_overview, status.HTTP_200_OK)


class LeaderFunds(APIView):
    """
    API to return funds of a leader profile
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """
        takes leader_user_id as an argument and returns the portfolio items of that user with annualized returns
        :param request:
        :return:
        """
        leader_user_id = request.data.get('leader_user_id')

        # query all fund_order_items of a user
        all_investments_of_user = models.FundOrderItem.objects.filter(
            portfolio_item__portfolio__user=leader_user_id, is_cancelled=False)

        # for real and transient portfolio details
        if all_investments_of_user:
            # for real dashboard
            if all_investments_of_user.filter(is_verified=True):
                # query all redeems of user
                all_redeems_of_user = models.FundRedeemItem.objects.filter(
                    portfolio_item__portfolio__user=leader_user_id)
                transaction_fund_map, today_portfolio, portfolios = utils.club_investment_redeem_together(
                    all_investments_of_user.filter(is_verified=True), all_redeems_of_user.filter(is_verified=True))
            # for transient dashboard
            else:
                user_portfolios = models.Portfolio.objects.filter(
                    user=leader_user_id, is_deleted=False).order_by('created_at')
                transactions_to_be_considered = all_investments_of_user.filter(
                    portfolio_item__portfolio=user_portfolios[0])
                transaction_fund_map, today_portfolio, portfolios = utils.club_investment_redeem_together(
                    transactions_to_be_considered, [])

            # utility to get the json response for the api
            portfolio_detail = utils.make_xirr_calculations_for_dashboard_version_two(
                transaction_fund_map, constants.PORTFOLIO_DETAILS, False)

            return api_utils.response(utils.convert_dashboard_to_leaderboard(portfolio_detail), status.HTTP_200_OK)

        # for virtual portfolio details
        portfolio_items = models.PortfolioItem.objects.filter(
            portfolio__user=leader_user_id, portfolio__has_invested=False, portfolio__is_deleted=False).select_related(
            'portfolio', 'fund')
        if not portfolio_items:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)
        portfolio_detail = utils.get_portfolio_details(portfolio_items)
        return api_utils.response(utils.convert_dashboard_to_leaderboard(portfolio_detail), status.HTTP_200_OK)


class PortfolioDetailsVersionTwo(APIView):
    """
    API for portfolio details version two

    If even a single fund order item exists for user a real dashboard will be shown
    Else a virtual dashboard will be shown
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return:
        """
        # query all fund_order_items of a user
        all_investments_of_user = models.FundOrderItem.objects.filter(
            portfolio_item__portfolio__user=request.user, is_cancelled=False)

        # for real and transient portfolio details
        if all_investments_of_user:
            # for real dashboard
            if all_investments_of_user.filter(is_verified=True):
                # query all redeems of user
                all_redeems_of_user = models.FundRedeemItem.objects.filter(portfolio_item__portfolio__user=request.user)
                transaction_fund_map, today_portfolio, portfolios = utils.club_investment_redeem_together(
                    all_investments_of_user.filter(is_verified=True), all_redeems_of_user.filter(is_verified=True))
            # for transient dashboard
            else:
                user_portfolios = models.Portfolio.objects.filter(user=request.user, is_deleted=False).order_by('created_at')
                transactions_to_be_considered = all_investments_of_user.filter(
                    portfolio_item__portfolio=user_portfolios[0])
                transaction_fund_map, today_portfolio, portfolios = utils.club_investment_redeem_together(
                    transactions_to_be_considered, [])

            # utility to get the json response for the api
            return api_utils.response(utils.make_xirr_calculations_for_dashboard_version_two(
                transaction_fund_map, constants.PORTFOLIO_DETAILS, False), status.HTTP_200_OK)

        # for virtual portfolio details
        portfolio_items = models.PortfolioItem.objects.filter(
            portfolio__user=request.user, portfolio__has_invested=False, portfolio__is_deleted=False).select_related(
            'portfolio', 'fund')
        if not portfolio_items:
            return api_utils.response({constants.MESSAGE: constants.USER_PORTOFOLIO_NOT_PRESENT},
                                      status.HTTP_400_BAD_REQUEST, constants.USER_PORTOFOLIO_NOT_PRESENT)
        return api_utils.response(utils.get_portfolio_details(portfolio_items), status.HTTP_200_OK)


class PortfolioTracker(APIView):
    """
    API to return the current/invested amount of user
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        :param request:
        :return: current/invested amount of user
        """
        dates, current_amount, invested_amount, xirr, portfolio_funds = [], [], [], [], []
        virtual_invested_lumpsum, virtual_invested_sip = 0, 0
        weekends = [1, 7]
        # read https://docs.djangoproject.com/en/dev/ref/models/querysets/#week-day for more details
        user_performances = models.PortfolioPerformance.objects.filter(
            user=request.user, date__lte=funds_helper.FundsHelper.get_dashboard_change_date()
        ).exclude(date__week_day__in=weekends).order_by('date')
        if user_performances:
            for user_performance in user_performances:
                dates.append(user_performance.date.strftime('%d-%m-%y'))
                current_amount.append(user_performance.current_amount)
                invested_amount.append(user_performance.invested_amount)
                xirr.append(user_performance.xirr)
            return api_utils.response({constants.DATE: dates, constants.CURRENT_AMOUNT: current_amount, constants.INVESTED_AMOUNT: invested_amount, constants.XIRR: xirr},
                                          status.HTTP_200_OK)
        else:
            try:
                user_portfolio = models.Portfolio.objects.get(user=request.user, has_invested=False, is_deleted= False)
            except models.Portfolio.DoesNotExist:
                return api_utils.response({constants.MESSAGE: constants.USER_PERFORMANCE_PORTOFOLIO_NOT_PRESENT},
                                          status.HTTP_400_BAD_REQUEST, constants.USER_PERFORMANCE_PORTOFOLIO_NOT_PRESENT)
            portfolio_items = user_portfolio.portfolioitem_set.all()
            for portfolio_item in portfolio_items:
                virtual_invested_lumpsum += portfolio_item.lumpsum
                virtual_invested_sip += portfolio_item.sip
                portfolio_funds.append(portfolio_item.fund)

            latest_date = funds_helper.FundsHelper.get_dashboard_change_date()
            historic_performance, dates = utils.get_portfolio_historic_data(utils.get_fund_historic_data_tracker(
                portfolio_funds, user_portfolio.modified_at.date(), latest_date), portfolio_items, True)

            investment_date = user_portfolio.modified_at.date()
            for index in range(len(dates)):
                date_to_consider = datetime.strptime(dates[index], '%d-%m-%y').date()
                months = relativedelta(date_to_consider, investment_date).months
                days = relativedelta(date_to_consider, investment_date).days
                time_since_invest = months + (1 if days >= 0 else 0)
                duration_date = investment_date + relativedelta(months=months, days=days)
                time_since_invest += relativedelta(date_to_consider, duration_date).years * 12

                virtual_invested_total = virtual_invested_lumpsum + (virtual_invested_sip * time_since_invest)
                gain = historic_performance[index] - virtual_invested_total
                xirr.append(round(utils.generate_xirr(gain / virtual_invested_total,
                                                      (date_to_consider - user_portfolio.modified_at.date()).days), 2))
                invested_amount.append(virtual_invested_total)

            return api_utils.response({constants.DATE: dates, constants.CURRENT_AMOUNT: historic_performance,
                                       constants.INVESTED_AMOUNT: invested_amount, constants.XIRR: xirr},
                                      status.HTTP_200_OK)


class TransactionComplete(View):
    """
    An api to trigger Transaction Complete Email.
    """
    def get(self, request):
        """
        Only admin user is allowed to trigger the transaction complete email.

        :param request: 
        :return: send the generated pipe file
        """
        # makes sure that only superuser can access this file.
        if request.user.is_superuser:
            try:
                order_detail = models.OrderDetail.objects.get(order_id=request.GET.get('order_id'))
            except models.OrderDetail.DoesNotExist:
                order_detail = None
                   
            response = models.order_detail_transaction_mail_send(order_detail)
            return HttpResponse(response) 
             
        else:
            return HttpResponse(external_constants.FORBIDDEN_ERROR, status=403)     
            
             
    

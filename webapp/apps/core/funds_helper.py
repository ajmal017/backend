from datetime import date, timedelta
from django.db.models import Max
import logging
from core import models, constants


class FundsHelper(object):
    
    error_logger = logging.getLogger('django.error')
    
    def __init__(self):
        super(FundsHelper, self).__init__()

    @staticmethod
    def get_latest_nav_date_for_funds():
        """
        returns latest nav date for funds
        :return:the minimum date fron funds
        """
        minimum_date = date.today()
    
        historical_fund_objects_by_max_date = models.Fund.objects.annotate(max_date=Max('historicalfunddata__date'))
        for historical_fund_object in historical_fund_objects_by_max_date:
            if historical_fund_object.max_date is not None:
                if historical_fund_object.max_date < minimum_date:
                    minimum_date = historical_fund_object.max_date
        return minimum_date

    @staticmethod
    def get_current_nav(fund_id, nav_date=None):
        if nav_date is None:
            nav_date = FundsHelper.get_latest_nav_date_for_funds()

        try:
            nav = models.HistoricalFundData.objects.get(fund_id=fund_id, date=nav_date).nav
        except:
            nav = 0
        return nav
    
    @staticmethod
    def get_index_latest_working_date(index):
        """
        :param index:
        :return:
        """
        index_list = models.HistoricalIndexData.objects.filter(index=index).order_by('-date')[:3]
        nav_list = []
        for i in index_list:
            if i.date.isoweekday() < 6:
                nav_list.append(i)
        latest_date = nav_list[0].date
        return latest_date
    
    @staticmethod
    def get_dashboard_change_date():
        """
        :return: Minimum dates among all funds date + BSE and NSE
        """
        NSE = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[0])
        BSE = models.Indices.objects.get(index_name=constants.DASHBOARD_BENCHMARKS[1])
        NSE_latest = FundsHelper.get_index_latest_working_date(NSE)
        BSE_latest = FundsHelper.get_index_latest_working_date(BSE)
        return min(NSE_latest, BSE_latest)

    @staticmethod
    def calculate_latest_nav(fund, latest_index_date=None):
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
                latest_fund_nav_date = latest_fund_data.date
                latest_fund_data_nav = latest_fund_data.nav
            else:
                latest_fund_nav_date = latest_fund_data.day_end_date
                latest_fund_data_nav = latest_fund_data.day_end_nav
        else:
            latest_fund_nav_date = latest_fund_data.day_end_date
            latest_fund_data_nav = latest_fund_data.day_end_nav
            
        return latest_fund_data_nav, latest_fund_nav_date
    

    @staticmethod
    def calculate_latest_and_one_previous_nav(fund, latest_index_date=None):
        """
        utility to find latest fund data nd one previous nav for a fund
        :param fund: the fund whose latest and one previous nav is to be found
        :param latest_index_date: the minimum date of bse and nse
        :return:
        """
        latest_fund_data_nav, latest_fund_nav_date = FundsHelper.calculate_latest_nav(fund, latest_index_date)
        
        if latest_fund_nav_date.isoweekday() == 7:
            fund_one_previous_date = latest_fund_nav_date - timedelta(days=3)
        elif latest_fund_nav_date.isoweekday() == 6:
            fund_one_previous_date = latest_fund_nav_date - timedelta(days=2)
        else:
            fund_one_previous_date = latest_fund_nav_date - timedelta(days=1)
        try:
            one_previous_nav = models.HistoricalFundData.objects.get(fund_id=fund, date=fund_one_previous_date).nav
        except:
            one_previous_nav = latest_fund_data_nav
            
        return latest_fund_data_nav, latest_fund_nav_date, one_previous_nav
    
    @staticmethod
    def get_folio_number(user, fund):
        folio_number = ""
        if fund.fund_house:
            try:
                f_numbers = models.FolioNumber.objects.filter(user=user, fund_house=fund.fund_house)
                if f_numbers:
                    folio_number = f_numbers.first().folio_number
            except models.FolioNumber.DoesNotExist:
                pass

        return folio_number

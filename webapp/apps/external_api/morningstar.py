from django.conf import settings

from rest_framework import status

from webapp.apps import generate_error_message
from api import utils as api_utils
from core import models as core_models
from . import constants, helpers, utils
from .funds_backend import BaseFundBackend

import requests
import logging
from xml.etree import ElementTree
from datetime import date, timedelta, datetime


class MorningStarBackend(BaseFundBackend):
    """
    A wrapper that manages the Morning star Backend
    """
    def _get_data(self, api_url):
        """

        :param api_url:
        :return:
        """
        mail_logger = logging.getLogger('django.info')
        try:
            return requests.get(api_url).json()
        except ConnectionError:
            mail_logger.info(constants.CONNECTION_ERROR + api_url)
            return api_utils.response({constants.MESSAGE: "error"}, status.HTTP_408_REQUEST_TIMEOUT, "error")

    def get_data_points_for_funds(self):
        """
        to get data for fund model from morning star
        :return:
        """
        json_data = self._get_data(constants.MORNING_STAR_FUND_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return api_utils.response({constants.MESSAGE: json_data[constants.STATUS][constants.MESSAGE]},
                                      json_data[constants.STATUS][constants.CODE],
                                      generate_error_message(json_data[constants.STATUS][constants.MESSAGE]))
        else:
            logger = logging.getLogger('django.error')
            for fund in json_data[constants.DATA]:
                does_exist = True
                try:
                    earlier_fund = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                except core_models.Fund.DoesNotExist:
                    earlier_fund = None
                    does_exist = False
                for field in constants.FIELDS_FUND_API:
                    if field == constants.BENCHMARK:
                        benchmark_list_of_fund = fund.get(constants.API).get(constants.FUND_MAP[field])
                        fields[field] = benchmark_list_of_fund[0].get(constants.INDEX_NAME)
                    else:
                        fields[field] = fund.get(constants.API).get(constants.FUND_MAP[field])
                    if fields[field] is None:
                        logger.error(helpers.generate_logger_message(field, fund))
                        if does_exist:
                            fields[field] = getattr(earlier_fund, field)
                        else:
                            fields[field] = 0
                core_models.Fund.objects.update_or_create(isin=fields.get("isin"), defaults=fields)
            return api_utils.response(({constants.MESSAGE: constants.SUCCESS}, status.HTTP_200_OK))

    def _deferred_load(self, deferred_load_list):
        """
        utility to save deferred loads
        :param self:
        :param deferred_load_list: a list of deferred loads
        :return:
        """
        if deferred_load_list is None:
            deferred_load_representation = 'Nil'
        else:
            deferred_load_representation = ''
            for index, deferred_load in enumerate(deferred_load_list):
                high_point = deferred_load.get(constants.HIGH_BREAK_POINT)
                unit = deferred_load.get(constants.BREAK_POINT_UNIT)
                value = float(deferred_load.get(constants.VALUE))
                low_point = deferred_load.get(constants.LOW_BREAK_POINT)
                if high_point is None and index == 0:
                    deferred_load_representation += 'Nil'
                elif high_point is None:
                    deferred_load_representation += '>' + low_point + unit + '   ' + str(round(value, 2)) + '%'
                else:
                    deferred_load_representation += low_point + '-' + high_point + ' ' + unit + '   ' + \
                                                    str(round(value, 2)) + '%' + '\n'
        return deferred_load_representation

    def get_data_points_for_fund_data_points_change_monthly(self):
        """
        to get data for data points that change monthly from morning star
        :return:
        """
        json_data = self._get_data(constants.MORNING_STAR_CHANGE_MONTHLY_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            logger = logging.getLogger('django.error')
            count = 0
            for fund in json_data[constants.DATA]:
                does_exist = True
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                try:
                    earlier_fund_data = core_models.FundDataPointsChangeMonthly.objects.get(fund_id=fund_object)
                except core_models.FundDataPointsChangeMonthly.DoesNotExist:
                    earlier_fund_data = None
                    does_exist = False
                for field in constants.FIELDS_DATA_POINTS_MONTHLY_API:
                    if field == constants.MANAGERS:
                        fields[field] = {constants.MANAGERS: str(fund.get(constants.API).get(
                            constants.MONTHLY_CHANGE_POINTS_MAP[field]))}
                    elif field == constants.MAX_DEFERRED_LOAD:
                        fields[constants.MAX_DEFERRED_LOAD] = self._deferred_load(fund.get(constants.API).get(
                            constants.DEFERRED_LOAD))
                    else:
                        fields[field] = fund.get(constants.API).get(constants.MONTHLY_CHANGE_POINTS_MAP[field])
                    if fields[field] is None:
                        logger.error(helpers.generate_logger_message(field, fund))
                        if does_exist:
                            fields[field] = getattr(earlier_fund_data, field)
                        else:
                            fields[field] = 0
                core_models.FundDataPointsChangeMonthly.objects.update_or_create(fund_id=fund_object.id, defaults=fields)
                count += 1
            return count

    def _calulate_beta(self, fund_object):
        """
        calculates beta for funds whose beta is not provided by morning star
        :param fund_object: the object of fund for which beta is being calculated
        :return:
        """
        latest_nav_date = core_models.HistoricalFundData.objects.filter(fund_id=fund_object).latest(
            constants.MODIFIED_AT).date
        date_list = [latest_nav_date]
        for i in range(36):
            date_list.append(latest_nav_date - timedelta(days=(i+1)*30))
        fund_nav_list = [fund_data.nav for fund_data in core_models.HistoricalFundData.objects.filter(
            fund_id=fund_object, date__in=date_list)]
        benchmark_nav_list = [bench_data.nav for bench_data in core_models.HistoricalIndexData.objects.filter(
            index=fund_object.mapped_benchmark, date__in=date_list)]
        return helpers.calculate_beta(fund_nav_list, benchmark_nav_list)

    def _get_exchange_rate(self):
        """
        :return:
        """
        try:
            data = requests.get(constants.EXCHANGE_RATE_API).content
        except ElementTree.ParseError:
            return float(core_models.ExchangeRate.objects.get(key='exchange_rate').value)
        root = ElementTree.fromstring(data)
        transaction = root.find(constants.TRANSACTION)
        exchange_rate_object = core_models.ExchangeRate.objects.get(key='exchange_rate')
        exchange_rate_object.value = transaction.find(constants.CLOSE_PRICE).text
        exchange_rate_object.save()
        return float(transaction.find(constants.CLOSE_PRICE).text)

    def get_data_points_for_fund_data_points_change_daily(self):
        """
        to get data for data points that change daily from morning star
        :return:
        """
        logger_response = 'The funds for which daily data point change ran are - '
        mail_logger = logging.getLogger('django.debug')
        json_data = self._get_data(constants.MORNING_STAR_CHANGE_DAILY_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            exchange_rate = self._get_exchange_rate()
            logger = logging.getLogger('django.error')
            count = 0
            for fund in json_data[constants.DATA]:
                does_exist = True
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                try:
                    earlier_fund_data = core_models.FundDataPointsChangeDaily.objects.get(fund_id=fund_object)
                except core_models.FundDataPointsChangeDaily.DoesNotExist:
                    earlier_fund_data = None
                    does_exist = False
                for field in constants.FIELDS_DATA_POINTS_DAILY_API:
                    fields[field] = fund.get(constants.API).get(constants.DAILY_CHANGE_POINTS_MAP[field])
                    if field == constants.AUM:
                        fields[field] = float(fields[field]) * exchange_rate
                    if fields[field] is None:
                        logger.error(helpers.generate_logger_message(field, fund))
                        if field == constants.BETA:
                            fields[field] = self._calulate_beta(fund_object)
                            # fields[field] = 0
                        else:
                            if does_exist:
                                fields[field] = getattr(earlier_fund_data, field)
                            else:
                                fields[field] = 0
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                core_models.FundDataPointsChangeDaily.objects.update_or_create(fund_id=fund_object.id, defaults=fields)
                logger_response += self.get_historical_data_points(fund.get(constants.ID), True)
                count += 1
            mail_logger.debug(logger_response)
            return count

    # Note - deprecated
    def _save_nav_in_historical_data(self, fund, day_end_date, day_end_nav):
        """
        Saves nav for historical data
        :param fund: the fund for which nav is being saved
        :param day_end_date: the date for nav
        :param day_end_nav: the nav on day_end_date
        :return:
        """
        logger = logging.getLogger('django.info')
        historical_data, is_created = core_models.HistoricalFundData.objects.update_or_create(
            fund_id=fund, date=day_end_date, defaults={'nav': day_end_nav})
        if not is_created:
            logger.info(str(historical_data.nav) + 'updated on' + str(day_end_nav))

    def get_data_points_for_equity(self):
        """
        to get data for data points for equity/elss specific funds
        :return:
        """
        json_data = self._get_data(constants.MORNING_STAR_EQUITY_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            logger = logging.getLogger('django.error')
            count = 0
            for fund in json_data[constants.DATA]:
                does_exist = True
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                try:
                    earlier_fund_data = core_models.EquityFunds.objects.get(fund_id=fund_object)
                except core_models.EquityFunds.DoesNotExist:
                    earlier_fund_data = None
                    does_exist = False
                for field in constants.FIELDS_DATA_POINTS_EQUITY_API:
                    if field == constants.NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS:
                        fields[field] = {constants.HOLDINGS: str(fund.get(constants.API).get(
                            constants.EQUITY_DATA_POINTS_MAP[field])[:5])}
                    else:
                        fields[field] = fund.get(constants.API).get(constants.EQUITY_DATA_POINTS_MAP[field])
                    if fields[field] is None:
                        logger.error(helpers.generate_logger_message(field, fund))
                        if does_exist:
                            fields[field] = getattr(earlier_fund_data, field)
                        else:
                            fields[field] = 0
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                core_models.EquityFunds.objects.update_or_create(fund_id=fund_object.id, defaults=fields)
                count += 1
            return count

    def get_data_points_for_sectors(self):
        """
        to get data for data points for top three sectors for equity/elss specific funds
        :return:
        """
        json_data = self._get_data(constants.MORNING_STAR_SECTOR_API)
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            count = 0
            for fund in json_data[constants.DATA]:
                sector_name_weight_list = []
                for field in constants.FIELDS_DATA_POINTS_SECTOR_API:
                    sector_name_weight_list.append([field, fund.get(constants.API).get(field)])
                sectors_sorted_weighatge = sorted(sector_name_weight_list, key=lambda tup: float(tup[1]), reverse=True)[:3]
                fields = {constants.FIRST_NAME: sectors_sorted_weighatge[0][0],
                          constants.FIRST_WEIGHTAGE: sectors_sorted_weighatge[0][1],
                          constants.SECOND_NAME: sectors_sorted_weighatge[1][0],
                          constants.SECOND_WEIGHTAGE: sectors_sorted_weighatge[1][1],
                          constants.THIRD_NAME: sectors_sorted_weighatge[2][0],
                          constants.THIR_WEIGHTAGE: sectors_sorted_weighatge[2][1]}
                equity_object = core_models.EquityFunds.objects.get(fund__mstar_id=fund.get(constants.ID))
                core_models.TopThreeSectors.objects.update_or_create(equity_fund_id=equity_object.id, defaults=fields)
                count += 1
            return count

    def get_data_points_for_debt(self):
        """
        to get data for data points for debt specific funds
        :return:
        """
        json_data = self._get_data(constants.MORNING_STAR_DEBT_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            logger = logging.getLogger('django.error')
            count = 0
            for fund in json_data[constants.DATA]:
                does_exist = True
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                try:
                    earlier_fund_data = core_models.DebtFunds.objects.get(fund_id=fund_object)
                except core_models.DebtFunds.DoesNotExist:
                    earlier_fund_data = None
                    does_exist = False
                for field in constants.FIELDS_DATA_POINTS_DEBT_API:
                    if field == constants.NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS:
                        fields[field] = {constants.HOLDINGS: str(fund.get(constants.API).get(
                            constants.DEBT_DATA_POINTS_MAP[field])[:3])}
                    else:
                        fields[field] = fund.get(constants.API).get(constants.DEBT_DATA_POINTS_MAP[field])
                    if fields[field] is None:
                        if does_exist:
                            fields[field] = getattr(earlier_fund_data, field)
                        else:
                            logger.error(helpers.generate_logger_message(field, fund))
                        fields[field] = 0
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                core_models.DebtFunds.objects.update_or_create(fund_id=fund_object.id, defaults=fields)
                count += 1
            return count

    def get_data_points_for_liquid(self):
        """
        to get data for data points for debt specific funds
        :return:
        """
        json_data = self._get_data(constants.MORNING_STAR_LIQUID_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            logger = logging.getLogger('django.error')
            count = 0
            for fund in json_data[constants.DATA]:
                does_exist = True
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                try:
                    earlier_fund_data = core_models.LiquidFunds.objects.get(fund_id=fund_object)
                except core_models.LiquidFunds.DoesNotExist:
                    earlier_fund_data = None
                    does_exist = False
                for field in constants.FIELDS_DATA_POINTS_LIQUID_API:
                    if field == constants.NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS:
                        fields[field] = {constants.HOLDINGS: str(fund.get(constants.API).get(
                            constants.LIQUID_DATA_POINTS_MAP[field])[:3])}
                    else:
                        fields[field] = fund.get(constants.API).get(constants.LIQUID_DATA_POINTS_MAP[field])
                    if fields[field] is None:
                        if does_exist:
                            fields[field] = getattr(earlier_fund_data, field)
                        else:
                            logger.error(helpers.generate_logger_message(field, fund))
                        fields[field] = 0
                fund_object = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
                core_models.LiquidFunds.objects.update_or_create(fund_id=fund_object.id, defaults=fields)
                count += 1
            return count

    # Note - deprecated
    def get_daily_nav_for_indices(self):
        """
        to get nav for daily indices
        :return:
        """
        json_data = self._get_data(constants.INDICES_NAV_API)
        fields = {}
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            count = 0
            logger = logging.getLogger('django.error')
            for fund in json_data[constants.DATA]:
                date_of_nav = fund.get(constants.API).get(constants.INDICES_NAV_LIST_MAP[constants.INDICES_DAY_END_DATE])
                nav = fund.get(constants.API).get(constants.INDICES_NAV_LIST_MAP[constants.INDICES_DAY_END_PRICE])
                if date_of_nav is None or nav is None:
                    logger.error(helpers.generate_logger_message(date_of_nav, fund))
                index = core_models.Indices.objects.get(mstar_id=fund.get(constants.ID))
                core_models.HistoricalIndexData.objects.update_or_create(index=index, date=date_of_nav,
                                                                         defaults={constants.NAV: nav})
                count += 1
            return count

    def get_historical_data_points(self, fund_mstar_id, for_daily_nav=False):
        """
        to get historical data points for all funds from their inception date till present
        :param fund_mstar_id: the mstar id of fund for which we need historical data
        :param for_daily_nav: flag to determine if we use the function for setting daily nav
        :return:
        """
        fund_list = ''
        try:
            fund = core_models.Fund.objects.get(mstar_id=fund_mstar_id)
        except core_models.Fund.DoesNotExist:
            return api_utils.response({constants.MESSAGE: constants.FUND_DOES_NOT_EXIST}, status.HTTP_400_BAD_REQUEST,
                                      constants.FUND_DOES_NOT_EXIST)
        start_date = settings.START_DATE
        if start_date is None:
            if for_daily_nav:
                start_date = date.today() - timedelta(days=10)
            else:
                start_date = fund.inception_date
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        while start_date < date.today():
            end_date = start_date + timedelta(days=constants.HISTORICAL_DATA_TIME_INTERVAL)
            if end_date > date.today():
                end_date = date.today()
            url = utils.generate_url_for_historical_data(fund_mstar_id, start_date, end_date)
            json_data = self._get_data(url)
            for data in json_data[constants.DATA][constants.API][constants.RAW_DATA]:
                date_of_nav = data[constants.HISTORICAL_DATA_MAP[constants.DATE]]
                nav = data[constants.HISTORICAL_DATA_MAP[constants.NAV]]
                core_models.HistoricalFundData.objects.update_or_create(fund_id=fund, date=date_of_nav,
                                                                        defaults={constants.NAV: nav})
            start_date = end_date
            fund_list += str(fund_mstar_id + ' ' + str(end_date) + '\n')

        return fund_list

    def get_daily_nav_for_indices_new(self):
        """
        new utility for setting nav of indices on daily basis
        :return:
        """
        logger_response = 'The indices for which daily data point change ran are - '
        logger = logging.getLogger('django.debug')
        index_mstar_ids = core_models.Indices.objects.values_list(constants.MSTAR_ID, flat=True)
        count = 0
        for index_id in index_mstar_ids:
            self.get_historical_index_data_points(index_id, date.today() - timedelta(days=10),
                                                  date.today() + timedelta(days=10))
            logger_response += str(index_id + " ")
            count += 1
        logger.debug(logger_response)
        return count

    def get_historical_index_data_points(self, index_mstar_id, start_date, last_date):
        """
        To get historical data points for all indices from their start date till end date
        :param index_mstar_id: the mstar id of index for which we need historical data
        :param start_date:start date from when we need data
        :param last_date: end date till which we need data
        :return:
        """
        while start_date < last_date:
            end_date = start_date + timedelta(days=constants.HISTORICAL_DATA_TIME_INTERVAL)
            if end_date > last_date:
                end_date = last_date
            url = utils.generate_url_for_historical_data(index_mstar_id, start_date, end_date)
            json_data = self._get_data(url)
            if json_data.get(constants.DATA):
                for data in json_data[constants.DATA][constants.API][constants.RAW_DATA]:
                    index_mstar_id = json_data[constants.DATA][constants.ID]
                    index = core_models.Indices.objects.get(mstar_id=index_mstar_id)
                    date_of_nav = data[constants.HISTORICAL_DATA_MAP[constants.DATE]]
                    nav = data[constants.HISTORICAL_DATA_MAP[constants.NAV]]
                    core_models.HistoricalIndexData.objects.update_or_create(index=index, date=date_of_nav,
                                                                             defaults={constants.NAV: nav})
            start_date = end_date

    # NOTE - deprecated
    def get_daily_nav_for_categories(self):
        """
        to get nav for daily categories
        :return:
        """
        json_data = self._get_data(constants.CATEGORY_NAV_API)
        if json_data[constants.STATUS][constants.CODE] != 0:
            return False
        else:
            logger = logging.getLogger('django.error')
            count = 0
            for fund in json_data[constants.DATA]:
                date_of_nav = fund.get(constants.API).get(constants.CATEGORY_DAY_END_DATE)
                nav = fund.get(constants.API).get(constants.CATEGORY_DAY_END_PRICE)
                category_code = fund.get(constants.API).get(constants.CATEGORY_CODE_DAILY)
                if date_of_nav is None or nav is None:
                    logger.error(helpers.generate_logger_message(date_of_nav, fund))
                core_models.HistoricalCategoryData.objects.update_or_create(
                    category_code=category_code, date=date_of_nav, defaults={constants.NAV: nav})
                count += 1
            return count

    def get_daily_nav_categories_new(self):
        """
        to get nav for categories on basis of historical category function
        :return:
        """
        logger = logging.getLogger('django.debug')
        logger_response = 'The categories for which daily data point change ran are - '
        category_codes = set(core_models.Fund.objects.all().values_list(constants.CATEGORY_CODE, flat=True))
        count= 0
        for category_code in category_codes:
            self.get_historical_category_data(category_code, date.today() - timedelta(days=10),
                                              date.today() + timedelta(days=10))
            logger_response += str(category_code + " ")
            count += 1
        logger.debug(logger_response)
        return count

    def get_historical_category_data(self, category_id, start_date, last_date):
        """
        to get historical data of categories
        :param category_id:the id of category
        :param start_date:the date from which data is required
        :param last_date:the date till which data is required
        :return:
        """
        while start_date < last_date:
            end_date = start_date + timedelta(days=constants.HISTORICAL_DATA_TIME_INTERVAL)
            if end_date > last_date:
                end_date = last_date
            url = utils.generate_url_for_category_history(category_id, start_date, end_date)
            json_data = self._get_data(url)
            for data in json_data[constants.DATA][constants.API]:
                category_id = json_data[constants.DATA][constants.ID]
                date_of_nav = data[constants.HISTORICAL_DATA_MAP[constants.DATE]]
                nav = data[constants.HISTORICAL_DATA_MAP[constants.NAV]]
                core_models.HistoricalCategoryData.objects.update_or_create(category_code=category_id, date=date_of_nav,
                                                                            defaults={constants.NAV: nav})
            start_date = end_date

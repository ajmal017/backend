from . import constants, helpers, utils
from django.conf import settings

from rest_framework import status

from webapp.apps import generate_error_message
from api import utils as api_utils
from core import models as core_models
from . import constants, helpers, utils

import requests
import logging
from xml.etree import ElementTree
from datetime import date, timedelta, datetime


class NSEBackend():
    """
    A wrapper that manages the NSE Purchase Transactions Backend
    """

    def _get_data(self, api_url, xml_request_body):
        """

        :param api_url:
        :return:
        """
        mail_logger = logging.getLogger('django.info')
        try:
            headers = {'Content-Type': 'application/xml'}
            return requests.post(api_url, data=xml_request_body, headers=headers)
        except ConnectionError:
            mail_logger.info(constants.CONNECTION_ERROR + api_url)
            return api_utils.response({constants.MESSAGE: "error"}, status.HTTP_408_REQUEST_TIMEOUT, "error")

    def _get_request_body(self, api_url):

        """

        :param api_url:
        :return:
        """
        if api_url == constants.NSE_GETIIN:
            return """<NMFIIService> <service_request>

< appln_id > KRISHNA < / appln_id > < password > TEST$258 < / password > < broker_code > ARN - 70209 < / broker_code > < tax_status > 01 < / tax_status > < hold_nature > SI < / hold_nature > < exempt_flag > N < / exempt_flag > < fh_pan > ABAPL9854C < / fh_pan > < jh1_exempt_flag > N < / jh1_exempt_flag > < jh1_pan > < / jh1_pan > < jh2_exempt_flag > N < / jh2_exempt_flag > < jh2_pan > < / jh2_pan > < guardian_pan > < / guardian_pan > / service_request >
< / NMFIIService > """


def get_iin(self):
    """
    to get IIN OR CUSTOMER ID
    :return:
    """
    xml_request_body = self._get_request_body(constants.NSE_GETIIN)

    xml_response_data = self._get_data(constants.NSE_GETIIN, xml_request_body)

    print(xml_response_data)
    # fields = {}
    # if json_data[constants.STATUS][constants.CODE] != 0:
    #     return api_utils.response({constants.MESSAGE: json_data[constants.STATUS][constants.MESSAGE]},
    #                               json_data[constants.STATUS][constants.CODE],
    #                               generate_error_message(json_data[constants.STATUS][constants.MESSAGE]))
    # else:
    #     logger = logging.getLogger('django.error')
    #     for fund in json_data[constants.DATA]:
    #         does_exist = True
    #         try:
    #             earlier_fund = core_models.Fund.objects.get(mstar_id=fund.get(constants.ID))
    #         except core_models.Fund.DoesNotExist:
    #             earlier_fund = None
    #             does_exist = False
    #         for field in constants.FIELDS_FUND_API:
    #             if field == constants.BENCHMARK:
    #                 benchmark_list_of_fund = fund.get(constants.API).get(constants.FUND_MAP[field])
    #                 fields[field] = benchmark_list_of_fund[0].get(constants.INDEX_NAME)
    #             else:
    #                 fields[field] = fund.get(constants.API).get(constants.FUND_MAP[field])
    #             if fields[field] is None:
    #                 logger.error(helpers.generate_logger_message(field, fund))
    #                 if does_exist:
    #                     fields[field] = getattr(earlier_fund, field)
    #                 else:
    #                     fields[field] = 0
    #         core_models.Fund.objects.update_or_create(isin=fields.get("isin"), defaults=fields)
    #     return api_utils.response(({constants.MESSAGE: constants.SUCCESS}, status.HTTP_200_OK))

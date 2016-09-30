from rest_framework import status

from external_api.nse import create_validate_nserequests
from external_api.nse import constants as nse_constants
from external_api import constants
from external_api import models
from external_api import ExchangeBackend
from profiles import models as pr_models
from profiles import constants as profile_constants
from external_api.bse import bank_mandate
from external_api.bse import bse_investor_info_generation
from external_api.bse import bulk_upload

import os
import re
import pdb
from api import utils as api_utils
import xml.etree.ElementTree as ET
import requests
import logging


class BSEBackend(object, ExchangeBackend):
    """
    A wrapper that manages the NSE Purchase Transactions Backend
    """

    def _get_data(self, method_name, xml_request_body):
        """

        :param api_url:
        :return: XML Element
        """
        api_url = nse_constants.NSE_NMF_BASE_API_URL + method_name
        error_logger = logging.getLogger('django.error')
        try:
            headers = {'Content-Type': 'application/xml', 'accept': 'application/xml'}
            response = requests.request("POST", api_url, data=xml_request_body, headers=headers)
            return self._get_valid_response(response)
        except ConnectionError:
            error_logger.info(constants.CONNECTION_ERROR + api_url)
        except requests.HTTPError:
            error_logger.info(constants.HTTP_ERROR + api_url)

    def _get_valid_response(self, response):
        if response.status_code == requests.codes.ok:
            element = ET.fromstring(response.text)
            root = element.find(nse_constants.RESPONSE_BASE_PATH)
            return root
        response.raise_for_status()

    def _get_request_body(self, method_name, user_id):

        """

        :param method_name:
        :return:
        """
        if method_name == nse_constants.METHOD_GETIIN:
            root = ET.fromstring(nse_constants.REQUEST_GETIIN)
            return create_validate_nserequests.getiinrequest(root, user_id)
        elif method_name == nse_constants.METHOD_CREATECUSTOMER:
            root = ET.fromstring(nse_constants.REQUEST_CREATECUSTOMER)
            return create_validate_nserequests.createcustomerrequest(root, user_id)
        elif method_name == nse_constants.METHOD_PURCHASETXN:
            root = ET.fromstring(nse_constants.REQUEST_PURCHASETXN)
            return create_validate_nserequests.purchasetxnrequest(root, user_id)
        elif method_name == nse_constants.METHOD_ACHMANDATEREGISTRATIONS:
            root = ET.fromstring(nse_constants.REQUEST_ACHMANDATEREGISTRATIONS)
            return create_validate_nserequests.achmandateregistrationsrequest(root, user_id)
        return

    def get_iin(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        xml_request_body = self._get_request_body(nse_constants.METHOD_GETIIN, user_id)
        root = self._get_data(nse_constants.METHOD_GETIIN, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return nse_constants.RETURN_CODE_SUCCESS
        else:
            createFlag = False
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                if error_msg == nse_constants.NO_DATA_FOUND:
                    createFlag = True
                error_logger.info(error_msg)
            if createFlag:
                return nse_constants.RETURN_CODE_FAILURE
            else:
                raise AttributeError

    def create_customer(self, user_id):
        return constants.RETURN_CODE_FAILURE
    
    def upload_aof_image(self, user_id):
        return constants.RETURN_CODE_FAILURE
    
    def purchase_trxn(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        xml_request_body = self._get_request_body(nse_constants.METHOD_PURCHASETXN, user_id)
        # make an entry to db for this order and transaction
        root = self._get_data(nse_constants.METHOD_PURCHASETXN, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            payment_link = root.find(nse_constants.RESPONSE_PAYMENT_LINK_PATH).text
            # Save payment link Order_detail Table
            return nse_constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return nse_constants.RETURN_CODE_FAILURE


    def ach_mandate_registrations(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        xml_request_body = self._get_request_body(nse_constants.METHOD_ACHMANDATEREGISTRATIONS, user_id)
        root = self._get_data(nse_constants.METHOD_ACHMANDATEREGISTRATIONS,
                                          xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            # save this entry to NSE_Details table
            return nse_constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return nse_constants.RETURN_CODE_FAILURE


    def bulk_create_customer(self, user_list):
        """
        This function generates a pipe separated file for bulk order entry.
        
        :param user_list: list of users to be bulk uploaded.
        :return: url of the generated pipe separated file of the bulk order entry
        """
        return bulk_upload.generate_client_pipe(user_list, self)
    
    def generate_aof_image(self, user_id):
        filePath = bse_investor_info_generation.bse_investor_info_generator(user_id)
        return filePath

    def generate_bank_mandate(self, user_id):
        return bank_mandate.generate_bank_mandate_pdf(user_id)

    def upload_bank_mandate(self, user_id):
        return constants.RETURN_CODE_FAILURE
    
    def generate_bank_mandate_registration(self, user_id):
        return NotImplementedError

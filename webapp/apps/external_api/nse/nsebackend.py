from rest_framework import status

from external_api.nse import create_validate_nserequests
from external_api.nse import constants as nse_constants
from external_api import constants
from external_api.nse import debit_mandate
from external_api.nse import nse_iinform_generation
import os
from api import utils as api_utils
import xml.etree.ElementTree as ET
import requests
import logging


class NseBackend():
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
            return self._get_valid_response(response, error_logger)
        except ConnectionError:
            error_logger.info(constants.CONNECTION_ERROR + api_url)
        except requests.HTTPError:
            error_logger.info(constants.HTTP_ERROR + api_url)

    def _get_valid_response(self, response):
        error_logger = logging.getLogger('django.error')
        if response.status_code == requests.codes.ok:
            element = ET.fromstring(response.text)
            root = element.find(nse_constants.RESPONSE_BASE_PATH)
            return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
            if return_code == nse_constants.RETURN_CODE_SUCCESS:
                return root.find(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            else:
                error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
                for error in error_responses:
                    error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                    error_logger.info(error_msg)
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
        xml_request_body = self._get_request_body(nse_constants.METHOD_GETIIN, user_id)
        response_element = self._get_data(nse_constants.METHOD_GETIIN, xml_request_body=xml_request_body)
        return response_element

    def create_customer(self, user_id):
        """
        # Complete with iin form upload flow

        :param:
        :return:
        """
        xml_request_body = self._get_request_body(nse_constants.METHOD_CREATECUSTOMER, user_id)
        response_element = self._get_data(nse_constants.METHOD_CREATECUSTOMER, xml_request_body=xml_request_body)
        return response_element

    def purchase_trxn_sip(self, user_id):
        """

        :param:
        :return:
        """
        # Complete ach registration and debit mandate upload flow

        xml_request_body = self._get_request_body(nse_constants.METHOD_PURCHASETXN, user_id)
        response_element = self._get_data(nse_constants.METHOD_PURCHASETXN, xml_request_body=xml_request_body)
        return response_element

    def purchase_trxn_lumpsum(self, user_id):
        """

        :param:
        :return:
        """

        xml_request_body = self._get_request_body(nse_constants.METHOD_PURCHASETXN, user_id)
        response_element = self._get_data(nse_constants.METHOD_PURCHASETXN, xml_request_body=xml_request_body)
        return response_element

    def ach_mandate_registrations(self, user_id):
        """

        :param:
        :return:
        """

        xml_request_body = self._get_request_body(nse_constants.METHOD_ACHMANDATEREGISTRATIONS, user_id)
        response_element = self._get_data(nse_constants.METHOD_ACHMANDATEREGISTRATIONS,
                                          xml_request_body=xml_request_body)
        return response_element

    def upload_img(self, customer_id, user_id, ref_no='', image_type=''):
        queryString = "?BrokerCode=" + nse_constants.NSE_NMF_BROKER_CODE + "&Appln_id=" + nse_constants.NSE_NMF_APPL_ID + \
                      "&Password=" + nse_constants.NSE_NMF_PASSWORD + "&CustomerID=" + customer_id + "&Refno=" + ref_no + \
                      "&ImageType=" + image_type
        api_url = nse_constants.NSE_NMF_BASE_API_URL + nse_constants.METHOD_UPLOADIMG + queryString
        filePath = ""
        if image_type == "A":
            filePath = nse_iinform_generation.get_tiff(user_id)
        elif image_type == "X":
            filePath = debit_mandate.get_tiff(user_id)

        headers = {'Content-Type': 'application/octet-stream'}
        with open(filePath, 'rb') as f:
            response = requests.post(api_url, files={'image': f}, headers=headers)
        response_element = self._get_valid_response(response)
        return response_element

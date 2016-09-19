from rest_framework import status
from .nse import constants as nse_constants
from . import constants
import os
from api import utils as api_utils
import xml.etree.ElementTree as ET
import requests
import logging


class NSEBackend():
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
        except ConnectionError:
            error_logger.info(constants.CONNECTION_ERROR + api_url)
        except requests.HTTPError:
            error_logger.info(constants.HTTP_ERROR + api_url)


    def _get_request_body(self, api_url):

        """

        :param api_url:
        :return:
        """
        if api_url == nse_constants.METHOD_GETIIN:
            root = ET.fromstring(nse_constants.REQUEST_GETIIN)
            # Have to add values in the template before forming xml body
            return ET.tostring(root)
        elif api_url == nse_constants.METHOD_IINDETAILS:
            root = ET.fromstring(nse_constants.REQUEST_IINDETAILS)
            root = tree.getroot()
            # Have to add values in the template before forming xml body
            return ET.tostring(root)
        elif api_url == nse_constants.METHOD_CREATECUSTOMER:
            root = ET.fromstring(nse_constants.REQUEST_CREATECUSTOMER)
            root = tree.getroot()
            # Have to add values in the template before forming xml body
            return ET.tostring(root)
        elif api_url == nse_constants.METHOD_PURCHASETXN:
            root = ET.fromstring(nse_constants.REQUEST_PURCHASETXN)
            root = tree.getroot()
            # Have to add values in the template before forming xml body
            return ET.tostring(root, encoding='utf8', method='xml')
        return


    def get_iin(self):
        """

        :param:
        :return:
        """
        xml_request_body = self._get_request_body(nse_constants.METHOD_GETIIN)
        response_element = self._get_data(nse_constants.METHOD_GETIIN, xml_request_body=xml_request_body)
        return response_element

    def create_customer(self):
        """

        :param:
        :return:
        """
        xml_request_body = self._get_request_body(nse_constants.METHOD_CREATECUSTOMER)
        response_element = self._get_data(nse_constants.METHOD_CREATECUSTOMER, xml_request_body=xml_request_body)
        return response_element

    def get_iin_details(self):
        """

        :param:
        :return:
        """
        xml_request_body = self._get_request_body(nse_constants.METHOD_IINDETAILS)
        response_element = self._get_data(nse_constants.METHOD_IINDETAILS, xml_request_body=xml_request_body)
        return response_element

    def purchase_trxn(self, type="sip"):
        """

        :param:
        :return:
        """
        # Make trxn based on type value either "sip or lumpsum"

        xml_request_body = self._get_request_body(nse_constants.METHOD_PURCHASETXN)
        response_element = self._get_data(nse_constants.METHOD_PURCHASETXN, xml_request_body=xml_request_body)
        return response_element

    def upload_img(self, customer_id, ref_no='', image_type=''):
        queryString = "?BrokerCode=" + "ARN-108537" + "&Appln_id=" + "MFS108537" + "&Password=" + "test$258" + "&CustomerID=" + customer_id  + "&Refno=" + ref_no + "&ImageType=" + image_type
        api_url = nse_constants.NSE_UPLOAD_IMG_URL + queryString
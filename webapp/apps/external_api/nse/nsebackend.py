from rest_framework import status

from external_api.nse import create_validate_nserequests
from external_api.nse import constants as nse_constants
from external_api import constants
from external_api import models
from profiles import models as pr_models
from payment import models as payment_models
from external_api.nse import bank_mandate
from external_api.nse import nse_iinform_generation
import os
import re
import pdb
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
            createCustomerFlag = False
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                if error_msg == nse_constants.NO_DATA_FOUND:
                    createCustomerFlag = True
                error_logger.info(error_msg)
            if createCustomerFlag:
                return nse_constants.RETURN_CODE_FAILURE
            else:
                raise AttributeError

    def create_customer(self, user_id):
        """
        # Complete with iin form upload flow

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        xml_request_body = self._get_request_body(nse_constants.METHOD_CREATECUSTOMER, user_id)
        root = self._get_data(nse_constants.METHOD_CREATECUSTOMER, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return_msg = root.find(nse_constants.SERVICE_RETURN_MSG_PATH).text
            return_msg = return_msg.replace(" ", "")
            iin_customer_id = re.search('ID:(.+?)', return_msg)
            nse_user = pr_models.User.get(id=user_id)
            vendor = models.Vendors.get(name='NSE')
            models.NseDetails(user=nse_user, iin_customer_id=iin_customer_id).save()
            models.UserVendors(user=nse_user, vendor=vendor).save()
            self.upload_img(user_id=user_id, image_type="A")
            return nse_constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                print(error_msg)
                error_logger.info(error_msg)
            return nse_constants.RETURN_CODE_FAILURE


    def purchase_trxn(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        xml_request_body = self._get_request_body(nse_constants.METHOD_PURCHASETXN, user_id)
        root = self._get_data(nse_constants.METHOD_PURCHASETXN, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            payment_link = root.find(nse_constants.RESPONSE_PAYMENT_LINK_PATH).text
            current_transaction = payment_models.Transaction.get(user_id=user_id, txn_status=0)
            # 0 for pending transactions assuming there is only one pending transaction
            current_transaction.payment_link= payment_link
            current_transaction.save()
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
            nse_user = pr_models.User.get(id=user_id)
            nse_details = models.NseDetails.get(user=nse_user)
            nse_details.ach_inserted = True
            nse_details.save()
            return nse_constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return nse_constants.RETURN_CODE_FAILURE


    def upload_img(self, user_id, ref_no='', image_type=''):
        error_logger = logging.getLogger('django.error')
        nse_user = models.NseDetails.get(user_id=user_id)
        queryString = "?BrokerCode=" + nse_constants.NSE_NMF_BROKER_CODE + "&Appln_id=" + nse_constants.NSE_NMF_APPL_ID + \
                      "&Password=" + nse_constants.NSE_NMF_PASSWORD + "&CustomerID=" + nse_user.iin_customer_id + "&Refno=" + ref_no + \
                      "&ImageType=" + image_type
        api_url = nse_constants.NSE_NMF_BASE_API_URL + nse_constants.METHOD_UPLOADIMG + queryString
        filePath = ""
        if image_type == "A":
            filePath = nse_iinform_generation.nse_investor_info_generator(user_id)
        elif image_type == "X":
            filePath = bank_mandate.generate_bank_mandate_tiff(user_id)

        headers = {'Content-Type': 'image/tiff'}
        with open(filePath, 'rb') as f:
            response = requests.post(api_url, files={'image': f}, headers=headers)
        root = self._get_valid_response(response)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return nse_constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return nse_constants.RETURN_CODE_FAILURE

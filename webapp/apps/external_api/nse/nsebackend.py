from rest_framework import status

from external_api.nse import create_validate_nserequests
from external_api.nse import constants as nse_constants
from external_api import constants
from external_api import models
from external_api.exchange_backend import ExchangeBackend 
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


class NSEBackend(ExchangeBackend):
    """
    A wrapper that manages the NSE Purchase Transactions Backend
    """
    error_logger = logging.getLogger('django.error')

    def __init__(self, vendor_name):
        super(ExchangeBackend, self).__init__(vendor_name)
        
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

    def _get_request_body(self, method_name, user_id, **kwargs):

        """

        :param method_name:
        :return:
        """
        if method_name == nse_constants.METHOD_GETIIN:
            root = ET.fromstring(nse_constants.REQUEST_GETIIN)
            return create_validate_nserequests.getiinrequest(root, user_id, **kwargs)
        elif method_name == nse_constants.METHOD_CREATECUSTOMER:
            root = ET.fromstring(nse_constants.REQUEST_CREATECUSTOMER)
            return create_validate_nserequests.createcustomerrequest(root, user_id)
        elif method_name == nse_constants.METHOD_PURCHASETXN:
            root = ET.fromstring(nse_constants.REQUEST_PURCHASETXN)
            return create_validate_nserequests.purchasetxnrequest(root, user_id, **kwargs)
        elif method_name == nse_constants.METHOD_ACHMANDATEREGISTRATIONS:
            root = ET.fromstring(nse_constants.REQUEST_ACHMANDATEREGISTRATIONS)
            return create_validate_nserequests.achmandateregistrationsrequest(root, user_id, **kwargs)
        elif method_name == nse_constants.METHOD_CEASESIP:
            root = ET.fromstring(nse_constants.REQUEST_CEASESIP)
            return create_validate_nserequests.ceasesystematictrxn(root, user_id, **kwargs)
        return

    def get_iin(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        kwargs = {'exchange_backend': self}
        xml_request_body = self._get_request_body(nse_constants.METHOD_GETIIN, user_id, **kwargs)
        root = self._get_data(nse_constants.METHOD_GETIIN, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return constants.RETURN_CODE_SUCCESS
        else:
            createCustomerFlag = False
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                if error_msg == nse_constants.NO_DATA_FOUND:
                    createCustomerFlag = True
                error_logger.info(error_msg)
            if createCustomerFlag:
                return constants.RETURN_CODE_FAILURE
            else:
                raise AttributeError

    def update_ucc(self, user_id, ucc):
        user_vendor = super(ExchangeBackend, self).update_ucc(user_id, ucc)
        if user_vendor:
            try: 
                user_vendor.ucc_registered = True
                user_vendor.save()
            except Exception as e:
                self.error_logger.error("Error updating ucc status: " + str(e))
        
    def cease_sip(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        kwargs = {'exchange_backend': self}
        xml_request_body = self._get_request_body(nse_constants.METHOD_CEASESIP, user_id, **kwargs)
        root = self._get_data(nse_constants.METHOD_CEASESIP, xml_request_body=xml_request_body)
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
        """
        # Complete with iin form upload flow

        :param:
        :return:
        """
        kwargs = {'exchange_backend': self}
        xml_request_body = self._get_request_body(nse_constants.METHOD_CREATECUSTOMER, user_id, **kwargs)
        root = self._get_data(nse_constants.METHOD_CREATECUSTOMER, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return_msg = root.find(nse_constants.SERVICE_RETURN_MSG_PATH).text
            return_msg = return_msg.replace(" ", "")
            iin_customer_id = re.search('ID:(.+?)', return_msg)
            self.update_ucc(user_id, iin_customer_id)
            return constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                print(error_msg)
                self.error_logger.info(error_msg)
            return constants.RETURN_CODE_FAILURE

    def upload_aof_image(self, user_id):
        self.upload_img(user_id=user_id, image_type="A")
        return constants.RETURN_CODE_SUCCESS

    def purchase_trxn(self, user_id):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        kwargs = {'exchange_backend': self}
        xml_request_body = self._get_request_body(nse_constants.METHOD_PURCHASETXN, user_id, **kwargs)
        root = self._get_data(nse_constants.METHOD_PURCHASETXN, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            payment_link = root.find(nse_constants.RESPONSE_PAYMENT_LINK_PATH).text
            current_transaction = payment_models.Transaction.get(user_id=user_id, txn_status=0)
            # 0 for pending transactions assuming there is only one pending transaction
            current_transaction.payment_link= payment_link
            current_transaction.save()
            return constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return constants.RETURN_CODE_FAILURE


    def generate_bank_mandate_registration(self, user_id, mandate_amount):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        kwargs = {"mandate_amount":mandate_amount, 'exchange_backend': self}
        xml_request_body = self._get_request_body(nse_constants.METHOD_ACHMANDATEREGISTRATIONS, user_id, **kwargs)
        root = self._get_data(nse_constants.METHOD_ACHMANDATEREGISTRATIONS,
                                          xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            super(ExchangeBackend, self).update_mandate_registration(user_id)
            return constants.RETURN_CODE_SUCCESS, None
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return constants.RETURN_CODE_FAILURE, None


    def upload_img(self, user_id, ref_no='', image_type='', **kwargs):
        error_logger = logging.getLogger('django.error')
        user_vendor = models.UserVendor.objects.get(user__id=user_id, vendor__name=self.vendor_name)
        queryString = "?BrokerCode=" + nse_constants.NSE_NMF_BROKER_CODE + "&Appln_id=" + nse_constants.NSE_NMF_APPL_ID + \
                      "&Password=" + nse_constants.NSE_NMF_PASSWORD + "&CustomerID=" + user_vendor.ucc + "&Refno=" + ref_no + \
                      "&ImageType=" + image_type
        api_url = nse_constants.NSE_NMF_BASE_API_URL + nse_constants.METHOD_UPLOADIMG + queryString
        filePath = ""
        if image_type == "A":
            filePath = self.generate_aof_image(user_id)
        elif image_type == "X":
            filePath = bank_mandate.generate_bank_mandate_tiff(user_id, **kwargs)

        headers = {'Content-Type': 'image/tiff'}
        with open(filePath, 'rb') as f:
            response = requests.post(api_url, files={'image': f}, headers=headers)
        root = self._get_valid_response(response)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.info(error_msg)
            return constants.RETURN_CODE_FAILURE
        
    @classmethod
    def bulk_create_customer(self, user_list):
        base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
        output_path = base_dir + '/webapp/statics/'
        outfile = open(output_path+"bulk_client_ucc.txt", "w")

        for i in range(len(user_list)):
            return_code = self.create_customer(user_list[i])
            outfile.write(user_list[i] + ", " + str(return_code))
            if i < len(user_list)-1:
                outfile.write("\r")
                
        outfile.close()
        return "/webapp/static/bulk_client_ucc.txt"

    def generate_aof_image(self, user_id):
        filePath = nse_iinform_generation.nse_investor_info_generator(user_id)
        return filePath

    def generate_bank_mandate(self, user_id, mandate_amount):
        kwargs = {'mandate_amount': mandate_amount}
        filePath = bank_mandate.generate_bank_mandate_tiff(user_id, **kwargs)
        return filePath
    
    def upload_bank_mandate(self, user_id, mandate_amount):
        kwargs = {'mandate_amount': mandate_amount}
        return self.upload_img(user_id, image_type="X", **kwargs)


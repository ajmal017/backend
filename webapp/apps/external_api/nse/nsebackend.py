from rest_framework import status

from external_api.nse import create_validate_nserequests
from external_api.nse import constants as nse_constants
from external_api import constants
from external_api import models
from external_api.exchange_backend import ExchangeBackend 
from profiles import models as pr_models
from core import utils as core_utils
from core import models as core_models
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
        super(NSEBackend, self).__init__(vendor_name)
        
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
            error_logger.error(constants.CONNECTION_ERROR + api_url)
        except requests.HTTPError:
            error_logger.error(constants.HTTP_ERROR + api_url)

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
            child_root = ET.fromstring(nse_constants.REQUEST_PURCHASE_CHILDTXN)
            return create_validate_nserequests.purchasetxnrequest(root, child_root, user_id, **kwargs)
        elif method_name == nse_constants.METHOD_REDEEMTXN:
            root = ET.fromstring(nse_constants.REQUEST_REDEEMTXN)
            child_root = ET.fromstring(nse_constants.REQUEST_REDEEM_CHILDTXN)
            return create_validate_nserequests.redeemtxnrequest(root, child_root, user_id, **kwargs)
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
                error_logger.error(error_msg)
            if createCustomerFlag:
                return constants.RETURN_CODE_FAILURE
            else:
                raise AttributeError

    def update_ucc(self, user_id, ucc):
        user_vendor = super(NSEBackend, self).update_ucc(user_id, ucc)
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
            return constants.RETURN_CODE_SUCCESS
        else:
            createFlag = False
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                if error_msg == nse_constants.NO_DATA_FOUND:
                    createFlag = True
                error_logger.info(error_msg)
            if createFlag:
                return constants.RETURN_CODE_FAILURE
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
            self.error_logger.error("IIN str: " + return_msg)
            iin_match = re.search('IIN\s*:\s*(.+)', return_msg)
            iin_customer_id = ""
            if iin_match:
                iin_customer_id = iin_match.group(1) 
            self.error_logger.error("IIN : " + str(iin_customer_id))
            self.update_ucc(user_id, iin_customer_id)
            return constants.RETURN_CODE_SUCCESS, None
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            error_string = ""
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_string += error_msg + " ; "
                self.error_logger.error(error_msg)
            return constants.RETURN_CODE_FAILURE, error_string

    def upload_aof_image(self, user_id):
        status = self.upload_img(user_id=user_id, image_type="A")
        if status == constants.RETURN_CODE_SUCCESS:
            self.update_aof_sent(user_id)
        return status

    def purchase_trxn(self, user_id, order_detail):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        kwargs = {'exchange_backend': self, "order" : order_detail}
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
                error_logger.error(error_msg)
            return constants.RETURN_CODE_FAILURE

    def redeem_trxn(self, user_id, grouped_redeem):
        """

        :param:
        :return:
        """
        error_logger = logging.getLogger('django.error')
        kwargs = {'exchange_backend': self, "redeem" : grouped_redeem}
        xml_request_body = self._get_request_body(nse_constants.METHOD_REDEEMTXN, user_id, **kwargs)
        root = self._get_data(nse_constants.METHOD_REDEEMTXN, xml_request_body=xml_request_body)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.error(error_msg)
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
            self.update_mandate_registered(user_id)
            return constants.RETURN_CODE_SUCCESS, None
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.error(error_msg)
            return constants.RETURN_CODE_FAILURE, None


    def upload_img(self, user_id, ref_no='', image_type='', **kwargs):
        error_logger = logging.getLogger('django.error')
        try:
            user_vendor = pr_models.UserVendor.objects.get(user__id=user_id, vendor__name=self.vendor_name)
        except Exception as e:
            error_logger.error("User vendor missing: " + user_id + " : " + self.vendor_name + " : " + str(e))
            return constants.RETURN_CODE_FAILURE
        
        queryString = "?BrokCode=" + nse_constants.NSE_NMF_BROKER_CODE + "&Appln_id=" + nse_constants.NSE_NMF_APPL_ID + \
                      "&Password=" + nse_constants.NSE_NMF_PASSWORD + "&CustomerID=" + user_vendor.ucc + "&Refno=" + ref_no + \
                      "&ImageType=" + image_type
        api_url = nse_constants.NSE_NMF_UPLOAD_BASE_API_URL + nse_constants.METHOD_UPLOADIMG + queryString
        filePath = ""
        if image_type == "A":
            filePath = self.generate_aof_image(user_id)
        elif image_type == "X":
            filePath = bank_mandate.generate_bank_mandate_tiff(user_id, **kwargs)

        headers = {'Content-Type': 'application/octet-stream'}
        with open(filePath, 'rb') as f:
            img_data = f.read()
            response = requests.request("POST", api_url, data=img_data, headers=headers)
        root = self._get_valid_response(response)
        return_code = root.find(nse_constants.SERVICE_RETURN_CODE_PATH).text
        if return_code == nse_constants.RETURN_CODE_SUCCESS:
            return constants.RETURN_CODE_SUCCESS
        else:
            error_responses = root.findall(nse_constants.SERVICE_RESPONSE_VALUE_PATH)
            error_logger.error("Response str: " + response.text)
            for error in error_responses:
                error_msg = error.find(nse_constants.SERVICE_RETURN_ERROR_MSG_PATH).text
                error_logger.error(error_msg)
            return constants.RETURN_CODE_FAILURE
        
    def bulk_create_customer(self, user_list):
        base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
        output_path = base_dir + '/webapp/static/'
        outfile = open(output_path+"bulk_client_ucc.txt", "w")

        for i in range(len(user_list)):
            return_code, error_string = self.create_customer(user_list[i])
            outfile.write(user_list[i] + ", " + str(return_code))
            if error_string:
                outfile.write(", " + error_string)
            if i < len(user_list)-1:
                outfile.write("\r")
                
        outfile.close()
        return "webapp/static/bulk_client_ucc.txt"

    def generate_aof_image(self, user_id):
        filePath = nse_iinform_generation.nse_investor_info_generator(user_id, self)
        return filePath

    def generate_bank_mandate(self, user_id, mandate_amount):
        kwargs = {'mandate_amount': mandate_amount, 'exchange_backend': self}
        filePath = bank_mandate.generate_bank_mandate_tiff(user_id, **kwargs)
        return filePath
    
    def upload_bank_mandate(self, user_id, mandate_amount):
        kwargs = {'mandate_amount': mandate_amount}
        return self.upload_img(user_id, image_type="X", **kwargs)
    
    def create_order(self, user_id, order_detail):
        return self.purchase_trxn(user_id, order_detail), None

    def generate_payment_link(self, transaction):
        error_logger = logging.getLogger('django.error')
        core_utils.convert_to_investor(transaction, self.get_vendor(), inlinePayment=True)
        try:
            order_detail = core_models.OrderDetail.objects.get(transaction=transaction, is_lumpsum=True)
        except Exception as e:
            error_logger.error("Failed to create orders: " + transaction.user.id + " : " + self.vendor_name + " : " + str(e))
            return None, constants.ORDERS_DONT_EXIST

        try:
            pr_models.UserVendor.objects.get(user__id=transaction.user.id, vendor__name=self.vendor_name)
        except Exception as e:
            error_logger.error("User vendor missing: " + transaction.user.id + " : " + self.vendor_name + " : " + str(e))
            return None, constants.USER_NOT_REGISTERED
        
        status = self.purchase_trxn(transaction.user.id, order_detail)
        
        if status == constants.RETURN_CODE_SUCCESS:
            return transaction.payment_link
        else:
            return None, constants.FAILED_TO_PUNCH_TRANSACTION
                
    def create_redeem(self, user_id, grouped_redeem):
        return self.redeem_trxn(user_id, grouped_redeem), None
    
        
from rest_framework import status

from external_api import constants
from external_api import models
from external_api.exchange_backend import ExchangeBackend
from profiles import models as pr_models
from profiles import constants as profile_constants
from external_api.bse import bank_mandate
from external_api.bse import bse_investor_info_generation
from external_api.bse import bulk_upload
from external_api.bse import xsip_registration

import os
import re
import pdb
from api import utils as api_utils
import xml.etree.ElementTree as ET
import requests
import logging

class BSEBackend(ExchangeBackend):
    """
    A wrapper that manages the BSE  Backend
    """
    def __init__(self, vendor_name):
        super(BSEBackend, self).__init__(vendor_name)

    def create_customer(self, user_id):
        return constants.RETURN_CODE_FAILURE
    
    def upload_aof_image(self, user_id):
        return constants.RETURN_CODE_FAILURE
    
    def purchase_trxn(self, user_id):
        """

        :param:
        :return:
        """
        return constants.RETURN_CODE_FAILURE

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

    def generate_bank_mandate(self, user_id, bank_mandate_instance):
        return bank_mandate.generate_bank_mandate_pdf(user_id, bank_mandate_instance)

    def upload_bank_mandate(self, user_id):
        return constants.RETURN_CODE_FAILURE
    
    def generate_bank_mandate_registration(self, user_id, bank_mandate_instance):
        file_path = bank_mandate.generate_bank_mandate_file(user_id, bank_mandate_instance)
        if file_path and bank_mandate_instance.mandate_registered == False:
            self.update_mandate_registered(bank_mandate_instance)
        return constants.RETURN_CODE_SUCCESS, file_path

    def create_order(self, user_id, order_detail):
        return constants.RETURN_CODE_SUCCESS, bulk_upload.generate_order_pipe_file(user_id, order_detail,self)
    
    def generate_payment_link(self, transaction,web=False):
        return transaction.url_hashed(web), constants.RETURN_CODE_SUCCESS 
    
    def create_redeem(self, user_id, grouped_redeem):
        return constants.RETURN_CODE_SUCCESS, bulk_upload.generate_redeem_pipe_file(user_id, grouped_redeem)

    def create_xsip_order(self, user_id, order_detail):
        return constants.RETURN_CODE_SUCCESS, xsip_registration.generate_order_pipe_file(user_id, order_detail,self)
    
    def create_xsip_cancellation(self,user,portfolio_item):
        return constants.RETURN_CODE_SUCCESS, bulk_upload.generate_sip_cancellation_pipe_file(user, portfolio_item)

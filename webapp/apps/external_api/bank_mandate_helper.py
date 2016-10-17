from profiles import models, utils
from external_api import helpers

from . import constants as cons
import os
from datetime import date
import logging

class BankMandateHelper(object):
    error_logger = logging.getLogger('django.error')
    
    def get_investor_mandate_amount(self, sip_amount):
        """
        :return: The total amount to be used to fill investor pdf 
        """
        mandate_amount = max(sip_amount*2, cons.DEFAULT_BANK_MANDATE_AMOUNT)
        
        if mandate_amount > cons.DEFAULT_BANK_MANDATE_AMOUNT:
            if mandate_amount <= cons.DEFAULT_BANK_MANDATE_AMOUNT_NEXT:
                mandate_amount = cons.DEFAULT_BANK_MANDATE_AMOUNT_NEXT
            else:
                amount_remainder = mandate_amount%10000
                if amount_remainder > 0:
                    mandate_amount = (mandate_amount - amount_remainder) + 10000
            
        return mandate_amount

    def get_latest_mandate(self, user, mandate_vendor):
        latest_mandate = models.UserBankMandate.objects.filter(user=user, vendor=mandate_vendor).latest('mandate_start_date')
        return latest_mandate
                
    def create_new_mandate(self, user, order_detail, vendor, mandate_amount):
        bank_mandate = None
        try:
            bank_mandate = models.UserBankMandate.objects.create(user=user, vendor=vendor, mandate_start_date=date.today(), 
                                              mandate_amount=mandate_amount, 
                                              mandate_bank_details=user.investorbankdetails)
            if bank_mandate and order_detail:
                order_detail.bank_mandate = bank_mandate
                order_detail.save()
        except Exception as e:
            self.error_logger.error("Error creating mandate: " + str(e))
        return bank_mandate
        
    def is_new_mandate_required(self, user, order_detail, create_new=False):
        if not order_detail or order_detail.bank_mandate:
            return False, None

        if order_detail.bank_mandate:
            return False, order_detail.bank_mandate
        
        need_mandate = False
        mandate_vendor = order_detail.vendor
        
        if not mandate_vendor:
            mandate_vendor = helpers.get_exchange_vendor_helper().get_active_vendor()
        
        latest_mandate = self.get_latest_mandate(user, mandate_vendor)
        
        if not latest_mandate:
            need_mandate = True
        
        order_sip_amount = utils.get_order_sip_amount(user, order_detail)
         
        if latest_mandate:
            current_mandate_sip_amount = utils.get_mandate_total_sip_amount(user, latest_mandate)
            if latest_mandate.mandate_amount< (order_sip_amount + current_mandate_sip_amount):
                need_mandate = True

        if need_mandate:
            mandate_amount = self.get_investor_mandate_amount(order_sip_amount)
            mandate = self.create_new_mandate(self, user, order_detail, mandate_vendor, mandate_amount)
            return True, mandate        
    
    def get_current_mandate(self, user):
        mandate_vendor = helpers.get_exchange_vendor_helper().get_active_vendor()
        latest_mandate = self.get_latest_mandate(user, mandate_vendor)

        if not latest_mandate:
            mandate_amount = self.get_investor_mandate_amount(0)
            latest_mandate = self.create_new_mandate(self, user, None, mandate_vendor, mandate_amount)

        return latest_mandate


from abc import ABC
from profiles import models as pr_models
from external_api import models as eapi_models
import logging


class ExchangeBackend(ABC):
    def __init__(self, vendor_name):
        super(ABC, self).__init__()
        self.vendor_name = vendor_name
        self.vendor = None

    @classmethod
    def create_customer(cls, user_id):
        return NotImplementedError

    @classmethod
    def bulk_create_customer(cls, user_list):
        return NotImplementedError

    @classmethod
    def generate_aof_image(cls, user_id):
        return NotImplementedError
    
    @classmethod
    def upload_aof_image(cls, user_id):
        return NotImplementedError
    
    def update_ucc(self, user_id, ucc):
        logger = logging.getLogger('django.error')
        try:
            user = pr_models.User.objects.get(id=user_id)
            if not self.vendor:
                self.vendor = eapi_models.Vendor.objects.get(name=self.vendor_name)
            user_vendor, created = pr_models.UserVendor.objects.update_or_create(user=user, vendor=self.vendor, defaults={'ucc':ucc})
            return user_vendor
        except Exception as e:
            logger.error("Error updating ucc: " + str(e))
        
        return None
    
    def get_vendor(self):
        logger = logging.getLogger('django.error')
        try:
            if not self.vendor:
                self.vendor = eapi_models.Vendor.objects.get(name=self.vendor_name)
        except Exception as e:
            logger.error("Error retrieving vendor: " + str(e))
        
        return self.vendor
        
    def update_mandate_registered(self, bank_mandate_instance):

        logger = logging.getLogger('django.error')
        try:
            bank_mandate_instance.mandate_registered = True
            bank_mandate_instance.save()
            return bank_mandate_instance
        except Exception as e:
            logger.error("Error updating ucc: " + str(e))
        return None

    def update_aof_sent(self, user_id):

        logger = logging.getLogger('django.error')
        try:
            user = pr_models.User.objects.get(id=user_id)
            if not self.vendor:
                self.vendor = eapi_models.Vendor.objects.get(name=self.vendor_name)
            user_vendor = pr_models.UserVendor.objects.get(user=user, vendor=self.vendor)
            user_vendor.tiff_mailed = True
            user_vendor.save()
            return user_vendor
        except Exception as e:
            logger.error("Error updating ucc: " + str(e))
        return None
    
    def generate_bank_mandate(self, user_id, bank_mandate):
        return NotImplementedError

    def upload_bank_mandate(self, user_id):
        return NotImplementedError
    
    def generate_bank_mandate_registration(self, user_id, bank_mandate):
        return NotImplementedError
    
    def create_order(self, user_id, order_detail):
        return NotImplementedError

    def generate_payment_link(self, transaction):
        return NotImplementedError

    def create_redeem(self, user_id, grouped_redeem):
        return NotImplementedError


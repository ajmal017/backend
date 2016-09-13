# -*- coding: utf-8 -*-

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.fields import HStoreField

from djutil.models import TimeStampedModel

from . import constants, utils

from external_api import constants as external_cons 

from enum import IntEnum


class Transaction(TimeStampedModel):
    """
    Stores all the params to be sent in a billdesk request.
    Excluding Return url which is a constant
    """
    class Status(IntEnum):
        """
        this is used for the choices of  status for transaction
        """
        Pending = 0
        Success = 1
        Failure = 2

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    source_id = models.CharField(_('Source Id'), max_length=15, default=constants.UNKNOWN)
    biller_id = models.CharField(_('Biller Id'), max_length=20, default=constants.UNKNOWN)
    txn_amount = models.FloatField(_('Transaction Amount'), max_length=8)
    txt_bank_id = models.CharField(_('Bank Name'), max_length=3)
    additional_info_1 = models.CharField(_('Order Number'), max_length=100, unique=True)
    additional_info_2 = models.CharField(_('Folio Number'), max_length=100, default=external_cons.MEMBER_CODE)
    additional_info_3 = models.CharField(_('User Login Id/CRN'), max_length=100, default=constants.UNKNOWN)
    additional_info_4 = models.CharField(_('Distributer Id'), max_length=100, default=constants.DISTRIBUTOR_ID)

    # additional_info_5 = models.CharField(_('BankId-AccountType-Debit Account No'), max_length=100, default='NA-NA-NA')

    additional_info_5 = models.CharField(_('AMC Id '), max_length=100, default=constants.BSE)
    additional_info_6 = models.CharField(_('Fund Type'), max_length=100, default=constants.NONLIQUID)
    additional_info_7 = models.CharField(_('Investor Type/Tax Status'), max_length=100,
                                         default=constants.DEFAULT_INVESTOR_TYPE)
    additional_info_8 = models.DateTimeField(_('Transaction Time'), max_length=100, auto_now_add=True)
    additional_info_9 = models.CharField(_('Scheme Code'), max_length=100, default=constants.BSE)
    additional_info_10 = models.CharField(_('Sender SIP Registration No.'), max_length=100, default=constants.UNKNOWN)
    additional_info_11 = models.CharField(_('Transaction Type'), max_length=100, default=constants.LUMPSUM)
    additional_info_12 = models.CharField(_('AMC Code'), max_length=100, default=constants.UNKNOWN)
    txt_merchant_user_ref_no = models.CharField(_('Bank Account Number'), max_length=17, default=None, null=True,
                                                blank=True)
    txn_reference_no = models.CharField(_('Transaction Reference Number'), max_length=100, default=None, null=True,
                                        blank=True)
    txn_status = models.IntegerField(choices=[(x.value, x.name) for x in Status], default=Status.Pending.value)
    auth_status = models.CharField(_('AuthStatus'), max_length=10, default=None, null=True, blank=True)
    merchant_id = models.CharField(_('Merchant Id'), max_length=100, default=constants.MERCHANT_ID, null=True,
                                   blank=True)
    customer_id = models.CharField(_('Customer Id'), unique=True, max_length=100)
    product_id = models.CharField(_('Product Id'), max_length=100, default=None, null=True, blank=True)
    txn_time = models.DateTimeField(_('Transaction Time'), max_length=100, auto_now_add=False, default=None, null=True, blank=True)
    response_string = HStoreField(blank=True, null=True)
    request_string = HStoreField(blank=True, null=True)

    def __str__(self):
        return str(self.id) + " " + str(self.user) + " " + str(self.additional_info_1 )

    def get_message(self):
        """
        :returns: A string to be hashed
        According to the documentation provided tries to recreate the string below

        FINASKUS|26|12011000051973|5.00|HDF|NA|NA|INR|DIRECT|R|finaskus|NA|NA|F|NA|NA|ARN-87554|BSE|LIQUID|RESIDENT-BSE-NA-L-NA-NA|20130706125634|http://219.64.14.241:100/billdesk_response.aspx
        """
        account_number = self.user.investorbankdetails.account_number
        # account_number = "NA"
        parts = [self.merchant_id, self.additional_info_1, account_number, str(self.txn_amount),
                 self.txt_bank_id, "NA", "NA", "INR", self.product_id, "R", "finaskus" , "NA", "NA", "F",
                 self.additional_info_2, self.additional_info_3, self.additional_info_4, self.additional_info_5,
                 self.additional_info_6, self.concated_additional_info(),
                 utils.date_time_format(self.additional_info_8, self.txn_amount), constants.RU]
        return "|".join(parts)

    def concated_additional_info(self):
        """
        :return: A string to be sent to second last params for message to be hashed
        According to documentation

        additional_info7-additional_info9-additonal_info10-additional_info11-additional_info12-sourceid
        RESIDENT-BSE-NA-L-NA-NA
        """
        parts = [self.additional_info_7, self.additional_info_9, self.additional_info_10, self.additional_info_11,
                 self.additional_info_12, self.source_id]
        return "-".join(parts)

    def hash(self):
        """

        :return:hashed value
        """
        code = self.get_message()
        return utils.get_billdesk_checksum(code, settings.BILLDESK_SECRET_KEY)

    def url_hashed(self):
        """

        :return: constant ru|hash value
        """
        parts = [self.get_message(), self.hash()]
        return "|".join(x for x in parts if x)





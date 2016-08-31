# -*- coding: utf-8 -*-

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator

from djutil.models import TimeStampedModel

from . import constants

from enum import IntEnum


class SMS(TimeStampedModel):
    """
    Storing a log for any sms that we tried to send
    failure_code is it was not able to successfully send the message
    """
    content = models.TextField(verbose_name=_(u'content'), help_text=_(u'SMS content'))
    to = models.CharField(max_length=32, verbose_name=_(u'receiver'), db_index=True)
    failure_code = models.TextField(verbose_name=_(u'failure code'), default=None, blank=True, null=True)
    mid = models.TextField(verbose_name=_(u'Message ID'), blank=True, null=True,
                           help_text=_(u'Message ID is used to track the delivery'))
    operator = models.IntegerField(choices=constants.OPERATOR_CHOICES, default=constants.OPERATOR_UNKNOWN,
                                   verbose_name=_(u'Operator Used'))

    class Meta:
        get_latest_by = 'modified_at'
        ordering = ('-modified_at',)
        verbose_name = _(u'SMS')
        verbose_name_plural = _(u'SMSes')

    def __str__(self):
        return u'SMS: "%s" this "%s"' % (self.to, self.content)


class Pincode(models.Model):
    """

    """
    pincode = models.IntegerField(unique=False)
    city = models.CharField(max_length=512, default="")
    state = models.CharField(max_length=512, default="")

    def __str__(self):
        return str(self.city) + " " + str(self.state) + " " + str(self.pincode)


class VerifiablePincode(TimeStampedModel):
    """
    Storing all the list of pincodes where doorstep delivery will be available
    """
    # TODO : make an upload utility for the pincode
    pincode = models.ManyToManyField(Pincode, verbose_name=_(u'pincode'))

    class Meta:
        get_latest_by = 'modified_at'
        ordering = ('modified_at',)
        verbose_name = _(u'VerifiablePincode')
        verbose_name_plural = _(u'VerifiablePincodes')

    def __str__(self):
        return str(self.pincode)


class BankDetails(models.Model):
    """
    Class to save details of a bank
    """
    name = models.CharField(max_length=100, blank=False, null=False)
    ifsc_regex = RegexValidator(regex='^[0-9A-Z]{11}', message=_(
        "IFC CODE MUST BE PUT IN FORMAT: 'ABHY0065001'. Up to 11 digits allowed."))
    ifsc_code = models.CharField(max_length=11, validators=[ifsc_regex], unique=True, blank=False, null=False)
    micr_code = models.CharField(max_length=10, blank=True, null=True)
    bank_branch = models.CharField(max_length=100, blank=False, null=False)
    address = models.TextField(blank=False, null=False)
    phone_number = models.CharField(max_length=12, blank=True, null=True)
    city = models.CharField(max_length=100, blank=False, null=False)
    district = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    updated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.ifsc_code)


# class OrderEntryParam(models.Model):
#     """
#
#     """
#     class TransactionCode(Enum):
#         New = 'NEW'
#         Modification = 'MOD'
#         Cancellation = 'CXL'
#
#     class BuySell(Enum):
#         Redemption = 'R'
#         Purchase = 'P'
#
#     class DpTxn(Enum):
#         Physical = 'P'
#         NSDL = 'N'
#         CSDL = 'C'
#
#     transaction_code = models.CharField(max_length=3, choices=[(x.value, x.name.title()) for x in TransactionCode])
#     unique_refrence_number = models.CharField(max_length=19)
#     order_id = models.CharField(max_length=8, null=True, blank=True, default=None)
#     user_id = models.CharField(max_length=5)
#     member_id = models.CharField(max_length=20)
#     client_code = models.CharField(max_length=20)
#     scheme_cd = models.CharField(max_length=20)
#     buy_sell = models.CharField(max_length=1, choices=[(x.value, x.name.title()) for x in BuySell])
#     buy_sell_type = models.CharField(max_length=10)
#     dp_txn = models.CharField(max_length=10, choices=[(x.value, x.name.title()) for x in DpTxn])
#     amount = models.FloatField(default="")
#     qty = models.FloatField(default="")
#     all_redeem = models.CharField(max_length=1)
#     folio_no = models.CharField(max_length=20, null=True, blank=True, default=None)
#     remarks = models.CharField(max_length=225, null=True, blank=True, default="")
#     kyc_status = models.CharField(max_length=1)
#     ref_no = models.CharField(max_length=20, null=True, blank=True, default=None)
#     sub_br_code = models.CharField(max_length=15)
#     euin = models.CharField(max_length=20)
#     euin_flag = models.CharField(max_length=1)
#     min_redeem = models.CharField(max_length=1)
#     dpc = models.CharField(max_length=1)
#     ip_add = models.CharField(max_length=20, null=True, blank=True, default=None)
#     # password = models.CharField(max_length=250)
#     pass_key = models.CharField(max_length=10)
#     param_1 = models.CharField(max_length=10, null=True, blank=True, default=None)
#     param_2 = models.CharField(max_length=10, null=True, blank=True, default=None)
#     param_3 = models.CharField(max_length=10, null=True, blank=True, default=None)
#
#
# class OrderEntryParamResponse(models.Model):
#     """
#
#     """
#     transaction_code = models.CharField(max_length=3, null=True, blank=True, default=None)
#     unique_refrence_number = models.CharField(max_length=19, null=True, blank=True, default=None)
#     order_number = models.CharField(max_length=8, null=True, blank=True, default=None)
#     user_id = models.CharField(max_length=5, null=True, blank=True, default=None)
#     member_id = models.CharField(max_length=20, null=True, blank=True, default=None)
#     client_code = models.CharField(max_length=20, null=True, blank=True, default=None)
#     bse_remarks = models.TextField(max_length=1000, null=True, blank=True, default="")
#     success_flag = models.CharField(max_length=1, null=True, blank=True, default=None)

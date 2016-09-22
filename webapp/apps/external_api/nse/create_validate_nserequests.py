import xml.etree.ElementTree as ET

from profiles import models
from external_api.models import Pincode
from . import constants
from external_api import constants as api_constants

from datetime import datetime


def getiinrequest(root, user_id):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)

    investor_dict = {
        constants.TAX_STATUS_XPATH: user.tax_status,
        constants.HOLD_NATURE_XPATH: None,  # TODO
        constants.EXEMPT_FLAG_XPATH: 'N',
        constants.FH_PAN_XPATH: investor.pan_number,
        constants.JH1_PAN_XPATH: None,
        constants.JH1_EXEMPT_FLAG_XPATH: None,
        constants.JH2_PAN_XPATH: None,
        constants.JH2_EXEMPT_FLAG_XPATH: None,
        constants.GUARD_PAN_XPATH: None
    }

    for key, value in investor_dict.items():
        if value is None:
            investor_dict[key] = ""
        root.find(key).text = value

    return root


def createcustomerrequest(root, user_id):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    nominee_address = nominee.nominee_address
    if nominee.nominee_address == None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address

    title=None
    if user.gender == 'M':
        title = "Mr."
    elif user.gender == 'F' & user.marital_status == 'Married':
        title = "Mrs."
    else :
        title = "Ms."



    investor_dict = {
        constants.TITLE_XPATH: title,
        constants.INV_NAME_XPATH: investor.applicant_name,
        constants.PAN_XPATH: investor.pan_number,
        constants.VALID_PAN_XPATH: 'Y',
        constants.EXEMPTION_XPATH: 'N',
        constants.EXEMPT_CATEGORY_XPATH: None, # TODO
        constants.EXEMPT_REF_NO_XPATH: None, # TODO
        constants.DOB_XPATH: user.dob,
        constants.HOLD_NATURE_XPATH: None, # TODO
        constants.TAX_STATUS_XPATH: user.tax_status,
        constants.KYC_XPATH: user.kyc_accepted,
        constants.OCCUPATION_XPATH: investor.occupation_type, # TODO : Refer master services for 2 letter occupation code
        constants.MFU_CAN_XPATH: None, # TODO
        constants.DP_ID_XPATH: None, # TODO
        constants.FATHER_NAME_XPATH: investor.father_name,
        constants.MOTHER_NAME_XPATH: None, # TODO
        constants.TRXN_ACCEPTANCE_XPATH: "ALL",
        constants.ADDR1_XPATH: contact.communication_address.address_line_1,
        constants.ADDR2_XPATH: contact.communication_address.address_line_2,
        constants.ADDR3_XPATH: contact.communication_address.nearest_landmark,
        constants.CITY_XPATH: contact.communication_address.pincode.city,
        constants.STATE_XPATH: contact.communication_address.pincode.state,
        constants.PINCODE_XPATH: contact.communication_address.pincode.pincode,
        constants.COUNTRY_XPATH: api_constants.INDIA,
        constants.MOBILE_XPATH: contact.phone_number,
        constants.RES_PHONE_XPATH: None,
        constants.OFF_PHONE_XPATH: None,
        constants.OFF_FAX_XPATH: None,
        constants.RES_FAX_XPATH: None,
        constants.EMAIL_XPATH: contact.email,
        constants.NRI_ADDR1_XPATH: None,
        constants.NRI_ADDR2_XPATH: None,
        constants.NRI_ADDR3_XPATH: None,
        constants.NRI_CITY_XPATH: None,
        constants.NRI_STATE_XPATH: None,
        constants.NRI_PINCODE_XPATH: None,
        constants.NRI_COUNTRY_XPATH: None,
        constants.BANK_NAME_XPATH: investor_bank.ifsc_code.name,
        constants.ACC_NO_XPATH: investor_bank.account_number,
        constants.ACC_TYPE_XPATH: investor_bank.account_type,
        constants.IFSC_CODE_XPATH: investor_bank.ifsc_code.ifsc_code,
        constants.BRANCH_NAME_XPATH: investor_bank.ifsc_code.bank_branch,
        constants.BRANCH_ADDR1_XPATH: investor_bank.ifsc_code.address,
        constants.BRANCH_ADDR2_XPATH: None,
        constants.BRANCH_ADDR3_XPATH: None,
        constants.BRANCH_CITY_XPATH: investor_bank.ifsc_code.city,
        constants.BRANCH_PINCODE_XPATH: None, #TODO
        constants.BRANCH_COUNTRY_XPATH: None, #TODO
        constants.JH1_NAME_XPATH: None,
        constants.JH1_PAN_XPATH: None,
        constants.JH1_VALID_PAN_XPATH: None,
        constants.JH1_EXEMPTION_XPATH: None,
        constants.JH1_EXEMPT_CATEGORY_XPATH: None,
        constants.JH1_EXEMPT_REF_NO_XPATH: None,
        constants.JH1_DOB_XPATH: None,
        constants.JH1_KYC_XPATH: None,
        constants.JH2_NAME_XPATH: None,
        constants.JH2_PAN_XPATH: None,
        constants.JH2_VALID_PAN_XPATH: None,
        constants.JH2_EXEMPTION_XPATH: None,
        constants.JH2_EXEMPT_CATEGORY_XPATH: None,
        constants.JH2_EXEMPT_REF_NO_XPATH: None,
        constants.JH2_DOB_XPATH: None,
        constants.JH2_KYC_XPATH: None,
        constants.NO_OF_NOMINEE_XPATH: None,
        constants.NOMINEE1_TYPE_XPATH: None,
        constants.NOMINEE1_NAME_XPATH: None,
        constants.NOMINEE1_DOB_XPATH: None,
        constants.NOMINEE1_ADDR1_XPATH: None,
        constants.NOMINEE1_ADDR2_XPATH: None,
        constants.NOMINEE1_ADDR3_XPATH: None,
        constants.NOMINEE1_CITY_XPATH: None,
        constants.NOMINEE1_STATE_XPATH: None,
        constants.NOMINEE1_PINCODE_XPATH: None,
        constants.NOMINEE1_RELATION_XPATH: None,
        constants.NOMINEE1_PERCENT_XPATH: None,
        constants.NOMINEE1_GUARD_NAME_XPATH: None,
        constants.NOMINEE1_GUARD_PAN_XPATH: None,
        constants.NOMINEE2_TYPE_XPATH: None,
        constants.NOMINEE2_NAME_XPATH: None,
        constants.NOMINEE2_DOB_XPATH: None,
        constants.NOMINEE2_RELATION_XPATH: None,
        constants.NOMINEE2_PERCENT_XPATH: None,
        constants.NOMINEE2_GUARD_NAME_XPATH: None,
        constants.NOMINEE2_GUARD_PAN_XPATH: None,
        constants.NOMINEE3_TYPE_XPATH: None,
        constants.NOMINEE3_NAME_XPATH: None,
        constants.NOMINEE3_DOB_XPATH: None,
        constants.NOMINEE3_RELATION_XPATH: None,
        constants.NOMINEE3_PERCENT_XPATH: None,
        constants.NOMINEE3_GUARD_NAME_XPATH: None,
        constants.NOMINEE3_GUARD_PAN_XPATH: None,
        constants.GUARD_NAME_XPATH: None,
        constants.GUARD_PAN_XPATH: None,
        constants.GUARD_VALID_PAN_XPATH: None,
        constants.GUARD_EXEMPTION_XPATH: None,
        constants.GUARD_EXEMPT_CATEGORY_XPATH: None,
        constants.GUARD_PAN_REF_NO_XPATH: None,
        constants.GUARD_DOB_XPATH: None
    }

    for key, value in investor_dict.items():
        if value is None:
            investor_dict[key] = ""
        if value is True:
            investor_dict[key] = "Y"
        if value is False:
            investor_dict[key] = "N"
        root.find(key).text = value

    return root


def purchasetxnrequest(root, user_id):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    nominee_address = nominee.nominee_address
    if nominee.nominee_address == None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address

    investor_dict = {
        constants.IIN_XPATH: None,
        constants.SUB_TRXN_TYPE_XPATH: None,
        constants.POA_XPATH: None,
        constants.TRXN_ACCEPTANCE_XPATH: None,
        constants.DEMAT_USER_XPATH: None,
        constants.DP_ID_XPATH: None,
        constants.BANK_NAME_XPATH: None,
        constants.AC_NO_XPATH: None,
        constants.IFSC_CODE_XPATH: None,
        constants.SUB_BROKER_ARN_CODE_XPATH: None,
        constants.SUB_BROKER_CODE_XPATH: None,
        constants.EUIN_OPTED_XPATH: None,
        constants.TRXN_EXECUTION_XPATH: None,
        constants.REMARKS_XPATH: None,
        constants.PAYMENT_MODE_XPATH: None,
        constants.BILLDESK_BANK_XPATH: None,
        constants.INSTRM_BANK_XPATH: None,
        constants.INSTRM_AC_NO_XPATH: None,
        constants.INSTRM_NO_XPATH: None,
        constants.INSTRM_AMOUNT_XPATH: None,
        constants.INSTRM_DATE_XPATH: None,
        constants.INSTRM_BRANCH_XPATH: None,
        constants.INSTRM_CHARGES_XPATH: None,
        constants.MICR_XPATH: None,
        constants.RTGS_CODE_XPATH: None,
        constants.NEFT_IFSC_XPATH: None,
        constants.ADVISIORY_CHARGE_XPATH: None,
        constants.CHEQUE_DEPOSIT_MODE_XPATH: None,
        constants.DD_CHARGE_XPATH: None,
        constants.DEBIT_AMOUNT_TYPE_XPATH: None,
        constants.NOMINEE_FLAG_XPATH: None,
        constants.NO_OF_NOMINEE_XPATH: None,
        constants.NOMINEE1_NAME_XPATH: None,
        constants.NOMINEE1_DOB_XPATH: None,
        constants.NOMINEE1_ADDR1_XPATH: None,
        constants.NOMINEE1_ADDR2_XPATH: None,
        constants.NOMINEE1_ADDR3_XPATH: None,
        constants.NOMINEE1_CITY_XPATH: None,
        constants.NOMINEE1_STATE_XPATH: None,
        constants.NOMINEE1_PINCODE_XPATH: None,
        constants.NOMINEE1_RELATION_XPATH: None,
        constants.NOMINEE1_PERCENT_XPATH: None,
        constants.NOMINEE1_GUARD_NAME_XPATH: None,
        constants.NOMINEE1_GUARD_PAN_XPATH: None,
        constants.NOMINEE2_NAME_XPATH: None,
        constants.NOMINEE2_DOB_XPATH: None,
        constants.NOMINEE2_RELATION_XPATH: None,
        constants.NOMINEE2_PERCENT_XPATH: None,
        constants.NOMINEE2_GUARD_NAME_XPATH: None,
        constants.NOMINEE3_NAME_XPATH: None,
        constants.NOMINEE3_DOB_XPATH: None,
        constants.NOMINEE3_RELATION_XPATH: None,
        constants.NOMINEE3_PERCENT_XPATH: None,
        constants.NOMINEE3_GUARD_NAME_XPATH: None,
        constants.NOMINEE3_GUARD_PAN_XPATH: None,
        constants.SIP_MICR_NO_XPATH: None,
        constants.SIP_BANK_XPATH: None,
        constants.SIP_ACC_NO_XPATH: None,
        constants.SIP_AC_TYPE_XPATH: None,
        constants.SIP_IFSC_CODE_XPATH: None,
        constants.UMRN_XPATH: None,
        constants.ACH_AMT_XPATH: None,
        constants.ACH_FROM_DATE_XPATH: None,
        constants.ACH_END_DATE_XPATH: None,
        constants.UNTIL_CANCELLED_XPATH: None,
        constants.RETURN_PAYMENT_FLAG_XPATH: None,
        constants.CLIENT_CALLBACK_URL_XPATH: None,
        constants.TRANS_COUNT_XPATH: None,
        constants.AMC_XPATH: None,
        constants.FOLIO_XPATH: None,
        constants.AMOUNT_XPATH: None,
        constants.SIP_FROM_DATE_XPATH: None,
        constants.SIP_END_DATE_XPATH: None,
        constants.SIP_FREQ_XPATH: None,
        constants.SIP_AMOUNT_XPATH: None,
        constants.SIP_PERIOD_DAY_XPATH: None
    }

    for key, value in investor_dict.items():
        if value is None:
            investor_dict[key] = ""
        root.find(key).text = value

    return root


def achmandateregistrationsrequest(root, user_id):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    contact = models.ContactInfo.objects.get(user=user)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    curr_date = datetime.now()

    nominee_address = nominee.nominee_address
    if nominee.nominee_address == None:
        blank_pincode = Pincode(None, None, None)
        blank_address = models.Address(None, None, None, None)
        blank_address.pincode = blank_pincode
        nominee.nominee_address = blank_address

    investor_dict = {
        constants.IIN_XPATH: None,
        constants.ACC_NO_XPATH: None,
        constants.ACC_TYPE_XPATH: None,
        constants.IFSC_CODE_XPATH: None,
        constants.BANK_NAME_XPATH: None,
        constants.MICR_NO_XPATH: None,
        constants.UC_XPATH: None,
        constants.ACH_FROM_DATE_XPATH: None,
        constants.ACH_TO_DATE_XPATH: None,
        constants.ACH_AMOUNT_XPATH: None
    }

    for key, value in investor_dict.items():
        if value is None:
            investor_dict[key] = ""
        root.find(key).text = value

    return root

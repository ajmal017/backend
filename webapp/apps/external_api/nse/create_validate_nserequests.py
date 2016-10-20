import xml.etree.ElementTree as ET

from profiles import models
from profiles import constants as profile_constants
from core import models as core_models
from external_api.models import Pincode
from . import constants
from external_api import constants as api_constants
from external_api.nse import bankcodes
from payment import constants as payment_constants
from datetime import datetime


def getValidRequest(investor_dict, root):
    for key, value in investor_dict.items():
        if value is None:
            investor_dict[key] = ''
        if value is True:
            investor_dict[key] = "Y"
        if value is False:
            investor_dict[key] = "N"

    for key, value in investor_dict.items():
        if value not in ("", "Y", "N"):
            investor_dict[key] = str(value).upper()
        root.find(key).text = investor_dict[key]

    return ET.tostring(root, encoding="us-ascii", method="xml")

def getValidRequestWithMultipleChildren(investor_dict, child_items, root, child_root):
    getValidRequest(investor_dict, root)
    
    child_str = ET.tostring(child_root, encoding="us-ascii", method="xml")
    for child_dict in child_items:
        child_root = ET.fromstring(child_str)
        getValidRequest(child_dict, child_root)
        root.extend(child_root)
        
    return ET.tostring(root, encoding="us-ascii", method="xml")

def changeDobFormat(dob):
    return dob.strftime('%d-%b-%Y')

def get_amc_code(code):
    AMC_CODE_MAP = {
        "AXIS MUTUAL FUND":"128",
        "BNP PARIBAS MUTUAL FUND":"M",
        "BOI AXA MUTUAL FUND":"116",
        "BARODA PIONEER ASSET MANAGEMENT COMPANY LIMITED":"107",
        "BIRLA SUN LIFE MUTUAL FUND":"B",
        "CANARA ROBECO MUTUAL FUND":"101",
        "DHFL PRAMERICA ASSET MANAGERS PRIVATE LIMITED":"129",
        "DSP BLACK ROCK MUTUAL FUND":"D",
        "EDELWEISS MUTUAL FUND":"118",
        "FRANKLIN TEMPLETON MUTUAL FUND":"FTI",
        "HDFC MUTUAL FUND":"H",
        "ICICI PRUDENTIAL MUTUAL FUND":"P",
        "IDBI MUTUAL FUND":"135",
        "IDFC MUTUAL FUND":"G",
        "INVESCO MUTUAL FUND":"120",
        "JPMORGAN MUTUAL FUND":"J",
        "KOTAK MUTUAL FUND":"K",
        "L AND T MUTUAL FUND":"F",
        "LIC NOMURA MUTUAL FUND":"102",
        "MIRAE ASSEST MUTUAL FUND":"117",
        "MOTILAL OSWAL MUTUAL FUND":"127",
        "PEERLESS MUTUAL FUND":"PLF",
        "PPFAS MUTUAL FUND":"PP",
        "PRINCIPAL MUTUAL FUND":"103",
        "QUANTUM MUTUAL FUND":"123",
        "RELIANCE MUTUAL FUND":"RMF",
        "SBI MUTUAL FUND":"L",
        "SHRIRAM MUTUAL FUND":"SH",
        "SUNDARAM MUTUAL FUND":"S",
        "TATA MUTUAL FUND.":"T",
        "UTI MUTUAL FUND":"108",
    }
    
    return AMC_CODE_MAP.get(code, None)

    
def get_occupation_code(code):
    """
    :param code: Our mapping for the occupation
    :return: Occupation code according to BSE standards

    Routes our model mapping to BSE mapping as shown below

    CLIENT_OCCUPATION_CODE_MAP = {
    "Business": "01",
    "Services": "02",
    "Professional": "03",
    "Agriculture": "04",
    "Retired": "05",
    "Housewife": "06",
    "Student": "07",
    "Others": "08"
    }
    """

    OCCUPATION_MAP = {
        profile_constants.BUSINESS: '1',
        profile_constants.PRIVATE_SECTOR: '2',
        profile_constants.PUBLIC_SECTOR: '2',
        profile_constants.GOVERNMENT: '2',
        profile_constants.PROFESSIONAL: '3',
        profile_constants.AGRICULTURE: '4',
        profile_constants.RETIRED: '5',
        profile_constants.HOUSEWIFE: '6',
        profile_constants.STUDENT: '7',
        profile_constants.OTHER: '8',
        profile_constants.FOREX_DEALER: '8',
    }

    return OCCUPATION_MAP.get(code, "8")

def get_country_code(code):
    code = code.title()
    
    COUNTRY_CODE_MAP = {
                        "Australia" : "AUS",
                        "BAHRAIN" : "BHR",
                        "Bangladesh" : "BAN",
                        "Belgium" : "BEL",
                        "Brazil" : "BRA",
                        "Brunei Darussalam" : "BRN",
                        "CANADA" : "CAN",
                        "China" : "CHN",
                        "DOMINICA" : "DMA",
                        "England" : "ENG",
                        "Ethiopia" : "ETH",
                        "Europe" : "EUR",
                        "Fiji" : "FJI",
                        "Finland" : "FIN",
                        "France" : "FRA",
                        "Germany" : "GER",
                        "Ghana" : "GHA",
                        "HONG KONG" : "HKG",
                        "India" : "IND",
                        "Indonesia" : "INA",
                        "Iran" : "IRN",
                        "Iraq" : "IRQ",
                        "Japan" : "JPN",
                        "KUWAIT" : "KWT",
                        "Kenya" : "KEN",
                        "LIBYA" : "LBY",
                        "Madagascar" : "MDG",
                        "Malaysia" : "MYS",
                        "Mauritius" : "MUS",
                        "Myanmar" : "MMR",
                        "Nepal" : "NEP",
                        "Netherland" : "NET",
                        "New Zealand" : "NZL",
                        "Nigeria" : "NGA",
                        "North Korea" : "NKR",
                        "Norway" : "NOR",
                        "OMAN" : "OMN",
                        "Pakistan" : "PAK",
                        "Qatar" : "QAT",
                        "Republic of Ireland" : "IRL",
                        "Russia" : "RUS",
                        "SWEDEN" : "SWE",
                        "Saudi Arabia" : "SAU",
                        "Singapore" : "SGP",
                        "South Africa" : "ZA",
                        "South Korea" : "SKR",
                        "Sri Lanka" : "SRI",
                        "Sudan" : "SUD",
                        "Switzerland" : "CHE",
                        "Tanzania" : "TZA",
                        "Thailand" : "THA",
                        "Uganda" : "UGA",
                        "Unite State of America" : "USA",
                        "United Arab Emirates" : "UAE",
                        "United Kingdom" : "GBR",
                        "ZAMBIA" : "ZMB",
    }
    
    return COUNTRY_CODE_MAP.get(code, "India")

def get_state_code(code):
    code = code.title()
    STATE_CODE_MAP = {
                      "Andaman and Nicobar Islands" : "AN",
                        "Andhra Pradesh" : "AP",
                        "Arunachal Pradesh" : "AR",
                        "Assam" : "AS",
                        "Bihar" : "BH",
                        "Chandigarh" : "CH",
                        "Chhattisgarh" : "CG",
                        "Dadra and Nagar Haveli" : "DN",
                        "Daman and Diu" : "DD",
                        "Goa" : "GO",
                        "Gujarat" : "GU",
                        "Haryana" : "HA",
                        "Himachal Pradesh" : "HP",
                        "Jammu and Kashmir" : "KR",
                        "Jharkhand" : "JD",
                        "Karnataka" : "KA",
                        "Kerala" : "KE",
                        "Lakshadweep" : "LD",
                        "Madhya Pradesh" : "MP",
                        "Maharashtra" : "MA",
                        "Manipur" : "MN",
                        "Meghalaya" : "ME",
                        "Mizoram" : "MI",
                        "Nagaland" : "NA",
                        "New Delhi" : "ND",
                        "ODISHA" : "OD",
                        "Others" : "OT",
                        "Puducherry" : "PO",
                        "Punjab" : "PU",
                        "Rajasthan" : "RA",
                        "Sikkim" : "SI",
                        "Tamil Nadu" : "TN",
                        "Telangana" : "TE",
                        "Tripura" : "TR",
                        "Uttar Pradesh" : "UP",
                        "Uttarakhand" : "UR",
                        "West Bengal" : "WB",
    }
    
    return STATE_CODE_MAP.get(code, "")


def getiinrequest(root, user_id, **kwargs):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)

    investor_dict = {
        constants.TAX_STATUS_XPATH: '01',  # TODO : user.tax_status return nothing
        constants.HOLD_NATURE_XPATH: 'SI',  # TODO
        constants.EXEMPT_FLAG_XPATH: 'N',
        constants.FH_PAN_XPATH: investor.pan_number,
        constants.JH1_PAN_XPATH: None,
        constants.JH1_EXEMPT_FLAG_XPATH: None,
        constants.JH2_PAN_XPATH: None,
        constants.JH2_EXEMPT_FLAG_XPATH: None,
        constants.GUARDIAN_PAN_XPATH: None
    }

    return getValidRequest(investor_dict, root)

def ceasesystematictrxn(root, user_id, **kwargs):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    exch_backend = kwargs.get('exchange_backend')
    user_vendor = models.UserVendor.objects.get(user=user, vendor__name=exch_backend.vendor_name)
    curr_date = datetime.now()

    investor_dict = {
        constants.REQUEST_IIN_XPATH: user_vendor.ucc,
        constants.TRXN_NO_XPATH: '155',  # TODO : Get this from systematic registration report
        constants.CEASE_REQ_DATE_XPATH: curr_date.strftime('%d-%b-%Y'),
        constants.INSTBY_XPATH: 'B', # 'B' for broker and 'I' for investor
        constants.NIGO_REMARKS_XPATH: 'test'
    }

    return getValidRequest(investor_dict, root)


def createcustomerrequest(root, user_id):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    investor = models.InvestorInfo.objects.get(user=user)
    nominee = models.NomineeInfo.objects.get(user=user)
    nominee_present = True if nominee and nominee.nominee_absent == False else False
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
        constants.TITLE_XPATH: None,
        constants.INV_NAME_XPATH: investor.applicant_name,
        constants.PAN_XPATH: investor.pan_number,
        constants.VALID_PAN_XPATH: 'Y',
        constants.EXEMPTION_XPATH: 'N',
        constants.EXEMPT_CATEGORY_XPATH: None,  # TODO
        constants.EXEMPT_REF_NO_XPATH: None,  # TODO
        constants.DOB_XPATH: changeDobFormat(investor.dob),
        constants.HOLD_NATURE_XPATH: api_constants.CLIENT_HOLDING_MAP["Single"], 
        constants.TAX_STATUS_XPATH: api_constants.CLIENT_TAX_STATUS_MAP["Individual"],
        constants.KYC_XPATH: investor.kra_verified,
        constants.OCCUPATION_XPATH: get_occupation_code(investor.occupation_type),
    # TODO : Refer master services for 2 letter occupation code
        constants.MFU_CAN_XPATH: None,  # TODO
        constants.DP_ID_XPATH: None,  # TODO
        constants.FATHER_NAME_XPATH: investor.father_name,
        constants.MOTHER_NAME_XPATH: None,  # TODO
        constants.TRXN_ACCEPTANCE_XPATH: "ALL",
        constants.ADDR1_XPATH: contact.communication_address.address_line_1,
        constants.ADDR2_XPATH: contact.communication_address.address_line_2,
        constants.ADDR3_XPATH: contact.communication_address.nearest_landmark,
        constants.CITY_XPATH: contact.communication_address.pincode.city,
        constants.STATE_XPATH: get_state_code(contact.communication_address.pincode.state),
        constants.PINCODE_XPATH: contact.communication_address.pincode.pincode,
        constants.COUNTRY_XPATH: get_country_code(api_constants.INDIA),
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
        constants.BANK_NAME_XPATH: bankcodes.bank_code_map.get(investor_bank.ifsc_code.name, None),
        constants.ACC_NO_XPATH: investor_bank.account_number,
        constants.ACC_TYPE_XPATH: 'SB', #TODO: investor_bank.account_type
        constants.IFSC_CODE_XPATH: investor_bank.ifsc_code.ifsc_code,
        constants.BRANCH_NAME_XPATH: investor_bank.ifsc_code.bank_branch,
        constants.BRANCH_ADDR1_XPATH: investor_bank.ifsc_code.address,
        constants.BRANCH_ADDR2_XPATH: None,
        constants.BRANCH_ADDR3_XPATH: None,
        constants.BRANCH_CITY_XPATH: investor_bank.ifsc_code.city,
        constants.BRANCH_PINCODE_XPATH: None,  # TODO
        constants.BRANCH_COUNTRY_XPATH: get_country_code(api_constants.INDIA),
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
        constants.NO_OF_NOMINEE_XPATH: '1' if nominee_present else '0',
        constants.NOMINEE1_TYPE_XPATH: 'Y' if nominee_present and nominee.guardian_name else 'N' if nominee_present else None,
        constants.NOMINEE1_NAME_XPATH: nominee.nominee_name if nominee_present else None,
        constants.NOMINEE1_DOB_XPATH: changeDobFormat(nominee.nominee_dob) if nominee_present else None,
        constants.NOMINEE1_ADDR1_XPATH: nominee.nominee_address.address_line_1 if nominee_present else None,
        constants.NOMINEE1_ADDR2_XPATH: nominee.nominee_address.address_line_2 if nominee_present else None,
        constants.NOMINEE1_ADDR3_XPATH: nominee.nominee_address.nearest_landmark if nominee_present else None,
        constants.NOMINEE1_CITY_XPATH: nominee.nominee_address.pincode.city if nominee_present else None,
        constants.NOMINEE1_STATE_XPATH: get_state_code(nominee.nominee_address.pincode.state) if nominee_present else None,
        constants.NOMINEE1_PINCODE_XPATH: nominee.nominee_address.pincode.pincode if nominee_present else None,
        constants.NOMINEE1_RELATION_XPATH: nominee.get_relationship_with_investor_display() if nominee_present else None,
        constants.NOMINEE1_PERCENT_XPATH: '100' if nominee_present else None,
        constants.NOMINEE1_GUARD_NAME_XPATH: nominee.guardian_name if nominee_present else None,
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

    return getValidRequest(investor_dict, root)

def purchasetxnrequest(root, child_root, user_id, **kwargs):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    exch_backend = kwargs.get('exchange_backend')
    user_vendor = models.UserVendor.objects.get(user=user, vendor__name=exch_backend.vendor_name)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    is_online_supported = investor_bank.ifsc_code.is_supported
    if is_online_supported:
        product_id_array = payment_constants.bank_product_id_map.get(investor_bank.ifsc_code.name, None)
        billdeskbank = product_id_array[0] 
    order_detail = kwargs.get("order")
    order_items = order_detail.fund_order_items.all()
    is_sip = kwargs.get("is_sip", False)
    if is_sip == True:
        bank_mandate = order_detail.bank_mandate
        if not bank_mandate:
            return None

    child_items = []
    total_amount = 0
    for item in order_items:
        item_fund = item.portfolio_item.fund
        neft_code = ''
        fund_vendor = core_models.FundVendorInfo.objects.get(fund=item_fund, vendor=user_vendor.vendor)
        if fund_vendor.neft_scheme_code:
            neft_code = fund_vendor.neft_scheme_code
        rtgs_code = ""
        if fund_vendor.rtgs_scheme_code:
            rtgs_code = fund_vendor.rtgs_scheme_code

        fund_house = None
        folio_number = None
        if item_fund.fund_house:
            fund_house = item_fund.fund_house
            try:
                folio_number = core_models.FolioNumber.objects.get(user=user, fund_house=fund_house).folio_number
            except core_models.FolioNumber.DoesNotExist:
                folio_number = None

        sip_tenure, tenure_len = user.get_sip_tenure(item.portfolio_item.portfolio)
        installment_no = 0 if sip_tenure is None else (sip_tenure * 12)
        agreed_sip = 0
        if is_sip == True:
            if item.agreed_sip:
                agreed_sip = item.agreed_sip
            start_date = models.get_valid_start_date(item_fund.id).strftime("%d-%b-%Y")
            end_date = start_date + datetime.relativedelta(months=+installment_no)
            trxn_amount = agreed_sip
        else:
            trxn_amount = item.order_amount
        
        total_amount += trxn_amount
        
        child_dict = {
            constants.AMC_XPATH: get_amc_code(fund_house.name.upper()) if fund_house is not None else None,
            constants.FOLIO_XPATH: folio_number,
            constants.PRODUCT_CODE_XPATH: neft_code if trxn_amount < 200000 else rtgs_code,
            constants.REINVEST_XPATH: 'N',
            constants.AMOUNT_XPATH: trxn_amount,
            constants.SIP_FROM_DATE_XPATH: None if is_sip == False else start_date.strftime("%d-%b-%Y"),
            constants.SIP_END_DATE_XPATH: None if is_sip == False else end_date.strftime("%d-%b-%Y"),
            constants.SIP_FREQ_XPATH: None if is_sip == False else 'OM',
            constants.SIP_AMOUNT_XPATH: None if is_sip == False else trxn_amount,
            constants.SIP_PERIOD_DAY_XPATH: None if is_sip == False else '{:02d}'.format(start_date.day)
        }
        
        child_items.append(child_dict)

    investor_dict = {
        constants.IIN_XPATH: user_vendor.ucc,
        constants.SUB_TRXN_TYPE_XPATH: 'N' if is_sip == False else 'S', # TODO: 'N' for normal and 'S' for systematic
        constants.POA_XPATH: 'N', # Executed by POA , values 'Y' or 'N'
        constants.TRXN_ACCEPTANCE_XPATH: 'ALL', # By Phone , online or both
        constants.DEMAT_USER_XPATH: 'N', #TODO: Is demat user or not
        constants.DP_ID_XPATH: None,
        constants.BANK_XPATH: bankcodes.bank_code_map.get(investor_bank.ifsc_code.name),
        constants.AC_NO_XPATH: investor_bank.account_number,
        constants.IFSC_CODE_XPATH: investor_bank.ifsc_code.ifsc_code,
        constants.SUB_BROKER_ARN_CODE_XPATH: None,
        constants.SUB_BROKER_CODE_XPATH: None,
        constants.EUIN_OPTED_XPATH: 'Y',# TODO
        constants.EUIN_XPATH: api_constants.Order_EUIN_Number,
        constants.TRXN_EXECUTION_XPATH: None,
        constants.REMARKS_XPATH: None,
        constants.PAYMENT_MODE_XPATH: 'OL' if is_online_supported else 'Q', #TODO :For Online
        constants.BILLDESK_BANK_XPATH: billdeskbank if is_online_supported else None,
        constants.INSTRM_BANK_XPATH: None,
        constants.INSTRM_AC_NO_XPATH: None,
        constants.INSTRM_NO_XPATH: None,
        constants.INSTRM_AMOUNT_XPATH: total_amount,
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
        constants.NOMINEE_FLAG_XPATH: 'C',
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
        constants.SIP_PAYMECH_XPATH: None if is_sip == False else 'M',
        constants.SIP_MICR_NO_XPATH: None,
        constants.SIP_BANK_XPATH: None if is_sip == False else bankcodes.bank_code_map.get(bank_mandate.mandate_bank_details.ifsc_code.name),
        constants.SIP_ACC_NO_XPATH: None if is_sip == False else bank_mandate.mandate_bank_details.account_number,
        constants.SIP_AC_TYPE_XPATH: None if is_sip == False else 'SB',
        constants.SIP_IFSC_CODE_XPATH: None if is_sip == False else bank_mandate.mandate_bank_details.ifsc_code.ifsc_code,
        constants.UMRN_XPATH: None,      #TODO: Provided by ACH Mandate Report , no need to give ach details here
        constants.ACH_AMT_XPATH: None if is_sip == False else bank_mandate.mandate_amount,
        constants.ACH_FROM_DATE_XPATH: None if is_sip == False else bank_mandate.mandate_start_date.strftime('%d-%b-%Y'),
        constants.ACH_END_DATE_XPATH: None if is_sip == False else '31-Dec-2999',
        constants.UNTIL_CANCELLED_XPATH: None if is_sip == False else 'Y',
        constants.RETURN_PAYMENT_FLAG_XPATH: 'Y',
        constants.CLIENT_CALLBACK_URL_XPATH: constants.PAYMENT_RU, #TODO
        constants.TRANS_COUNT_XPATH: len(child_items)
    }
    return getValidRequestWithMultipleChildren(investor_dict, child_items, root, child_root)

def redeemtxnrequest(root, child_root, user_id, **kwargs):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    exch_backend = kwargs.get('exchange_backend')
    user_vendor = models.UserVendor.objects.get(user=user, vendor__name=exch_backend.vendor_name)
    investor_bank = models.InvestorBankDetails.objects.get(user=user)
    grouped_redeem = kwargs.get("redeem")
    redeem_items = grouped_redeem.redeem_details.all()

    child_items = []
    total_amount = 0
    for item in redeem_items:
        total_amount += item.order_amount
        item_fund = item.portfolio_item.fund
        neft_code = ''
        fund_vendor = core_models.FundVendorInfo.objects.get(fund=item_fund, vendor=user_vendor.vendor)
        if fund_vendor.neft_scheme_code:
            neft_code = fund_vendor.neft_scheme_code
        rtgs_code = ""
        if fund_vendor.rtgs_scheme_code:
            rtgs_code = fund_vendor.rtgs_scheme_code

        fund_house = None
        folio_number = None
        if item_fund.fund_house:
            fund_house = item_fund.fund_house
            try:
                folio_number = core_models.FolioNumber.objects.get(user=user, fund_house=fund_house).folio_number
            except core_models.FolioNumber.DoesNotExist:
                folio_number = None

        redeem_value = str(item.redeem_amount)
        all_units = "N"
        if item.is_all_units_redeemed:
            all_units = "Y"

        child_dict = {
            constants.AMC_XPATH: get_amc_code(fund_house.name.upper()) if fund_house is not None else None,
            constants.FOLIO_XPATH: folio_number,
            constants.PRODUCT_CODE_XPATH: neft_code if item.order_amount < 200000 else rtgs_code,
            constants.AMOUNT_UNIT_TYPE_XPATH: item.order_amount,
            constants.AMOUNT_UNIT_XPATH: item.order_amount,
            constants.ALL_UNITS_XPATH: item.order_amount,
        }
        
        child_items.append(child_dict)

    investor_dict = {
        constants.IIN_XPATH: user_vendor.ucc,
        constants.POA_XPATH: 'N', # Executed by POA , values 'Y' or 'N'
        constants.TRXN_ACCEPTANCE_XPATH: 'ALL', # By Phone , online or both
        constants.DP_ID_XPATH: None,
        constants.BANK_NAME_XPATH: bankcodes.bank_code_map.get(investor_bank.ifsc_code.name),
        constants.AC_NO_XPATH: investor_bank.account_number,
        constants.IFSC_CODE_XPATH: investor_bank.ifsc_code.ifsc_code,
        constants.REMARKS_XPATH: None,
        constants.TRANS_COUNT_XPATH: len(child_items)
    }

    return getValidRequestWithMultipleChildren(investor_dict, child_items, root, child_root)

def achmandateregistrationsrequest(root, user_id, **kwargs):
    """

    :param user_id: id of user for whom the nse_request is to be generated
    :return:
    """
    user = models.User.objects.get(id=user_id)
    bank_mandate = kwargs.get('bank_mandate')
    exch_backend = kwargs.get('exchange_backend')
    user_vendor = models.UserVendor.objects.get(user=user, vendor__name=exch_backend.vendor_name)


    investor_dict = {
        constants.IIN_XPATH: user_vendor.ucc,
        constants.ACC_NO_XPATH: bank_mandate.mandate_bank_details.account_number,
        constants.ACC_TYPE_XPATH: 'SB', #TODO: investor_bank.account_type
        constants.IFSC_CODE_XPATH: bank_mandate.mandate_bank_details.ifsc_code.ifsc_code,
        constants.BANK_NAME_XPATH: bankcodes.bank_code_map.get(bank_mandate.mandate_bank_details.ifsc_code.name),
        constants.BRANCH_NAME_XPATH: bank_mandate.mandate_bank_details.ifsc_code.bank_branch,
        constants.MICR_NO_XPATH: bank_mandate.mandate_bank_details.ifsc_code.micr_code,
        constants.UC_XPATH: 'Y',
        constants.ACH_FROM_DATE_XPATH: bank_mandate.mandate_start_date.strftime('%d-%b-%Y'),
        constants.ACH_TO_DATE_XPATH: '31-Dec-2999',
        constants.ACH_AMOUNT_XPATH: bank_mandate.mandate_amount
    }

    return getValidRequest(investor_dict, root)

from . import constants as cons
from profiles import models as profile_models
from profiles.utils import is_investable
from profiles import constants as profile_constants
from core import models

from collections import OrderedDict
import os
import time


def generate_order_pipe_file(user, order_items):
    """
    This function generates a pipe separated file for bulk order entry.
    :param order_items: list of order_items for that order_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the bulk order entry
    """

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    bulk_order_pipe_file_name = "bulk_order_pipe" + timestamp + ".txt"
    outfile = open(output_path + bulk_order_pipe_file_name, "w")
    for i, item in enumerate(order_items):
        neft_code = ''
        if item.portfolio_item.fund.bse_neft_scheme_code:
            neft_code = item.portfolio_item.fund.bse_neft_scheme_code
        rgts_code = ""
        if item.portfolio_item.fund.bse_rgts_scheme_code:
            rgts_code = item.portfolio_item.fund.bse_rgts_scheme_code

        fund_house = ""
        folio_number = ""
        if item.portfolio_item.fund.fund_house:
            fund_house = item.portfolio_item.fund.fund_house
            try:
                f_number = models.FolioNumber.objects.get(user=user, fund_house=fund_house).folio_number
                if f_number:
                    folio_number = f_number
            except models.FolioNumber.DoesNotExist:
                folio_number = ""

        if int(order_items[i].agreed_lumpsum) > 0:
            bulk_order_dict = OrderedDict([('SCHEME CODE', neft_code if item.order_amount < 200000 else rgts_code),
                                           ('Purchase / Redeem', cons.Order_Purchase),
                                           ('Buy Sell Type', cons.Order_Buy_Type),
                                           ('Client Code', str(user.finaskus_id)),
                                           ('Demat / Physical', cons.Order_Demat),
                                           ('Order Val AMOUNT', str(order_items[i].agreed_lumpsum)),
                                           ('Folio No (10 digits)', str(folio_number)),
                                           ('Remarks', cons.Order_Remarks),
                                           ('KYC Flag Char', cons.Order_KYC_Flag),
                                           ('Sub Broker ARN Code', ''),
                                           ('EUIN Number', cons.Order_EUIN_Number),
                                           ('EUIN Declaration', cons.Order_EUIN_declaration),
                                           ('MIN redemption flag', cons.Order_MIN_redemption_Flag),
                                           ('DPC Flag', cons.Order_DPC_Flag),  # TODO:
                                           ('All Units', cons.Order_All_Units),  # TODO:
                                           ('Redemption Units', '')])  # TODO:
            outfile.write("|".join(bulk_order_dict.values()))
            if i < len(order_items) - 1:
                outfile.write("\r")
            bulk_order_dict.clear()
    outfile.close()
    return output_path + bulk_order_pipe_file_name


def generate_redeem_pipe_file(user, redeem_items):
    """
    This function generates a pipe separated file for redeem.
    :param redeem_items: list of redeem_items for that redeem_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the redeem
    """

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    redeem_pipe_file_name = "redeem_pipe" + timestamp + ".txt"
    outfile = open(output_path + redeem_pipe_file_name, "w")
    for i, item in enumerate(redeem_items):

        neft_code = ''
        if item.fund.bse_neft_scheme_code:
            neft_code = item.fund.bse_neft_scheme_code
        rgts_code = ""
        if item.fund.bse_rgts_scheme_code:
            rgts_code = item.fund.bse_rgts_scheme_code

        fund_house = ""
        folio_number = ""
        if item.fund.fund_house:
            fund_house = item.fund.fund_house
            try:
                f_number = models.FolioNumber.objects.get(user=user, fund_house=fund_house).folio_number
                if f_number:
                    folio_number = f_number
            except models.FolioNumber.DoesNotExist:
                folio_number = ""
        redeem_value = str(redeem_items[i].redeem_amount)
        all_units = cons.Redeem_All_Units
        if redeem_items[i].is_all_units_redeemed:
            redeem_value = ""
            all_units = "Y"
        bulk_redeem_dict = OrderedDict([('SCHEME CODE', neft_code if item.redeem_amount < 200000 else rgts_code),
                                       ('Purchase / Redeem', cons.Redeem_Purchase),
                                       ('Buy Sell Type', cons.Redeem_Buy_Type),
                                       ('Client Code', str(user.finaskus_id)),
                                       ('Demat / Physical', cons.Redeem_Demat),
                                       ('Redeem Val AMOUNT', redeem_value),
                                       ('Folio No (10 digits)', str(folio_number)),
                                       ('Remarks', cons.Redeem_Remarks),
                                       ('KYC Flag Char', cons.Redeem_KYC_Flag),
                                       ('Sub Broker ARN Code', ''),
                                       ('EUIN Number', cons.Redeem_EUIN_Number),
                                       ('EUIN Declaration', cons.Redeem_EUIN_declaration),
                                       ('MIN redemption flag', cons.Redeem_MIN_redemption_Flag),
                                       ('DPC Flag', cons.Redeem_DPC_Flag),  # TODO:
                                       ('All Units', all_units),
                                       ('Redemption Units', '')])  # TODO:
        outfile.write("|".join(bulk_redeem_dict.values()))
        if i < len(redeem_items)-1:
            outfile.write("\r")
        bulk_redeem_dict.clear()
    outfile.close()
    return output_path + redeem_pipe_file_name


def generate_client_pipe(user_list):
    """
    This function generates a pipe separated file for bulk order entry.
    
    :param user_list: list of users to be bulk uploaded.
    :return: url of the generated pipe separated file of the bulk order entry
    """

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps', '')
    output_path = base_dir + '/webapp/statics/'
    outfile = open(output_path+"bulk_client_pipe.txt", "w")
    
    def get_bse_occupation_code(code):
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
            profile_constants.BUSINESS: '01',
            profile_constants.PRIVATE_SECTOR: '02',
            profile_constants.PUBLIC_SECTOR: '02',
            profile_constants.GOVERNMENT: '02',
            profile_constants.PROFESSIONAL: '03',
            profile_constants.AGRICULTURE: '04',
            profile_constants.RETIRED: '05',
            profile_constants.HOUSEWIFE: '06',
            profile_constants.STUDENT: '07',
            profile_constants.OTHER: '08',
            profile_constants.FOREX_DEALER: '08',
        }

        return OCCUPATION_MAP.get(code, "08")
    
    def get_bse_account_type(code):
        """
        :param code: Our mapping for the account type
        :return: Account type code according to BSE standard
    
        Route our account type to
            SB - Saving Bank
            CB - Current Bank
            NE - NRE Account
            NO- NRO Account
        """
        ACCOUNT_MAP = {
            "S": "SB",
            "C": "CB",
            "NE": "NE",
            "NO": "NO"
        }
        return ACCOUNT_MAP.get(code, None)
    
    def get_bse_state_code(state_name):
        """
        :param state_name:
        :return: state code as expected by bse
        """
    
        STATE_MAP = {
        "ANDAMAN AND NICOBAR ISLAND": cons.CLIENT_STATE["Andaman & Nicobar"],
        "ANDHRA PRADESH": cons.CLIENT_STATE["Andhra Pradesh"],
        "ARUNACHAL PRADESH": cons.CLIENT_STATE["Arunachal Pradesh"],
        "ASSAM": cons.CLIENT_STATE["Assam"],
        "BIHAR": cons.CLIENT_STATE["Bihar"],
        "BILASPUR": cons.CLIENT_STATE["Chhattisgarh"],
        "CHANDIGARH": cons.CLIENT_STATE["Chandigarh"],
        "CHHATTISGARH": cons.CLIENT_STATE["Chhattisgarh"],
        "DADRA AND NAGAR HAVELI": cons.CLIENT_STATE["Dadra and Nagar Haveli"],
        "DAMAN AND DIU": cons.CLIENT_STATE["Daman and Diu"],
        "DELHI": cons.CLIENT_STATE["New Delhi"],
        "GOA": cons.CLIENT_STATE["GOA"],
        "GUJARAT": cons.CLIENT_STATE["Gujarat"],
        "HARYANA": cons.CLIENT_STATE["Haryana"],
        "HIMACHAL PRADESH": cons.CLIENT_STATE["Himachal Pradesh"],
        "JAMMU AND KASHMIR": cons.CLIENT_STATE["Jammu & Kashmir"],
        "JHARKHAND": cons.CLIENT_STATE["Jharkhand"],
        "KARANATAKA": cons.CLIENT_STATE["Karnataka"],
        "KARNATAKA": cons.CLIENT_STATE["Karnataka"],
        "KERALA": cons.CLIENT_STATE["Kerala"],
        "LAKSHADWEEP": cons.CLIENT_STATE["Others"],
        "MADHYA PRADESH": cons.CLIENT_STATE["Madhya Pradesh"],
        "MAHARASHTRA": cons.CLIENT_STATE["Maharashtra"],
        "MANIPUR": cons.CLIENT_STATE["Manipur"],
        "MEGHALAYA": cons.CLIENT_STATE["Meghalaya"],
        "MH": cons.CLIENT_STATE["Others"],
        "MIZORAM": cons.CLIENT_STATE["Mizoram"],
        "NAGALAND": cons.CLIENT_STATE["Nagaland"],
        "ODISHA": cons.CLIENT_STATE["Orissa"],
        "PUDUCHERRY": cons.CLIENT_STATE["Pondicherry"],
        "PUNJAB": cons.CLIENT_STATE["Punjab"],
        "RAJASTHAN": cons.CLIENT_STATE["Rajasthan"],
        "SIKKIM": cons.CLIENT_STATE["Sikkim"],
        "TAMIL NADU": cons.CLIENT_STATE["Tamil Nadu"],
        "TELANGANA": cons.CLIENT_STATE["Telangana"],
        "TRIPURA": cons.CLIENT_STATE["Tripura"],
        "UTTARAKHAND": cons.CLIENT_STATE["Uttaranchal"],
        "UTTAR PRADESH": cons.CLIENT_STATE["Uttar Pradesh"],
        "WEST BENGAL" : cons.CLIENT_STATE["West Bengal"]
        }

        return STATE_MAP.get(state_name, "OH")
    
    def create_user_dict(user_id):
        """
    
        :return:
        """
        user = profile_models.User.objects.get(id=user_id)
        investor = profile_models.InvestorInfo.objects.get(user=user)
        nominee = profile_models.NomineeInfo.objects.get(user=user)
        contact = profile_models.ContactInfo.objects.get(user=user)
        investor_bank = profile_models.InvestorBankDetails.objects.get(user=user)
    
        bse_dict = OrderedDict([("CLIENT CODE", user.finaskus_id),
                               ("CLIENT HOLDING", cons.CLIENT_HOLDING_MAP["Single"]),
                               ("CLIENT TAXSTATUS", cons.CLIENT_TAX_STATUS_MAP["Individual"]),
                               ("CLIENT OCCUPATIONCODE", get_bse_occupation_code(investor.occupation_type)),
                               ("CLIENT APPNAME1", investor.applicant_name),
                               ("CLIENT APPNAME2", None),
                               ("CLIENT APPNAME3", None),
                               ("CLIENT DOB", investor.dob.strftime("%d/%m/%Y")),
                               ("CLIENT GENDER", user.gender),
                               ("CLIENT FATHERHUSBAND", None),
                               ("CLIENT PAN", investor.pan_number),
                               ("CLIENT NOMINEE", nominee.nominee_name if nominee else None),
                               ("CLIENT NOMINEE RELATION", nominee.get_relationship_with_investor_display() if nominee else None),
                               ("CLIENT GUARDIANPAN", None),
                               ("CLIENT TYPE", cons.CLIENT_TYPE_P),
                               ("CLIENT DEFAULTDP", None),
                               ("CLIENT CDSLDPID", None),
                               ("CLIENT CDSLCLTID", None),
                               ("CLIENT NSDLDPID", None),
                               ("CLIENT NSDLCLTID", None),
                               ("CLIENT ACCTYPE1", get_bse_account_type(investor_bank.account_type)),
                               ("CLIENT ACCNO1", investor_bank.account_number),
                               ("CLIENT MICRNO1", None),
                               ("CLIENT NEFTCODE1", investor_bank.ifsc_code.ifsc_code),
                               ("DEFAULT BANK FLAG", cons.DEFAULT_BANK_Y),
                               ("CLIENT ACCTYPE2", None),
                               ("CLIENT ACCNO2", None),
                               ("CLIENT MICRNO2", None),
                               ("CLIENT NEFTCODE2", None),
                               ("DEFAULT BANK FLAG2", None),
                               ("CLIENT ACCTYPE3", None),
                               ("CLIENT ACCNO3", None),
                               ("CLIENT MICRNO3", None),
                               ("CLIENT NEFTCODE3", None),
                               ("DEFAULT BANK FLAG3", None),
                               ("CLIENT ACCTYPE4", None),
                               ("CLIENT ACCNO4", None),
                               ("CLIENT MICRNO4", None),
                               ("CLIENT NEFTCODE4", None),
                               ("DEFAULT BANK FLAG4", None),
                               ("CLIENT ACCTYPE5", None),
                               ("CLIENT ACCNO5", None),
                               ("CLIENT MICRNO5", None),
                               ("CLIENT NEFTCODE5", None),
                               ("DEFAULT BANK FLAG5", None),
                               ("CLIENT CHEQUENAME", None),
                               ("CLIENT ADD1", contact.communication_address.address_line_1),
                               ("CLIENT ADD2", contact.communication_address.address_line_2),
                               ("CLIENT ADD3", None),
                               ("CLIENT CITY", contact.communication_address.pincode.city),
                               ("CLIENT STATE", get_bse_state_code(contact.communication_address.pincode.state)),
                               ("CLIENT PINCODE", contact.communication_address.pincode.pincode),
                               ("CLIENT COUNTRY", user.nationality),
                               ("CLIENT RESIPHONE", contact.phone_number),
                               ("CLIENT RESIFAX", None),
                               ("CLIENT OFFICEPHONE", None),
                               ("CLIENT OFFICEFAX", None),
                               ("CLIENT EMAIL", contact.email),
                               ("CLIENT COMMMODE", cons.CLIENT_COMM_MODE["Electronic"]),
                               ("CLIENT DIVPAYMODE", cons.CLIENT_DIV_PAY_MODE.get("NEFT")),
                               ("CLIENT PAN2", None),
                               ("CLIENT PAN3", None),
                               ("MAPIN NO", None),
                               ("CM_FORADD1", None),
                               ("CM_FORADD2", None),
                               ("CM_FORADD3", None),
                               ("CM_FORCITY", None),
                               ("CM_FORPINCODE", None),
                               ("CM_FORSTATE", None),
                               ("CM_FORCOUNTRY", None),
                               ("CM_FORRESIPHONE", None),
                               ("CM_FORRESIFAX", None),
                               ("CM_FOROFFPHONE", None),
                               ("CM_FOROFFFAX", None),
                               ("CM_MOBILE", contact.phone_number)
                                ])

        for k, v in bse_dict.items():
            if v is None:
                bse_dict[k] = ''
            if type(v) != "<class 'str'>":
                bse_dict[k] = str(bse_dict[k])

        return bse_dict

    not_set = []
    for i in user_list:
        user = profile_models.User.objects.get(id=i)
        if not is_investable(user):
            not_set.append(user.id)
    if len(not_set) > 0:
        return not_set
    else:
        for i in range(len(user_list)):
            bulk_order_dict = create_user_dict(user_list[i])
            outfile.write("|".join(bulk_order_dict.values()))
            if i < len(user_list)-1:
                outfile.write("\r")
            bulk_order_dict.clear()
        outfile.close()

        return "/webapp/static/bulk_client_pipe.txt"

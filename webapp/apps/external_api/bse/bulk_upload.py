from external_api import constants as cons
from profiles import models as profile_models
from profiles.utils import is_investable
from profiles import constants as profile_constants
from core import models

from collections import OrderedDict
import os
import time


def generate_order_pipe_file(user_id, order_detail,exch_backend):
    """
    This function generates a pipe separated file for bulk order entry.
    :param order_items: list of order_items for that order_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the bulk order entry
    """
    user = profile_models.User.objects.get(id=user_id)
    order_items = order_detail.fund_order_items.all()
    order_id = order_detail.order_id
    user_vendor = profile_models.UserVendor.objects.get(user=user, vendor__name=exch_backend.vendor_name)
    
    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    bulk_order_pipe_file_name = order_id + "_lumpsum_" + user_vendor.ucc +".txt"
    print(bulk_order_pipe_file_name)
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
                                           ('Client Code', str(user_vendor.ucc)),
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
                                           ('Redemption Units', ''),
                                           ('SubBroker ARN', '')])  # TODO:
            outfile.write("|".join(bulk_order_dict.values()))
            if i < len(order_items) - 1:
                outfile.write("\r")
            bulk_order_dict.clear()
    outfile.close()
    return output_path + bulk_order_pipe_file_name


def generate_redeem_pipe_file(user_id, grouped_redeem):
    """
    This function generates a pipe separated file for redeem.
    :param redeem_items: list of redeem_items for that redeem_detail
    :param user: The user for which the file is being generated
    :return: url of the generated pipe separated file of the redeem
    """

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
    output_path = base_dir + '/webapp/static/'
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    redeem_pipe_file_name = "redeem_pipe" + timestamp + ".txt"
    outfile = open(output_path + redeem_pipe_file_name, "w")
    
    redeem_items = grouped_redeem.redeem_details.all()
    user = profile_models.User.objects.get(id=user_id)
    
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

def get_bse_occupation_type(code):
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

    OCCUPATION_TYPE_MAP = {
        profile_constants.BUSINESS: 'B',
        profile_constants.PRIVATE_SECTOR: 'S',
        profile_constants.PUBLIC_SECTOR: 'S',
        profile_constants.GOVERNMENT: 'S',
        profile_constants.PROFESSIONAL: 'B',
        profile_constants.AGRICULTURE: 'O',
        profile_constants.RETIRED: 'O',
        profile_constants.HOUSEWIFE: 'O',
        profile_constants.STUDENT: 'O',
        profile_constants.OTHER: 'O',
        profile_constants.FOREX_DEALER: 'O',
    }

    return OCCUPATION_TYPE_MAP.get(code, "O")

def get_bse_srcwealth_code(code):
    """
    :param code: Our mapping for the occupation
    :return: Occupation code according to BSE standards

    Routes our model mapping to BSE mapping as shown below
    """

    OCCUPATION_TO_SRCWEALTH_MAP = {
        profile_constants.BUSINESS: '02',
        profile_constants.PRIVATE_SECTOR: '01',
        profile_constants.PUBLIC_SECTOR: '01',
        profile_constants.GOVERNMENT: '01',
        profile_constants.PROFESSIONAL: '02',
        profile_constants.AGRICULTURE: '08',
        profile_constants.RETIRED: '08',
        profile_constants.HOUSEWIFE: '08',
        profile_constants.STUDENT: '08',
        profile_constants.OTHER: '08',
        profile_constants.FOREX_DEALER: '08',
    }

    return OCCUPATION_TO_SRCWEALTH_MAP.get(code, "08")

def get_bse_address_type_code(code):
    """
    :param code: Our mapping for the address type code
    :return: Address type code according to BSE standards

    Routes our model mapping to BSE mapping as shown below

    """

    ADDRESSTYPE_MAP = {
        profile_models.ContactInfo.AddressType.Residential_Business: '1',
        profile_models.ContactInfo.AddressType.Residential: '2',
        profile_models.ContactInfo.AddressType.Business: '3',
        profile_models.ContactInfo.AddressType.Registered_Office: '4',
    }

    return ADDRESSTYPE_MAP.get(code, "5")

def get_bse_income_code(code):
    """
    :param code: Our mapping for the income slab code
    :return: Income slab code according to BSE standards

    """

    INCOMESLAB_MAP = {
        profile_models.InvestorInfo.INCOME_CHOICE[0]: '31',
        profile_models.InvestorInfo.INCOME_CHOICE[1]: '32',
        profile_models.InvestorInfo.INCOME_CHOICE[2]: '33',
        profile_models.InvestorInfo.INCOME_CHOICE[3]: '34',
        profile_models.InvestorInfo.INCOME_CHOICE[4]: '35',
        profile_models.InvestorInfo.INCOME_CHOICE[5]: '36',
    }

    return INCOMESLAB_MAP.get(code, "33")

def get_bse_pep_code(code):
    """
    :param code: Our mapping for the income slab code
    :return: Income slab code according to BSE standards

    """

    PEP_MAP = {
        profile_models.InvestorInfo.EXPOSURE_CHOICE[0]: 'N',
        profile_models.InvestorInfo.EXPOSURE_CHOICE[1]: 'Y',
        profile_models.InvestorInfo.EXPOSURE_CHOICE[2]: 'R',
    }

    return PEP_MAP.get(code, "N")

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

def get_bse_country_code_fatca(country):
    """
    :param code: Our mapping for the country
    :return: Country code according to BSE standard

    """
    COUNTRY_MAP = {
        "Afghanistan": "AF",
        "Aland Islands": "AX",
        "Albania": "AL",
        "Algeria": "DZ",
        "American Samoa": "AS",
        "Andorra": "AD",
        "Angola": "AO",
        "Anguilla": "AI",
        "Antarctica": "AQ",
        "Antigua And Barbuda": "AG",
        "Argentina": "AR",
        "Armenia": "AM",
        "Aruba": "AW",
        "Australia": "AU",
        "Austria": "AT",
        "Azerbaijan": "AZ",
        "Bahamas": "BS",
        "Bahrain": "BH",
        "Bangladesh": "BD",
        "Barbados": "BB",
        "Belarus": "BY",
        "Belgium": "BE",
        "Belize": "BZ",
        "Benin": "BJ",
        "Bermuda": "BM",
        "Bhutan": "BT",
        "Bolivia": "BO",
        "Bosnia And Herzegovina": "BA",
        "Botswana": "BW",
        "Bouvet Island": "BV",
        "Brazil": "BR",
        "British Indian Ocean Territory": "IO",
        "Brunei Darussalam": "BN",
        "Bulgaria": "BG",
        "Burkina Faso": "BF",
        "Burundi": "BI",
        "Cambodia": "KH",
        "Cameroon": "CM",
        "Canada": "CA",
        "Cape Verde": "CV",
        "Cayman Islands": "KY",
        "Central African Republic": "042",
        "Chad": "CF",
        "Chile": "CL",
        "China": "CN",
        "Christmas Island": "CX",
        "Cocos (Keeling) Islands": "CC",
        "Colombia": "CO",
        "Comoros": "KM",
        "Congo": "CG",
        "Congo, The Democratic Republic Of The": "CD",
        "Cook Islands": "CK",
        "Costa Rica": "CR",
        "Cote DIvoire": "CI",
        "Croatia": "HR",
        "Cuba": "CU",
        "Cyprus": "CY",
        "Czech Republic": "CZ",
        "Denmark": "DK",
        "Djibouti": "DJ",
        "Dominica": "DM",
        "Dominican Republic": "DO",
        "Ecuador": "EC",
        "Egypt": "EG",
        "El Salvador": "SV",
        "Equatorial Guinea": "GQ",
        "Eritrea": "ER",
        "Estonia": "EE",
        "Ethiopia": "ET",
        "Falkland Islands (Malvinas)": "FK",
        "Faroe Islands": "FO",
        "Fiji": "FJ",
        "Finland": "FI",
        "France": "FR",
        "French Guiana": "GF",
        "French Polynesia": "PF",
        "French Southern Territories": "TF",
        "Gabon": "GA",
        "Gambia": "GM",
        "Georgia": "GE",
        "Germany": "DE",
        "Ghana": "GH",
        "Gibraltar": "GI",
        "Greece": "GR",
        "Greenland": "GL",
        "Grenada": "GD",
        "Guadeloupe": "GP",
        "Guam": "GU",
        "Guatemala": "GT",
        "Guernsey": "GG",
        "Guinea": "GN",
        "Guinea-Bissau": "GW",
        "Guyana": "GY",
        "Haiti": "HT",
        "Heard Island And Mcdonald Islands": "HM",
        "Holy See (Vatican City State)": "VA",
        "Honduras": "HN",
        "Hong Kong": "HK",
        "Hungary": "HU",
        "Iceland": "IS",
        "India": "IN",
        "Indonesia": "IN",
        "Iran, Islamic Republic Of": "IR",
        "Iraq": "IQ",
        "Ireland": "IE",
        "Isle Of Man": "IM",
        "Israel": "IL",
        "Italy": "IT",
        "Jamaica": "JM",
        "Japan": "JP",
        "Jersey": "JE",
        "Jordan": "JO",
        "Kazakhstan": "KZ",
        "Kenya": "KE",
        "Kiribati": "KI",
        "Korea, Democratic Peoples Republic Of": "KP",
        "Korea, Republic Of": "KR",
        "Kuwait": "KW",
        "Kyrgyzstan": "KG",
        "Lao Peoples Democratic Republic": "LA",
        "Latvia": "LV",
        "Lebanon": "LB",
        "Lesotho": "LS",
        "Liberia": "LR",
        "Libyan Arab Jamahiriya": "LY",
        "Liechtenstein": "LI",
        "Lithuania": "LT",
        "Luxembourg": "LU",
        "Macao": "MO",
        "Macedonia, The Former Yugoslav Republic Of": "MK",
        "Madagascar": "MG",
        "Malawi": "MW",
        "Malaysia": "MY",
        "Maldives": "MV",
        "Mali": "ML",
        "Malta": "MT",
        "Marshall Islands": "MH",
        "Martinique": "MQ",
        "Mauritania": "MR",
        "Mauritius": "MU",
        "Mayotte": "YT",
        "Mexico": "MX",
        "Micronesia, Federated States Of": "FM",
        "Moldova, Republic Of": "MD",
        "Monaco": "MC",
        "Mongolia": "MN",
        "Montserrat": "MS",
        "Morocco": "MA",
        "Mozambique": "MZ",
        "Myanmar": "MM",
        "Namibia": "NA",
        "Nauru": "NR",
        "Nepal": "NP",
        "Netherlands": "NL",
        "Netherlands Antilles": "AN",
        "New Caledonia": "NC",
        "New Zealand": "NZ",
        "Nicaragua": "NI",
        "Niger": "NE",
        "Nigeria": "NG",
        "Niue": "NU",
        "Norfolk Island": "NF",
        "Northern Mariana Islands": "MP",
        "Norway": "NO",
        "Oman": "OM",
        "Pakistan": "PK",
        "Palau": "PW",
        "Palestinian Territory, Occupied": "PS",
        "Panama": "PA",
        "Papua New Guinea": "PG",
        "Paraguay": "PY",
        "Peru": "PE",
        "Philippines": "PH",
        "Pitcairn": "PN",
        "Poland": "PL",
        "Portugal": "PT",
        "Puerto Rico": "PR",
        "Qatar": "QA",
        "Reunion": "RE",
        "Romania": "RO",
        "Russian Federation": "RU",
        "Rwanda": "RW",
        "Saint Helena": "SH",
        "Saint Kitts And Nevis": "KN",
        "Saint Lucia": "LC",
        "Saint Pierre And Miquelon": "PM",
        "Saint Vincent And The Grenadines": "VC",
        "Samoa": "WS",
        "San Marino": "SM",
        "Sao Tome And Principe": "ST",
        "Saudi Arabia": "SA",
        "Senegal": "SN",
        "Serbia And Montenegro": "RS",
        "Seychelles": "SC",
        "Sierra Leone": "SL",
        "Singapore": "SG",
        "Slovakia": "SK",
        "Slovenia": "SI",
        "Solomon Islands": "SB",
        "Somalia": "SO",
        "South Africa": "ZA",
        "South Georgia And The South Sandwich Islands": "GS",
        "Spain": "ES",
        "Sri Lanka": "LK",
        "Sudan": "SD",
        "Suriname": "SR",
        "Svalbard And Jan Mayen": "SJ",
        "Swaziland": "SZ",
        "Sweden": "SE",
        "Switzerland": "CH",
        "Syrian Arab Republic": "SY",
        "Taiwan, Province Of China": "TW",
        "Tajikistan": "TJ",
        "Tanzania, United Republic Of": "TZ",
        "Thailand": "TH",
        "Timor-Leste": "TL",
        "Togo": "TG",
        "Tokelau": "TK",
        "Tonga": "TO",
        "Trinidad And Tobago": "TT",
        "Tunisia": "TN",
        "Turkey": "TR",
        "Turkmenistan": "TM",
        "Turks And Caicos Islands": "TC",
        "Tuvalu": "TV",
        "Uganda": "UG",
        "Ukraine": "UA",
        "United Arab Emirates": "AE",
        "United Kingdom": "GB",
        "United States of America": "US",
        "United States Minor Outlying Islands": "UM",
        "Uruguay": "UY",
        "Uzbekistan": "UZ",
        "Vanuatu": "VU",
        "Venezuela": "VE",
        "Viet Nam": "VN",
        "Virgin Islands, British": "VG",
        "Virgin Islands, U.S.": "VI",
        "Wallis And Futuna": "WF",
        "Western Sahara": "EH",
        "Yemen": "YE",
        "Zambia": "ZM",
        "Zimbabwe": "ZW",
    }
    
    return COUNTRY_MAP.get(country, None)


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
    

def generate_client_pipe(user_list, bse_backend):
    """
    This function generates a pipe separated file for bulk order entry.
    
    :param user_list: list of users to be bulk uploaded.
    :return: url of the generated pipe separated file of the bulk order entry
    """

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
    output_path = base_dir + '/webapp/static/'
    outfile = open(output_path+"bulk_client_pipe.txt", "w")
    
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

        bse_backend.update_ucc(user_id, user.finaskus_id)
        return bse_dict

    for i in range(len(user_list)):
        bulk_order_dict = create_user_dict(user_list[i])
        outfile.write("|".join(bulk_order_dict.values()))
        if i < len(user_list)-1:
            outfile.write("\r")
        bulk_order_dict.clear()
    outfile.close()

    return "webapp/static/bulk_client_pipe.txt"

def generate_client_fatca_pipe(user_list):
    """
    This function generates a pipe separated file for bulk order entry.
    
    :param user_list: list of users to be bulk uploaded.
    :return: url of the generated pipe separated file of the bulk order entry
    """

    base_dir = os.path.dirname(os.path.dirname(__file__)).replace('/webapp/apps/external_api', '')
    output_path = base_dir + '/webapp/static/'
    outfile = open(output_path+"fatca_pipe.txt", "w")
    
    def get_pan_idenitfication_type():
        return "C"
    
    def create_user_dict(user_id):
        """
    
        :return:
        """
        user = profile_models.User.objects.get(id=user_id)
        investor = profile_models.InvestorInfo.objects.get(user=user)
        contact = profile_models.ContactInfo.objects.get(user=user)
    
        bse_dict = OrderedDict([("CLIENT PAN", investor.pan_number),
                               ("CLIENT PAN EXEMPT", None),
                               ("CLIENT APPNAME1", investor.applicant_name),
                               ("CLIENT DOB", investor.dob.strftime("%m/%d/%Y")),
                               ("CLIENT FATHERHUSBAND", None),
                               ("CLIENT SP NAME", None),
                               ("CLIENT TAXSTATUS", cons.CLIENT_TAX_STATUS_MAP["Individual"]),
                               ("CLIENT DATA SRC", cons.FATCA_DATA_SRC_E),
                               ("CLIENT ADDR TYPE", get_bse_address_type_code(contact.communication_address_type)),
                               ("CLIENT POB", investor.place_of_birth),
                               ("CLIENT COB", get_bse_country_code_fatca(investor.country_of_birth)),
                               ("CLIENT TAXRES", get_bse_country_code_fatca("India")),
                               ("CLIENT TAX PIN", investor.pan_number),
                               ("CLIENT TAX PIN TYPE", get_pan_idenitfication_type()),
                               ("CLIENT TAXRES2", None),
                               ("CLIENT TAX PIN2", None),
                               ("CLIENT TAX PIN TYPE2", None),
                               ("CLIENT TAXRES3", None),
                               ("CLIENT TAX PIN3", None),
                               ("CLIENT TAX PIN TYPE3", None),
                               ("CLIENT TAXRES4", None),
                               ("CLIENT TAX PIN4", None),
                               ("CLIENT TAX PIN TYPE4", None),
                               ("CLIENT SRC WEALTH", get_bse_srcwealth_code(investor.occupation_type)),
                               ("CLIENT CORP SERVS", None),
                               ("CLIENT INC SLAB", get_bse_income_code(investor.income)),
                               ("CLIENT NET WORTH", None),
                               ("CLIENT NET WORTH DATE", None),
                               ("CLIENT PEP", get_bse_pep_code(investor.political_exposure)),
                               ("CLIENT OCCUPATIONCODE", get_bse_occupation_code(investor.occupation_type)),
                               ("CLIENT OCCUPATIONType", get_bse_occupation_type(investor.occupation_type)),
                               ("CLIENT EXMPT CODE", None),
                               ("CLIENT FFI_DRNFE", None),
                               ("CLIENT GIIN_NO", None),
                               ("CLIENT SPR_ENTITY", None),
                               ("CLIENT GIIN_NA", None),
                               ("CLIENT GIIN_EXEMC", None),
                               ("CLIENT NFFE_CATG", None),
                               ("CLIENT ACT_NFE_SC", None),
                               ("CLIENT NATURE_BUS", None),
                               ("CLIENT REL_LISTED", None),
                               ("CLIENT EXCH_NAME", cons.EXCHNAME_BSE),
                               ("CLIENT UBO_APPL", "N"),
                               ("CLIENT UBO_COUNT", None),
                               ("CLIENT UBO_NAME", None),
                               ("CLIENT UBO_PAN", None),
                               ("CLIENT UBO_NATION", None),
                               ("CLIENT UBO_ADD1", None),
                               ("CLIENT UBO_ADD2", None),
                               ("CLIENT UBO_ADD3", None),
                               ("CLIENT UBO_CITY", None),
                               ("CLIENT UBO_PIN", None),
                               ("CLIENT UBO_STATE", None),
                               ("CLIENT UBO_CNTRY", None),
                               ("CLIENT UBO_ADD_TY", None),
                               ("CLIENT UBO_CTR", None),
                               ("CLIENT UBO_TIN", None),
                               ("CLIENT UBO_ID_TY", None),
                               ("CLIENT UBO_COB", None),
                               ("CLIENT UBO_DOB", None),
                               ("CLIENT UBO_GENDER", None),
                               ("CLIENT UBO_FR_NAM", None),
                               ("CLIENT UBO_OCC", None),
                               ("CLIENT UBO_OCC_TY", None),
                               ("CLIENT UBO_TEL", None),
                               ("CLIENT UBO_MOBILE", None),
                               ("CLIENT UBO_CODE", None),
                               ("CLIENT UBO_HOL_PC", None),
                               ("CLIENT SDF_FLAG", None),
                               ("CLIENT UBO_DF", "N"),
                               ("CLIENT AADHAAR_RP", None),
                               ("CLIENT NEW_CHANGE", "N"),
                               ("CLIENT LOG_NAME", user.finaskus_id + ":" + investor.modified_at.strftime("%d/%m/%Y")),
                               ("CLIENT FILLER1", None),
                               ("CLIENT FILLER2", None)
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
        else:
            investor = profile_models.InvestorInfo.objects.get(user=user)
            if investor and investor.other_tax_payer == True:
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

        return "webapp/static/fatca_pipe.txt"

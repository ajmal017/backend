from django.utils.translation import ugettext_lazy as _

from webapp.conf import local_settings as settings

OPERATOR_UNKNOWN = 0
OPERATOR_MGAGE = 1

OPERATOR_CHOICES = (
    (OPERATOR_UNKNOWN, _(u'Unknown')),
    (OPERATOR_MGAGE, _(u'MGage')),
)

MORNING_STAR_FUND_API = "http://api.morningstar.com/v2/service/mf/fknv977vtji58cx9/universeid/" + \
                        settings.MORNING_STAR_UNIVERSE_ID + "?accesscode=" + \
                        settings.MORNING_STAR_ACCESS_CODE + "&format=json"

MORNING_STAR_CHANGE_MONTHLY_API = "http://api.morningstar.com/v2/service/mf/xpmnckajt5a1ld2e/universeid/" + \
                                  settings.MORNING_STAR_UNIVERSE_ID + "?accesscode=" + \
                                  settings.MORNING_STAR_ACCESS_CODE + "&format=json"

MORNING_STAR_CHANGE_DAILY_API = "http://api.morningstar.com/v2/service/mf/m8tsm9qxk5se4co9/universeid/" + \
                                settings.MORNING_STAR_UNIVERSE_ID + "?accesscode=" + settings.MORNING_STAR_ACCESS_CODE + \
                                "&format=json"

MORNING_STAR_EQUITY_API = "http://api.morningstar.com/v2/service/mf/hxo7xm6b11k8nqz7/universeid/" + \
                          settings.MORNING_STAR_UNIVERSE_ID_EQUITY + "?accesscode=" + settings.MORNING_STAR_ACCESS_CODE +  \
                          "&format=json"

MORNING_STAR_SECTOR_API = "http://api.morningstar.com/v2/service/mf/GlobalStockSectorBreakdownRecentPort/universeid/" + \
                          settings.MORNING_STAR_UNIVERSE_ID_EQUITY + "?accesscode=" + settings.MORNING_STAR_ACCESS_CODE + \
                          "&format=json"

MORNING_STAR_DEBT_API = "http://api.morningstar.com/v2/service/mf/y9lk27a9omrxswh8/universeid/" + \
                        settings.MORNING_STAR_UNIVERSE_ID_DEBT + "?accesscode=" + settings.MORNING_STAR_ACCESS_CODE + \
                        "&format=json"

HISTORICAL_DATA_API = 'http://api.morningstar.com/service/mf/DailyReturnIndex/MStarID/'

INDICES_NAV_API = 'http://api.morningstar.com/v2/service/mf/c13k49f38raoyutj/universeid/'+ \
                     settings.MORNING_STAR_UNIVERSE_ID_INDICES + '?accesscode=' + settings.MORNING_STAR_ACCESS_CODE +\
                     "&format=json"

CATEGORY_NAV_API = 'http://api.morningstar.com/v2/service/mf/mk2ipzwesb5qricc/universeid/'+ \
                   settings.MORNING_STAR_UNIVERSE_ID + '?accesscode=' + settings.MORNING_STAR_ACCESS_CODE +\
                   '&format=json'

HISTORICAL_NAV_CATEGORY_API = 'http://api.morningstar.com/service/mf/CategoryTotalReturnIndex?accesscode='

EXCHANGE_RATE_API = 'http://www.morningstar.in/exchangerate/'


CATEGORY_ID = '&categoryId='
UNIVERSE = '&universe=FO'
ACCESS_CODE = '?accesscode='
START_DATE = '&startdate='
END_DATE = '&enddate='
REGION = '&region=IN&format=json'
FREQUENCY = '&frequency=D&format=json'


ISIN = 'isin'
MSTAR_ID = 'mstar_id'
FUND_ID = 'fund_id'
FUND_NAME = 'fund_name'
LEGAL_NAME = 'legal_name'
FUND_STANDARD_NAME = 'fund_standard_name'
BRANDING_NAME = 'branding_name'
BROAD_CATEGORY_GROUP = 'broad_category_group'
LEGAL_STRUCTURE = 'legal_structure'
CATEGORY_NAME = 'category_name'
INCEPTION_DATE = 'inception_date'
BENCHMARK = 'benchmark'
INDEX_NAME = 'IndexName'
MINIMUM_INVESTMENT = 'minimum_investment'
MINIMUM_SIP_INVESTMENT = 'minimum_sip_investment'
CATEGORY_CODE = 'category_code'

STAR_RATING = 'star_rating'
RISK = 'risk'
MAX_FRONT_LOAD = 'max_front_load'
DEFERRED_LOAD = 'LS-DeferLoads'
MAX_DEFERRED_LOAD = 'max_deferred_load'
EXPENSE_RATIO = 'expense_ratio'
MANAGERS = 'managers'
INVESTMENT_STRATEGY = 'investment_strategy'
HIGH_BREAK_POINT = 'HighBreakpoint'
BREAK_POINT_UNIT = 'BreakpointUnit'
VALUE = 'Value'
LOW_BREAK_POINT = 'LowBreakpoint'

CAPITAL_GAIN = 'capital_gain'
CAPITAL_GAIN_PERCENTAGE = 'capital_gain_percentage'
DAY_END_DATE = 'day_end_date'
DAY_END_NAV = 'day_end_nav'
CURRENCY = 'currency'
AUM = 'aum'
RETURN_ONE_YEAR = 'return_one_year'
RETURN_THREE_YEAR = 'return_three_year'
RETURN_FIVE_YEAR = 'return_five_year'
RETURN_ONE_MONTH = 'return_one_month'
RETURN_THREE_MONTH = 'return_three_month'
RETURN_ONE_DAY = 'return_one_day'
BETA = 'beta'

NUMBER_OF_HOLDINGS_TOTAL = 'number_of_holdings_total'
TOP_TEN_HOLDINGS = 'top_ten_holdings'
TOP_FIVE_HOLDINGS = 'top_five_holdings'
PORTFOLIO_TURNOVER = 'portfolio_turnover'
NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS = 'number_of_holdings_top_three_portfolios'

FIRST_NAME = 'first_name'
FIRST_WEIGHTAGE = 'first_weightage'
SECOND_NAME = 'second_name'
SECOND_WEIGHTAGE = 'second_weightage'
THIRD_NAME = 'third_name'
THIR_WEIGHTAGE = 'third_weightage'

AVERAGE_MATURITY = 'average_maturity'
MODIFIED_DURATION = 'modified_duration'
YIELD_TO_MATURITY = 'yield_to_maturity'
CREDIT_QUALITY_A = 'credit_quality_a'
CREDIT_QUALITY_AA = 'credit_quality_aa'
CREDIT_QUALITY_AAA = 'credit_quality_aaa'

AVERAGE_CREDIT_QUALITY = 'average_credit_quality'

FIELDS_FUND_API = [ISIN, MSTAR_ID, FUND_ID, LEGAL_NAME, FUND_STANDARD_NAME, BRANDING_NAME,
                   BROAD_CATEGORY_GROUP, LEGAL_STRUCTURE, CATEGORY_NAME, INCEPTION_DATE, BENCHMARK, MINIMUM_INVESTMENT,
                   MINIMUM_SIP_INVESTMENT, CATEGORY_CODE]

FIELDS_DATA_POINTS_MONTHLY_API = [STAR_RATING, MAX_FRONT_LOAD, MAX_DEFERRED_LOAD, EXPENSE_RATIO, MANAGERS,
                                  INVESTMENT_STRATEGY]

FIELDS_DATA_POINTS_DAILY_API = [CAPITAL_GAIN, CAPITAL_GAIN_PERCENTAGE, DAY_END_DATE, DAY_END_NAV, CURRENCY, AUM,
                                RETURN_ONE_YEAR, RETURN_THREE_YEAR, RETURN_FIVE_YEAR, RETURN_ONE_MONTH,
                                RETURN_THREE_MONTH, RETURN_ONE_DAY, BETA]

FIELDS_DATA_POINTS_EQUITY_API = [NUMBER_OF_HOLDINGS_TOTAL, TOP_TEN_HOLDINGS, PORTFOLIO_TURNOVER,
                                 NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS]

FIELDS_DATA_POINTS_SECTOR_API = ['EquitySectorBasicMaterialsLongRescaled', 'EquitySectorCommunicationServicesLongRescaled',
                                 'EquitySectorConsumerCyclicalLongRescaled', 'EquitySectorConsumerDefensiveLongRescaled',
                                 'EquitySectorHealthcareLongRescaled', 'EquitySectorIndustrialsLongRescaled',
                                 'EquitySectorRealEstateLongRescaled', 'EquitySectorTechnologyLongRescaled',
                                 'EquitySectorEnergyLongRescaled', 'EquitySectorFinancialServicesLongRescaled',
                                 'EquitySectorUtilitiesLongRescaled']

FIELDS_DATA_POINTS_DEBT_API = [NUMBER_OF_HOLDINGS_TOTAL, TOP_TEN_HOLDINGS, AVERAGE_MATURITY, MODIFIED_DURATION,
                               YIELD_TO_MATURITY, NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS, CREDIT_QUALITY_A,
                               CREDIT_QUALITY_AA, CREDIT_QUALITY_AAA, AVERAGE_CREDIT_QUALITY]

FUND_MAP = {
    ISIN : 'FSCBI-ISIN',
    MSTAR_ID: 'FSCBI-MStarID',
    FUND_ID: 'FSCBI-FundId',
    LEGAL_NAME: 'FSCBI-LegalName',
    FUND_STANDARD_NAME: 'FSCBI-FundStandardName',
    BRANDING_NAME: 'FSCBI-BrandingName',
    BROAD_CATEGORY_GROUP:'FSCBI-BroadCategoryGroup',
    LEGAL_STRUCTURE: 'FSCBI-LegalStructure',
    CATEGORY_NAME: 'FSCBI-CategoryName',
    INCEPTION_DATE: 'FSCBI-InceptionDate',
    BENCHMARK: 'FB-PrimaryProspectusBenchmarks',
    MINIMUM_INVESTMENT: 'PI-MinimumInitial',
    MINIMUM_SIP_INVESTMENT: 'PI-MinimumAIP',
    CATEGORY_CODE: 'FSCBI-CategoryCode'
}

MONTHLY_CHANGE_POINTS_MAP = {
    STAR_RATING: 'MR-RatingOverall',
    MAX_FRONT_LOAD: 'LS-MaximumFrontLoad',
    EXPENSE_RATIO: 'ARF-NetExpenseRatio',
    MANAGERS: 'FM-Managers',
    INVESTMENT_STRATEGY: 'IC-InvestmentStrategy',
}

DAILY_CHANGE_POINTS_MAP = {
    CAPITAL_GAIN: 'DP-NAVChange',
    CAPITAL_GAIN_PERCENTAGE: 'DP-NAVChangePercentage',
    DAY_END_DATE: 'DP-DayEndDate',
    DAY_END_NAV: 'DP-DayEndNAV',
    CURRENCY: 'DP-Currency',
    AUM:'FNA-SurveyedFundNetAssets',
    RETURN_ONE_YEAR: 'DP-Return1Yr',
    RETURN_THREE_YEAR: 'DP-Return3Yr',
    RETURN_FIVE_YEAR: 'DP-Return5Yr',
    RETURN_ONE_MONTH: 'DP-Return1Mth',
    RETURN_THREE_MONTH: 'DP-Return3Mth',
    RETURN_ONE_DAY: 'DP-Return1Day',
    BETA: 'MPTPI-Beta3Yr'
}

EQUITY_DATA_POINTS_MAP = {
    NUMBER_OF_HOLDINGS_TOTAL: 'PSRP-NumberofHolding',
    TOP_TEN_HOLDINGS: 'PSRP-AssetinTop10Holdings',
    PORTFOLIO_TURNOVER: 'PS-TurnoverRatio',
    NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS: 'T10HV2-HoldingDetail',
}

DEBT_DATA_POINTS_MAP = {
    NUMBER_OF_HOLDINGS_TOTAL: 'PSRP-NumberofHolding',
    TOP_TEN_HOLDINGS: 'PSRP-AssetinTop10Holdings',
    AVERAGE_MATURITY: 'PSRP-AverageEffMaturity',
    MODIFIED_DURATION: 'PSRP-ModifiedDurationLong',
    YIELD_TO_MATURITY: 'PS-YieldToMaturity',
    NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS: 'T10HV2-HoldingDetail',
    CREDIT_QUALITY_A: 'CQBRP-CreditQualA',
    CREDIT_QUALITY_AA: 'CQBRP-CreditQualAA',
    CREDIT_QUALITY_AAA: 'CQBRP-CreditQualAAA',
    AVERAGE_CREDIT_QUALITY: 'PSRP-AverageCreditQualityName'
}

MGAGE_MESSAGE_CONCAT_TRUE = 1

NO_DOORSTEP_VERIFICATION = "Doorstep verification is not possible at this pincode"
YES_DOORSTEP_VERIFICATION = "Doorstep verification is possible at this pincode"

CSV_FILE_NAME = 'pin.csv'
CSV_BANK_FILE_PATH = 'bank_details1.csv'
PIN_CODE = 'pincode'
STATE = 'state'
CITY = 'city'
MESSAGE = "message"
DATA = 'data'
STATUS = 'status'
CODE = 'code'
HOLDINGS = "holdings"
SUCCESS = "success"
FAIL = 'fail'
CONNECTION_ERROR = 'Connection Error'
HTTP_ERROR = 'HTTP Error'
NO_DATA_RECEIVED = 'No data received'
ID = '_id'
API = 'api'
RAW_DATA = 'r'
DATE = 'date'
NAV = 'nav'
HISTORICAL_DATA_MAP = {
    DATE: 'd',
    NAV: 'v'
}
FUND_DOES_NOT_EXIST = 'fund with the mstar id does not exist'

USER_NOT_FOUND = 'User does not exist'

PURCHASE_TXN_FAILED = 'Purchase transaction failed'

VAULT_NOT_CLOSED = 'Vault not closed'

HISTORICAL_DATA_TIME_INTERVAL = 30

INDICES_MAP = {
    'FOUSA09JXZ': 1,
    'FOUSA05MHG': 2,
    'FOUSA05LXA': 3,
    'F00000T9C0': 4,
    'FOUSA0907S': 5,
}

START_DATE_FOR_INDEX = None
IFSC = 'IFSC'
IFSC_CODE = 'ifsc_code'
BANK_NAME = 'name'
BRANCH = 'bank_branch'
ADDRESS = 'address'
CONTACT = 'phone_number'
DISTRICT = 'district'

INDICES_DAY_END_DATE = 'date'
INDICES_DAY_END_PRICE = 'nav'

INDICES_NAV_LIST_MAP = {
    INDICES_DAY_END_DATE: 'DMP-DayEndDate',
    INDICES_DAY_END_PRICE: 'DMP-DayEndPrice'
}
IFSC_CODE_INCORRECT = 'The IFSC code is incorrect.'

CATEGORY_DAY_END_DATE = 'DP-CategoryEndDate'
CATEGORY_DAY_END_PRICE = 'DP-CategoryReturn1Day'
CATEGORY_CODE_DAILY = 'DP-CategoryCode'
MODIFIED_AT = 'modified_at'
TRANSACTION = 'Transaction'
CLOSE_PRICE = 'ClosePrice'
MODE_OF_HOLDING = 'SI'  # mode of holding is Single (SI)

CLIENT_HOLDING_MAP = {
    "Single": "SI",
    "Joint": "JO",
    "Anyone or Survivor": "AS",
}

CLIENT_TAX_STATUS_MAP = {
    "Individual": "01",
    "On behalf of minor": "02",
    "HUF": "03",
    "Company": "04",
    "NRE": "21",
    "NRO": "24",
    "FII": "23",
    "DFI": "12",
    "TRUST": "08",
    "AOP": "05",
    "LLP": "47",
    "Others": "10",
    "Partnership Firm": "06"
}
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
CLIENT_GENDER = {
    "Male": "M",
    "Female": "F"
}
CLIENT_ACCOUNT_TYPE = {
    "Saving Bank": "SB",
    "Current Bank": "CB",
    "NRE Account": "NE",
    "NRO Account": "NO"
}
CLIENT_STATE = {
    "Andaman & Nicobar": "AN",
    "Arunachal Pradesh": "AR",
    "Andhra Pradesh": "AP",
    "Assam": "AS",
    "Bihar": "BH",
    "Chandigarh": "CH",
    "Chhattisgarh": "CG",
    "Delhi": "DL",
    "GOA": "GO",
    "Gujarat": "GU",
    "Haryana": "HA",
    "Himachal Pradesh": "HP",
    "Jammu & Kashmir": "JM",
    "Jharkhand": "JK",
    "Karnataka": "KA",
    "Kerala": "KE",
    "Madhya Pradesh": "MP",
    "Maharashtra": "MA",
    "Manipur": "MN",
    "Meghalaya": "ME",
    "Mizoram": "MI",
    "Nagaland": "NA",
    "New Delhi": "ND",
    "Orissa": "OR",
    "Pondicherry": "PO",
    "Punjab": "PU",
    "Rajasthan": "RA",
    "Sikkim": "SI",
    "Telangana": "TG",
    "Tamil Nadu": "TN",
    "Tripura": "TR",
    "Uttar Pradesh": "UP",
    "Uttaranchal": "UC",
    "West Bengal": "WB",
    "Dadra and Nagar Haveli": "DN",
    "Daman and Diu": "DD",
    "Others": "OH"
}
CLIENT_COMM_MODE = {
    "Physical": "P",
    "Electronic": "E"
}
CLIENT_DIV_PAY_MODE = {
    "Cheque": "01",
    "Direct Credit": "02",
    "ECS": "03",
    "NEFT": "04",
    "RTGS": "05"
}
CM_FOR_COUNTRY = {
    "Afghanistan": "001",
    "Aland Islands": "002",
    "Albania": "003",
    "Algeria": "004",
    "American Samoa": "005",
    "Andorra": "006",
    "Angola": "007",
    "Anguilla": "008",
    "Antarctica": "009",
    "Antigua And Barbuda": "010",
    "Argentina": "011",
    "Armenia": "012",
    "Aruba": "013",
    "Australia": "014",
    "Austria": "015",
    "Azerbaijan": "016",
    "Bahamas": "017",
    "Bahrain": "018",
    "Bangladesh": "019",
    "Barbados": "020",
    "Belarus": "021",
    "Belgium": "022",
    "Belize": "023",
    "Benin": "024",
    "Bermuda": "025",
    "Bhutan": "026",
    "Bolivia": "027",
    "Bosnia And Herzegovina": "028",
    "Botswana": "029",
    "Bouvet Island": "030",
    "Brazil": "031",
    "British Indian Ocean Territory": "032",
    "Brunei Darussalam": "033",
    "Bulgaria": "034",
    "Burkina Faso": "035",
    "Burundi": "036",
    "Cambodia": "037",
    "Cameroon": "038",
    "Canada": "039",
    "Cape Verde": "040",
    "Cayman Islands": "041",
    "Central African Republic": "042",
    "Chad": "043",
    "Chile": "044",
    "China": "045",
    "Christmas Island": "046",
    "Cocos (Keeling) Islands": "047",
    "Colombia": "048",
    "Comoros": "049",
    "Congo": "050",
    "Congo, The Democratic Republic Of The": "051",
    "Cook Islands": "052",
    "Costa Rica": "053",
    "Cote DIvoire": "054",
    "Croatia": "055",
    "Cuba": "056",
    "Cyprus": "057",
    "Czech Republic": "058",
    "Denmark": "059",
    "Djibouti": "060",
    "Dominica": "061",
    "Dominican Republic": "062",
    "Ecuador": "063",
    "Egypt": "064",
    "El Salvador": "065",
    "Equatorial Guinea": "066",
    "Eritrea": "067",
    "Estonia": "068",
    "Ethiopia": "069",
    "Falkland Islands (Malvinas)": "070",
    "Faroe Islands": "071",
    "Fiji": "072",
    "Finland": "073",
    "France": "074",
    "French Guiana": "075",
    "French Polynesia": "076",
    "French Southern Territories": "077",
    "Gabon": "078",
    "Gambia": "079",
    "Georgia": "080",
    "Germany": "081",
    "Ghana": "082",
    "Gibraltar": "083",
    "Greece": "084",
    "Greenland": "085",
    "Grenada": "086",
    "Guadeloupe": "087",
    "Guam": "088",
    "Guatemala": "089",
    "Guernsey": "090",
    "Guinea": "091",
    "Guinea-Bissau": "092",
    "Guyana": "093",
    "Haiti": "094",
    "Heard Island And Mcdonald Islands": "095",
    "Holy See (Vatican City State)": "096",
    "Honduras": "097",
    "Hong Kong": "098",
    "Hungary": "099",
    "Iceland": "100",
    "India": "101",
    "Indonesia": "102",
    "Iran, Islamic Republic Of": "103",
    "Iraq": "104",
    "Ireland": "105",
    "Isle Of Man": "106",
    "Israel": "107",
    "Italy": "108",
    "Jamaica": "109",
    "Japan": "110",
    "Jersey": "111",
    "Jordan": "112",
    "Kazakhstan": "113",
    "Kenya": "114",
    "Kiribati": "115",
    "Korea, Democratic Peoples Republic Of": "116",
    "Korea, Republic Of": "117",
    "Kuwait": "118",
    "Kyrgyzstan": "119",
    "Lao Peoples Democratic Republic": "120",
    "Latvia": "121",
    "Lebanon": "122",
    "Lesotho": "123",
    "Liberia": "124",
    "Libyan Arab Jamahiriya": "125",
    "Liechtenstein": "126",
    "Lithuania": "127",
    "Luxembourg": "128",
    "Macao": "129",
    "Macedonia, The Former Yugoslav Republic Of": "130",
    "Madagascar": "131",
    "Malawi": "132",
    "Malaysia": "133",
    "Maldives": "134",
    "Mali": "135",
    "Malta": "136",
    "Marshall Islands": "137",
    "Martinique": "138",
    "Mauritania": "139",
    "Mauritius": "140",
    "Mayotte": "141",
    "Mexico": "142",
    "Micronesia, Federated States Of": "143",
    "Moldova, Republic Of": "144",
    "Monaco": "145",
    "Mongolia": "146",
    "Montserrat": "147",
    "Morocco": "148",
    "Mozambique": "149",
    "Myanmar": "150",
    "Namibia": "151",
    "Nauru": "152",
    "Nepal": "153",
    "Netherlands": "154",
    "Netherlands Antilles": "155",
    "New Caledonia": "156",
    "New Zealand": "157",
    "Nicaragua": "158",
    "Niger": "159",
    "Nigeria": "160",
    "Niue": "161",
    "Norfolk Island": "162",
    "Northern Mariana Islands": "163",
    "Norway": "164",
    "Oman": "165",
    "Pakistan": "166",
    "Palau": "167",
    "Palestinian Territory, Occupied": "168",
    "Panama": "169",
    "Papua New Guinea": "170",
    "Paraguay": "171",
    "Peru": "172",
    "Philippines": "173",
    "Pitcairn": "174",
    "Poland": "175",
    "Portugal": "176",
    "Puerto Rico": "177",
    "Qatar": "178",
    "Reunion": "179",
    "Romania": "180",
    "Russian Federation": "181",
    "Rwanda": "182",
    "Saint Helena": "183",
    "Saint Kitts And Nevis": "184",
    "Saint Lucia": "185",
    "Saint Pierre And Miquelon": "186",
    "Saint Vincent And The Grenadines": "187",
    "Samoa": "188",
    "San Marino": "189",
    "Sao Tome And Principe": "190",
    "Saudi Arabia": "191",
    "Senegal": "192",
    "Serbia And Montenegro": "193",
    "Seychelles": "194",
    "Sierra Leone": "195",
    "Singapore": "196",
    "Slovakia": "197",
    "Slovenia": "198",
    "Solomon Islands": "199",
    "Somalia": "200",
    "South Africa": "201",
    "South Georgia And The South Sandwich Islands": "202",
    "Spain": "203",
    "Sri Lanka": "204",
    "Sudan": "205",
    "Suriname": "206",
    "Svalbard And Jan Mayen": "207",
    "Swaziland": "208",
    "Sweden": "209",
    "Switzerland": "210",
    "Syrian Arab Republic": "211",
    "Taiwan, Province Of China": "212",
    "Tajikistan": "213",
    "Tanzania, United Republic Of": "214",
    "Thailand": "215",
    "Timor-Leste": "216",
    "Togo": "217",
    "Tokelau": "218",
    "Tonga": "219",
    "Trinidad And Tobago": "220",
    "Tunisia": "221",
    "Turkey": "222",
    "Turkmenistan": "223",
    "Turks And Caicos Islands": "224",
    "Tuvalu": "225",
    "Uganda": "226",
    "Ukraine": "227",
    "United Arab Emirates": "228",
    "United Kingdom": "229",
    "United States of America": "230",
    "United States Minor Outlying Islands": "231",
    "Uruguay": "232",
    "Uzbekistan": "233",
    "Vanuatu": "234",
    "Venezuela": "235",
    "Viet Nam": "236",
    "Virgin Islands, British": "237",
    "Virgin Islands, U.S.": "238",
    "Wallis And Futuna": "239",
    "Western Sahara": "240",
    "Yemen": "241",
    "Zambia": "242",
    "Zimbabwe": "24",
}

UNACCEPTABLE_PAN_NUMBER = "This PAN is already registered with another account."
INDIA = 'India'
STATIC = '/static/'

Accept_Mode = "P"

Xsip_status = "1"

Brokerage_money = "0"

First_Order_Today = "Y"

Frequency_Type = "MONTHLY"
Frequency_Allowed = "1"
DP_TXN_MODE = "P"

Order_Purchase = "P"
Order_Buy_Type = "FRESH"
Order_Demat = "P"
Order_Remarks = ""
Order_KYC_Flag = "Y"
Order_EUIN_Number = "E148376"
Order_EUIN_declaration = "Y"
Order_MIN_redemption_Flag = "N"
Order_DPC_Flag = "N"
Order_All_Units = ""

Redeem_Purchase = "R"
Redeem_Buy_Type = "FRESH"
Redeem_Demat = "P"
Redeem_Remarks = ""
Redeem_KYC_Flag = "Y"
Redeem_EUIN_Number = "E148376"
Redeem_EUIN_declaration = "Y"
Redeem_MIN_redemption_Flag = "N"
Redeem_DPC_Flag = "N"
Redeem_All_Units = "N"

ARN_CODE = "108537"
MEMBER_CODE = "10382"
DEMO_MEMBER_CODE = "10236"
PHYS = "PHYS"
CLIENT_TYPE_P = "P"
DEFAULT_BANK_Y = "Y"
DEFAULT_BANK_N = "N"
FATCA_DATA_SRC_E = "E"

UNSUPPORTED_BANK = "Payment is not supported through this bank as of now."

#  various international standard values are defined for image resizing.
# note it is width X height always, in real life too not just python.
LANDSCAPE_SIZE = (1024, 512)  # international landscape is 1,024 x 512 these are minimum dimensions.
PORTRAIT_SIZE = (800, 1200)  # international portrait is 800 x 1,200 these are minimum dimensions.
PASSPORT_SIZE = (600, 600)  # international standard 600 pixels X 600 pixels
SIGNATURE_SIZE = (1000, 300)  # international standard 1000 pixels X 300 pixels
TIFF_SIGNATURE_SIZE = (900, 220)  # international standard 1000 pixels X 300 pixels
TIFF_LANDSCAPE_SIZE = (840, 500)
TIFF_PORTRAIT_SIZE = (500, 840)
WALLPAPER_SIZE = (1920, 1080)  # standard wallpaper publishing 1920 X 1080 pixels
SEMI_WALLPAPER_SIZE = (900, 900)  # standard semi_wallpaper publishing 1920 X 1080 pixels
ORIGINAL_SIZE = 1  # maintain original size.
FIT_SIZE = 2  # page fit size.
WIDTH = 3.5
HEIGHT = 4.5
TIFF_HEIGHT = 4
WALLPAPER_WIDTH = 20
WALLPAPER_HEIGHT = 20
SEMI_WALLPAPER_WIDTH = 15
SEMI_WALLPAPER_HEIGHT = 12
ORIGINAL_WIDTH = 2.54/96  # std pixels to cm conversion unit
ORIGINAL_HEIGHT = 2.54/96  # std pixels to cm conversion unit
DEFAULT_NOMINEE_SIGNATURE = "webapp/static/images/dummy_nominee_signature.png"

FORBIDDEN_ERROR = "access is forbidden."  # to prevent unauthorized access of private files.

DEFAULT_IMAGE = "webapp/static/images/dummy_image.jpg"


TO_URL = 'http://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc/Basic'
GET_PASSWORD_URL = 'http://tempuri.org/IMFUploadService/getPassword'

BSE_ORDER_WSDL = 'http://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc?singleWsdl'
BSE_ORDER_GET_PASSWORD_URL = 'http://bsestarmf.in/MFOrderEntry/getPassword'
EXCHNAME_BSE = "B"

RETURN_CODE_FAILURE = '1'

RETURN_CODE_SUCCESS = '0'

USER_NOT_REGISTERED = "USER_NOT_REGISTERED"
ORDERS_DONT_EXIST = "ORDERS_DONT_EXIST"
FAILED_TO_PUNCH_TRANSACTION = "FAILED_TO_PUNCH_TRANSACTION"
 

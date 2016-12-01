QUESTION_NOT_FOUND = 'Questions not found.'
ANSWER_SAVING_ERROR = 'Error occurred while saving the answer.'
RISK_PROFILES_ERROR = 'Could not fetch risk profiles.'
FUND_NOT_IN_PORTFOLIO = "This fund does not exists in the portfolio and thus cannot be swapped."
FUND_ALREADY_IN_PORTFOLIO = "This fund already exists in the portfolio and thus cannot be swapped."
NO_SUCH_FUND = "This fund does not exists."
MINIMUM_SIP_ERROR = "You cannot swap funds as the minimum sip of this fund is less than the sip you wish to invest. " \
                    "Please increase your sip or choose another fund to swap"
MINIMUM_LUMPSUM_ERROR = "You cannot swap funds as the minimum lumpsum of this fund is less than the lumpsum you wish to " \
                        "invest. Please increase your lumpsum or choose another fund to swap"

CHECKBOX = "C"
RADIO = "R"
TEXT = "T"
BLANKS = "B"
MULTIPLE_TEXT = "M"

TYPE_CHOICES = {
    CHECKBOX: 'Checkbox',
    RADIO: 'Radio',
    TEXT: 'Text',
    BLANKS: 'B',
    MULTIPLE_TEXT: 'MultipleText'
}

ASSESS = 'A'
PLAN = 'P'
RETIREMENT = 'R'
TAX_SAVING = 'T'
BUY_PROPERTY = 'BP'
EDUCATION = 'E'
WEDDING = 'W'
OTHER_EVENT = 'O'
INVEST = 'I'
LIQUID_GOAL = 'L'
AUTO_MOBILE = 'AM'
VACATION = 'V'
JEWELLERY = 'J'

EDUCATION_TYPE = "education"
PROPERTY_TYPE = "property"
AUTO_MOBILE_TYPE = "automobile"
VACATION_TYPE = "vacation"
WEDDING_TYPE = "wedding"

MAP = {
    "invest": INVEST,
    "assess": ASSESS,
    "tax": TAX_SAVING,
    "plan": PLAN,
    "retirement": RETIREMENT,
    "property": BUY_PROPERTY,
    "education": EDUCATION,
    "wedding": WEDDING,
    "event": OTHER_EVENT,
    "liquid":LIQUID_GOAL,
    "automobile":AUTO_MOBILE,
    "vacation":VACATION,
    "jewellery":JEWELLERY
}


ASSET_ALLOCATION_MAP = {
    RETIREMENT: [None, 'monthly_investment', 'RET', ['current_age', 'retirement_age'], 'grow_sip'],
    TAX_SAVING: ['amount_invested', None, 'TAX', None, None],
    BUY_PROPERTY: ['lumpsum', 'sip', 'PRO', ['term'], None],
    EDUCATION: ['lumpsum', 'sip', 'EDU', ['term'], None],
    WEDDING: ['lumpsum', 'sip', 'WED', ['term'], None],
    OTHER_EVENT: ['lumpsum', 'sip', 'EVT', ['term'], None],
    INVEST: ['lumpsum', 'sip', 'INV', ['term'], 'grow_sip'],
    LIQUID_GOAL: ['amount_invested', None, 'LIQ', None, None],
    AUTO_MOBILE: ['lumpsum','sip', 'AUT', ['term'], None],
    VACATION: ['lumpsum','sip', 'VAC', ['term'], None],
    JEWELLERY: ['lumpsum','sip', 'JEW', ['term'], None]
}

ALLOCATION_LIST = ['invest', 'tax', 'retirement', 'property', 'education', 'wedding', 'event','liquid','automobile','vacation','jewellery']

EQUITY = "equity"
DEBT = "debt"
ELSS = "elss"
LIQUID = "liquid"
SIP = 'sip'
LUMPSUM = 'lumpsum'
SIP_COUNT = 'sip_count'
LUMPSUM_COUNT = 'lumpsum_count'
RECOMMENDED_SCHEMES = 'recommended_schemes'
PORTFOLIO_DETAILS = 'portfolio_details'
DASHBOARD = 'dashboard'
RETIREMENT_ALLOCATION = "retirement_allocation"
ALLOCATION = "allocation"
GOAL_NAME = "goal_name"


NOT_IN_PORTFOLIO = 'not_in_portfolio'
IN_PORTFOLIO = 'in_portfolio'

EMPTY_ALLOCATION = {ELSS: "0", DEBT: "0", EQUITY: "0",LIQUID:"0"}
TAX_ALLOCATION = {"elss": "100", "debt": "0", "equity": "0","liquid":"0"}
LIQUID_ALLOCATION = {"elss": "0", "debt": "0", "equity": "0",'liquid':'100'}


TEST_API_URL = 'http://api.morningstar.com/service/mf/Price/mstarid/F0GBR06SDC?accesscode=jvon369domrbr3hcbivbdiorvkvjbb3a&startdate=2016-03-01&enddate=2016-03-04&format=json'

ALLOCATION_PROPERTY_LIST = ["retirement", "tax", "property", "education", "wedding", "event", "invest","liquid","automobile","vacation","jewellery"]

TAX_DEFAULT_TERM = 3
LIQUID_DEFAULT_TERM = 3

DUMMY_THREE_YEAR_RETURN = 13.5

FUND_MAP = {
    EQUITY: "E",
    DEBT: "D",
    ELSS: "T",
    LIQUID:"L"
}

FUND_MAP_REVERSE = {
    "E": EQUITY,
    "D": DEBT,
    "T": ELSS,
    "L":LIQUID
}

PENDING = 0
ONGOING = 1
COMPLETE = 2
CANCELLED= 3

HOLDING_PERCENTAGE = 'holding_per'
FUND_IMAGE_PATH = 'fund/image/'
SET_XIRR = 'set_xirr'
SCHEME = 'scheme'
OTHER_RECOMMENDED = 'other recommended'
MODIFIED_AT = 'modified_at'

LEGAL_NAME = 'legal_name'
DESCRIPTION = 'description'
IMAGE_URL = 'image_url'
STAR_RATING = 'star_rating'
RETURN_ONE_YEAR = 'return_one_year'
RETURN_THREE_YEAR = 'return_three_year'
RETURN_FIVE_YEAR = 'return_five_year'
RISK = 'risk'
DAY_END_NAV = 'day_end_nav'
DAY_CHANGE_NAV = 'day_change_nav'
AUM = 'aum'
DAY_END_DATE = 'day_end_date'
SCHEME_DETAILS_LIST = [LEGAL_NAME, DESCRIPTION, IMAGE_URL, STAR_RATING, RETURN_ONE_YEAR, RETURN_THREE_YEAR,
                       RETURN_FIVE_YEAR, RISK, DAY_END_NAV, DAY_CHANGE_NAV, AUM, DAY_END_DATE]

NUMBER_OF_HOLDINGS = 'Number Of Holdings'
TOP_TEN_HOLDING = 'Top 10 Holding %'
AVERAGE_MATURITY = 'Average Maturity'
MODIFIED_DURATION = 'Modified Duration'
YIELD_TO_MATURITY = 'Yield To Maturity'
TOP_FIVE_HOLDING = 'Top 5 Holding %'
TOP_THREE_SECTORS = 'Top 3 Sectors'
PORTFOLIO_TURNOVER = 'Portfolio Turnover'

TOP_PORTFOLIO_EQUITY = [NUMBER_OF_HOLDINGS, TOP_TEN_HOLDING, PORTFOLIO_TURNOVER]
TOP_PORTFOLIO_DEBT = [NUMBER_OF_HOLDINGS, TOP_TEN_HOLDING, AVERAGE_MATURITY, MODIFIED_DURATION, YIELD_TO_MATURITY]

TOP_PORTFOLIO_MAP = {
    NUMBER_OF_HOLDINGS:'number_of_holdings_total',
    TOP_TEN_HOLDING: 'top_ten_holdings',
    AVERAGE_MATURITY: 'average_maturity',
    MODIFIED_DURATION: 'modified_duration',
    YIELD_TO_MATURITY: 'yield_to_maturity'
}

TOP_PORTFOLIO_MAP_EQUITY = {
    NUMBER_OF_HOLDINGS:'number_of_holdings_total',
    TOP_TEN_HOLDING: 'top_ten_holdings',
    PORTFOLIO_TURNOVER: 'portfolio_turnover',
}

CREDIT_QUALITY_LIST = ['AAA', 'AA', 'A']

CREDIT_QUALITY_MAP ={
    'A': 'credit_quality_a',
    'AA': 'credit_quality_aa',
    'AAA': 'credit_quality_aaa'
}


DUMMY_ANALYSIS = "A fund with top-of-mind recall in the large-cap category, this fund stayed true-to-label through three market cycles over the last 20 years. It has rarely slipped below four-five stars throughout its 20-year tenure. The fund typically holds about 35-40 stocks, striving to maintain adequate diversification across companies and sectors. It adopts a buy-hold approach, with the average holding period for individual stocks at around two years. The fund's investment style leans towards growth at a reasonable price. The fund selects stocks based on classic fundamental metrics such as high RoCE, good management and the ability to deliver sustainable earnings growth."

INCEPTION_DATE = 'inception_date'
BENCHMARK = 'benchmark'
MINIMUM_INVESTMENT = 'minimum_investment'
MINIMUM_SIP_INVESTMENT = 'minimum_sip_investment'
MAX_FRONT_LOAD = 'max_front_load'
MAX_DEFERRED_LOAD = 'max_deferred_load'
EXPENSE_RATIO = 'expense_ratio'
BETA = 'beta'
INVESTMENT_STRATEGY = 'investment_strategy'

KEY_PERFORMANCE_FIELD_LIST = [INCEPTION_DATE, BENCHMARK, MINIMUM_INVESTMENT, MINIMUM_SIP_INVESTMENT, MAX_FRONT_LOAD,
                              MAX_DEFERRED_LOAD, EXPENSE_RATIO, BETA]

KEY_PERFORMANCE_MAP = {
    INCEPTION_DATE: 'Inception Date',
    BENCHMARK: 'Benchmark',
    MINIMUM_INVESTMENT: 'Minimum Investment',
    MINIMUM_SIP_INVESTMENT: 'Minimum SIP Investment',
    MAX_FRONT_LOAD: 'Max Front Load',
    MAX_DEFERRED_LOAD: 'Max Deferred Load',
    EXPENSE_RATIO: 'Expense Ratio %',
    BETA: 'Beta',
    INVESTMENT_STRATEGY: 'Investment Strategy'
}


SCHEME_DETAILS = 'scheme_details'
TYPE_OF_FUND = 'type_of_fund'
ANALYSIS = 'analysis'
KEY_PERFORMANCE = 'key_performance'
PORTFOLIO = 'portfolio'
CATEGORY_NAME = 'category_name'
LEGAL_STRUTURE = 'legal_structure'
CAPITAL_GAIN = 'capital_gain'
CAPITAL_GAIN_PERCENTAGE = 'capital_gain_percentage'
KEY = 'key'
VALUE = 'value'
TOTAL = 'total'
TOP_THREE_HOLDING_PORTFOLIO = 'Top 3 Holdings % Portfolio'
NUMBER_OF_HOLDINGS_TOP_THREE_PORTFOLIOS = 'number_of_holdings_top_three_portfolios'
HOLDINGS = 'holdings'
WEIGHTING = "Weighting"
NAME = 'name'
KEY_NAME = 'Name'
CREDIT_QUALITY = 'Credit Quality'
TOP = "top"
BOTTOM = 'bottom'
FIRST_WEIGHT = 'first_weightage'
SECOND_WEIGHT = 'second_weightage'
THIRD_WEIGHT = 'third_weightage'
FIRST_NAME = 'first_name'
SECOND_NAME = 'second_name'
THIRD_NAME = 'third_name'
TOP_THREE_SECTORS_PORTFOLIO = 'Top 3 Sectors %'
MANAGERS = 'managers'
START_DATE = 'StartDate'
FUND_MANAGER_NAME = 'Fund manager name'
FUND_MANAGER_START_DATE = 'Fund manager start date'

ELSS_FUNDS_BY_SIP = 0
LIQUID_FUNDS_BY_SIP = 0

ID = 'id'
FUND_NAME = 'fund_name'
COMAPRED_FUND = 'compared_fund'
DEBT_OTHER_DATA = 'debt_other_data'
EQUITY_OTHER_DATA = 'equity_other_data'
LIQUID_OTHER_DATA = 'liquid_other_data'
FUND_TYPES_NOT_SAME = 'The fund types were not same'
FUND_MANAGR_NAME_KEY = 'Name'

EMPTY_lIST_FOR_DATA = []

MESSAGE = 'message'
SUCCESS = 'success'
SIP_OR_LUMPSUM_TOO_LOW_ERROR = 'Sip or Lumpsum is too low. Please go to DEFINE FINANCIAL GOALS to increase them.'
DATE = 'date'
CURRENT_AMOUNT = 'current_amount'
INVESTED_AMOUNT = 'invested_amount'
XIRR = 'xirr'

USER_PORTOFOLIO_NOT_PRESENT = 'User portfolio is not present.'
USER_GOAL_NOT_PRESENT = 'User goal is not present.'
USER_PERFORMANCE_PORTOFOLIO_NOT_PRESENT = 'User performance portfolio is not present'
USER_HAS_NOT_INVESTED = 'user has not invested'
FUND_NOT_PRESENT = 'Fund related to ID not present'
FUND_LIST_INCORRECT = 'FUND list was incorrect'
IS_VIRTUAL = 'is_virtual'
FUND_CATEGORY_LIST = [EQUITY, DEBT, ELSS,LIQUID]
TIME_INTERVAL_FOR_ANNUALISED_API = 365

ONE_YEAR_RETURN = 'one_year_return'
TWO_YEAR_RETURN = 'two_year_return'
THREE_YEAR_RETURN = 'three_year_return'

INDEX_NAME = 'S&P BSE SENSEX India INR'
SENSEX = 'BSE Sensex'

PERCENTAGE = '_percentage'
NAV = 'nav'

INDEX_MAP = {
    'ICICI_Securities_Mibex_TR_INR': 1,
    'IISL_Nifty_Midcap100_PR_INR': 2,
    'S_P_BSE_200_India_INR': 3,
    'S_P_BSE_100_India_INR': 4,
    'Crisil_Composite_Bond_Index': 5
}
DATE_FORMAT = '%Y-%m-%d'
DATE = 'date'
DATES = 'dates'
FUND = 'fund'
INDEX = 'index'
CATEGORY = 'category'

CALL_UMANG = "Hie this is a demo api and specifications are unknown. If you need this changed send a mail at " \
             "umang.shukla@kuliza.com. Thanks"

DATA_FIVE_YEAR_START_DATE = '2011-01-01'
DATA_FIVE_YEAR_END_DATE = '2016-01-01'
DATA_THREE_YEAR_START_DATE = '2013-01-01'
DATA_ONE_YEAR_START_DATE = '2015-01-01'
DATA_ONE_MONTH_START_DATE = '2015-12-01'
DATA_THREE_MONTH_START_DATE = '2015-10-01'

INVEST_MINIMUM_TERM = 10

LEADER_USER_ID = 'leader_user_id'

DASHBOARD_BENCHMARKS = ['IISL Nifty 50 PR INR', 'S&P BSE SENSEX India INR']
INVESTED = 'invested'
GAIN = 'gain'
GAIN_PERCENTAGE = 'gain_per'
IS_GAIN = 'is_gain'
YOUR_PORTFOLIO = 'Your Portfolio'
BSE_SENSEX = 'BSE Sensex'
NSE_CNX_Nifty = 'NSE CNX Nifty'
PORTFOLIO_OVERVIEW = 'portfolio_overview'
INVESTED_VALUE = 'invested_value'
CURRENT_VALUE = 'current_value'
RETURN_PERCENTAGE = 'return_percentage'
CURRENT_RETURNS = 'current_return'
ASSET_CLASS_OVERVIEW = 'asset_class_overview'
YESTERDAY_CHANGE = 'yesterday_changes'
FINANCIAL_GOAL_STATUS = 'financial_goal_status'
GOAL = 'goal'
CORPUS = 'corpus'
TERM = 'term'
EXPECTD_VALUE = 'expected_value'
GOAL_ANSWERS = 'goal_answers'
INVESTMENT_TILL_DATE = 'investment_till_date'
PROGRESS = 'progress'
FUND_ID_LIST = 'fund_id_list'
CURRENT_PORTFOLIO = 'current portfolio'
FUND_PERCENTAGE = 'fund_percentage'
CATEGORY_CHOICE_REVERSE = {
    'R': "RET1",
    "T": "TAX",
    "BP": "PRO1",
    "E": "EDU1",
    "W": "WED1",
    "O": "EVT1",
    "I": "SIP1",
    "L": "LIQ",
    "AM": "AUT",
    "V": "VAC",
    "J": "JEW"
}
FINASKUS_ID_PREFIX = "FAU0"
IS_EMPTY = 'is_empty'
TOTAL_NOT_EQUAL = 'Total redemption amount does not match with sum of individual fund redeem amount. ' \
                  'Please check and fill again'
EMPTY_PORTFOLIO_HISTORIC_DATA = {CATEGORY: [], FUND: [{ID: PORTFOLIO, VALUE: []}], INDEX: [], DATES: [],
                                 INVESTED_VALUE: 0, IS_EMPTY: True}
USER_ANSWERS_NOT_PRESENT = 'user answers not present'
DEFAULT_LOW_AGE = 0
DEFAULT_HIGH_AGE = 100
DEFAULT_SAL = 0.0
DEFAULT_LOW_SCORE = 0
DEFAULT_HIGH_SCORE = 10.0
DEFAULT_GENDER = None
DEFAULT_OCCUPATION = 4

CHECK_PORTFOLIO_DISTRIBUTION_MESSAGE = 'You have modified your portfolio and selected the following scheme {}. ' \
                                       'The above selection is invalid due to minimum amount restrictions. Select ' \
                                       'another scheme.'

MOST_POPULAR_FUND = "most_popular_funds"


FUND_CATEGORY_NAME_LARGE = "Large-Cap"
FUND_CATEGORY_NAME_MID = "Small/Mid-Cap"
MAX_NUMBER_EQUITY_FUNDS = 4
MAX_NUMBER_EQUITY_FUNDS_LARGE = 3

FILTER_DATE_NOT_SELECTED = 0   # date not selected for filter
FILTER_DATE_ONE_WEEK = 1  # date selected for one week
FILTER_DATE_ONE_MONTH  = 2  # date selected for one month
FILTER_DATE_THREE_MONTH = 3  # date selected for 3 month

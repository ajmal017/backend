"""
This document will help you setup a fresh or add new funds.

Firstly make sure you have added the following in your bashrc only adding those funds whose data needs to be updated.

export MORNING_STAR_UNIVERSE_ID="XXXXXXXXXXX"
export MORNING_STAR_ACCESS_CODE="XXXXXXXXXXX"
export MORNING_STAR_UNIVERSE_ID_EQUITY='XXXXXXXXXXXXX'
export MORNING_STAR_UNIVERSE_ID_DEBT='XXXXXXXXXXXXXX'
export MORNING_STAR_UNIVERSE_ID_INDICES='XXXXXXXXXXXXX'

Make sure you have those data which MS does not provide in a csv file in the format like its present in
to decrease the work that admin will have to do.
the format is

mstar_id,fund_rank,risk,minimum_investment,minimum_sip_investment,minimum_withdrawal,minimum_balance,mapped_benchmark,sip_dates,type_of_fund,bse_neft_scheme_code,bse_rgts_scheme_code,amc_code

You can save it any csv file and put it in a constant name NON_MS_DATA_FOR FUNDS. Right now the constant is set to
funds.csv as if that data.


"""


# Open up python manage.py shell then copy the following lines next comment
from django.db.models import Min

from external_api import morningstar
from core.utils import get_current_invested_value_date
from core.models import Fund
from core import models, constants
from profiles.models import User
from profiles import utils
import requests
import datetime
import csv

morningstar_object = morningstar.MorningStarBackend()

DUMMY_ANALYSIS = "A fund with top-of-mind recall in the large-cap category, this fund stayed true-to-label through three market cycles over the last 20 years. It has rarely slipped below four-five stars throughout its 20-year tenure. The fund typically holds about 35-40 stocks, striving to maintain adequate diversification across companies and sectors. It adopts a buy-hold approach, with the average holding period for individual stocks at around two years. The fund's investment style leans towards growth at a reasonable price. The fund selects stocks based on classic fundamental metrics such as high RoCE, good management and the ability to deliver sustainable earnings growth."

def read_csv_and_populate_indices_data(csv_file_name):
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')
    for row in data_reader:
        if row[0] != 'mstar_id':
            inception_date = datetime.datetime.strptime(row[2], "%Y-%m-%d").date()
            models.Indices.objects.create(mstar_id=row[0], index_name=row[1], inception_date=inception_date)


def read_csv_and_populate_fund_data(csv_file_name):
    """
    :return:
    """
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')

    for row in data_reader:
        if row[0] != 'mstar_id':
            fund = models.Fund.objects.get(mstar_id=row[0])
            fund.fund_rank = row[1]
            fund.minimum_investment = row[3]
            fund.minimum_sip_investment = row[4]
            fund.minimum_withdrawal = row[5]
            fund.minimum_balance = row[6]
            fund.mapped_benchmark = models.Indices.objects.get(mstar_id=row[7])
            fund.sip_dates = eval(row[8])
            fund.type_of_fund = constants.FUND_MAP[str(row[9]).lower()]
            fund.bse_neft_scheme_code = row[10]
            fund.bse_rgts_scheme_code = row[11]
            fund.amc_code = row[12]
            fund.analysis = DUMMY_ANALYSIS
            print(fund.mstar_id, fund.fund_rank, fund.minimum_investment,
                  fund.minimum_sip_investment, fund.minimum_withdrawal, fund.minimum_balance,
                  fund.mapped_benchmark.mstar_id,  fund.sip_dates, fund.type_of_fund, fund.bse_neft_scheme_code,
                  fund.bse_rgts_scheme_code, fund.amc_code, sep=' ')
            answer = input('y to save')
            if answer == 'y':
                fund.save()

def add_riskometer_data(fund):
    """
    :return:
    """
    csv_file_name = 'webapp/fixtures/risk_levels.csv'  # name of the csv file
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')  # open the csv file
    for row in data_reader:
        if row[2] == fund.fund.mstar_id:
            fund.risk = row[1]
            fund.save()

NON_MS_DATA_FOR_INDICES = 'webapp/fixtures/indices.csv'
read_csv_and_populate_indices_data(NON_MS_DATA_FOR_INDICES)

# Till this step you have created an object of morning star backend and defined few function that will be need to populate data
morningstar_object.get_data_points_for_funds()

# After this command the Funds model will be populated with all the constant data the MS apis provide directly
# Now we update funds data from csv file which we dont have from MS

NON_MS_DATA_FOR_FUNDS = 'webapp/fixtures/funds.csv'  # replace it relevant csv file that you create. You can always  update these records via admin manually.
read_csv_and_populate_fund_data(NON_MS_DATA_FOR_FUNDS)

# Now as MS does not provide data for crisl related funds we will have to create records for these via admin/shell
# Create rows using in python shell like this only for non existing indices like example below
# models.Indices.objects.create(mstar_id="F00000UT07", index_name="IISL Nifty 200 PR INR", inception_date=datetime.date(2006, 1, 1))
# Also note all these mstar_id you will need it later for pulling historical data

# Now you will have to set the foreign keys for "mapped_benchmark" in Funds table
# NOTE: for cases where benchmark is any crisil index use CCIL All Sovereign TR INR
# After doing this your Funds table is completly populated after which we add historical data
# For this you have to run the below written 3 line for each mstar id of funds that you want to populate
# For one funds it can take upto 20 minutes. If you want to start from a particular date then edit the settings
# constants named START_DATE and set it to a date string of the format "yyyy-mm-dd"

#MSTAR_ID = "XXXXXXXXX" # replace this
funds = models.Fund.objects.all()
for fund in funds:
    morningstar_object.get_historical_data_points(fund.mstar_id)


# Run the next 5 line to populate the daily, monthly, equity, debt and sector related data in those tables after the
# historical data of all funds are populated
morningstar_object.get_data_points_for_fund_data_points_change_monthly()
morningstar_object.get_data_points_for_fund_data_points_change_daily()
morningstar_object.get_data_points_for_equity()
morningstar_object.get_data_points_for_sectors()
morningstar_object.get_data_points_for_debt()

# Now add the riskometer data via following lines
fund_monthly_objects = models.FundDataPointsChangeMonthly.objects.all()
for fund in fund_monthly_objects:
    add_riskometer_data(fund)

# index_map = {}
# url = 'http://api.morningstar.com/v2/service/mf/l82q5ufg7cumeb01/universeid/settings.MORNING_STAR_UNIVERSE_ID_INDICES?accesscode=settings.MORNING_STAR_ACCESS_CODE&format=json'
# indices = requests.get(url).json()
#
# for index in indices['data']:
#     index_map[index.get('_id')] = datetime.datetime.strptime(index.get('api').get('FSCBI-InceptionDate'),"%Y-%m-%d").date()
#
# for k, v in index_map.items():
#     if models.HistoricalIndexData.objects.filter(index__mstar_id=str(k)).count() == 0:
#         morningstar_object.get_historical_index_data_points(str(k),v, datetime.datetime.now().date())
# The above code pull historical data in one go for all category but that way is not recommended



# For all newly created Indices run the next two lines to pull historical data of new indexes
MSTAR_ID = "XXXX" # replace this to mstar id of index not fund!
morningstar_object.get_historical_index_data_points(MSTAR_ID, datetime.date(2006, 1, 1) , datetime.datetime.now().date())


# We can add data off category average history by running the next lines
category_code_set = set()
inception_category_code_map = {}
all_funds = models.Fund.objects.all()
# Create unique category_code iterable set
for fund in all_funds:
    category_code_set.add(fund.category_code)


# Calls the MS api to populate database this
for category in category_code_set:
    if  models.HistoricalCategoryData.objects.filter(category_code=str(category)).count() == 0:
        print("completed for "+str(category))
        morningstar_object.get_historical_category_data(str(category), datetime.date(2006, 1, 1), datetime.datetime.now().date())


# deletes records from historical index data which are older than 2006 Ideally there should not be any unless you
# have used commented script in between
models.HistoricalIndexData.objects.filter(date__year__lte=2006).delete()
models.HistoricalCategoryData.objects.filter(date__year__lte=2006).delete()
models.HistoricalFundData.objects.filter(date__year__lte=2006).delete()


#  To be run one time when you want to setup the past portfolio performance of a portfolio. Need not be used now
def make_past_portfolio_values():
    """
    :return:
    """
    order_details = models.OrderDetail.objects.filter(order_status=2).distinct('user')
    date = datetime.datetime.now()
    for user in order_details:
        print(user.user)
        new_date = date
        order_ids = models.OrderDetail.objects.filter(user=user.user, order_status=2).values_list('id', flat=True)
        inception_date = models.FundOrderItem.objects.filter(orderdetail__in=order_ids).aggregate(Min('allotment_date'))
        if inception_date["allotment_date__min"]:
            days_since_inception = (new_date.date() - inception_date["allotment_date__min"]).days
            for i in range(days_since_inception + 1):
                new_date = date - datetime.timedelta(i)
                # TODO: only add weekdays values? if new_date.isoweekday() < 6
                amount = get_current_invested_value_date(new_date, user.user)
                print(amount)
                if type(amount['xirr']) == complex:
                    amount['xirr'] = 0.0
                models.PortfolioPerformance.objects.update_or_create(
                    user=user.user, date=new_date.date(),
                    defaults={'current_amount': amount['current_amount'], 'invested_amount': amount['invested_amount'],
                              'xirr': round(amount['xirr']*100, 1)})


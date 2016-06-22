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
all_funds = Fund.objects.all()

morningstar_object.get_data_points_for_fund_data_points_change_monthly()
morningstar_object.get_data_points_for_fund_data_points_change_daily()
morningstar_object.get_data_points_for_equity()
morningstar_object.get_data_points_for_sectors()
morningstar_object.get_data_points_for_debt()

for fund in all_funds:
    morningstar_object.get_historical_data_points(fund.mstar_id)


index_map = {}
url = 'http://api.morningstar.com/v2/service/mf/l82q5ufg7cumeb01/universeid/ttr83nzvyxn4lrvs?accesscode=zy46g7rbbzici5cci8nau20l930zgg5c&format=json'
indices = requests.get(url).json()

for index in indices['data']:
    index_map[index.get('_id')] = datetime.datetime.strptime(index.get('api').get('FSCBI-InceptionDate'),"%Y-%m-%d").date()

for k, v in index_map.items():
    if models.HistoricalIndexData.objects.filter(index__mstar_id=str(k)).count() == 0:
        morningstar_object.get_historical_index_data_points(str(k),v, datetime.datetime.now().date())


category_code_set = set()
inception_category_code_map = {}

# Create unique category_code iterable set
for fund in all_funds:
    category_code_set.add(fund.category_code)

# Maps category code with most oldest inception_date of the funds which relates to that category code
for i in category_code_set:
    inception_category_code_map[i] = Fund.objects.filter(category_code=i).aggregate(Min('inception_date'))["inception_date__min"]

# Calls the MS api to populate database
for k, v in inception_category_code_map.items():
    if  models.HistoricalCategoryData.objects.filter(category_code=str(k)).count() == 0:
        morningstar_object.get_historical_category_data(str(k),v, datetime.datetime.now().date())


DUMMY_ANALYSIS = "A fund with top-of-mind recall in the large-cap category, this fund stayed true-to-label through three market cycles over the last 20 years. It has rarely slipped below four-five stars throughout its 20-year tenure. The fund typically holds about 35-40 stocks, striving to maintain adequate diversification across companies and sectors. It adopts a buy-hold approach, with the average holding period for individual stocks at around two years. The fund's investment style leans towards growth at a reasonable price. The fund selects stocks based on classic fundamental metrics such as high RoCE, good management and the ability to deliver sustainable earnings growth."

for fund in all_funds:
    i.analysis = DUMMY_ANALYSIS
    i.save()

# deletes records from historical index data which are older than 2006
models.HistoricalIndexData.objects.filter(date__year__lte=2006).delete()
models.HistoricalCategoryData.objects.filter(date__year__lte=2006).delete()
models.HistoricalFundData.objects.filter(date__year__lte=2006).delete()

for user in User.objects.all():
    if utils.is_investable(user):
        user.vault_locked = True
        user.save()

#  To be run one time when you want to setup the past portfolio performance of a portfolio
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


# Upload funds data from csv file which we dont have from MS
def read_csv_and_populate_fund_data():
    """
    :return:
    """
    csv_file_name = 'webapp/fixtures/funds.csv'  # name of the csv file
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')  # open the csv file

    # for each row except the header row populate data in table pin code
    for row in data_reader:
        if row[0] != 'mstar_id':
            fund = models.Fund.objects.get(mstar_id=row[0])
            fund_monthly_object = models.FundDataPointsChangeMonthly.objects.get(fund=fund)

            fund.fund_rank = row[1]
            fund_monthly_object.risk = row[2]
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
            print(fund.mstar_id, fund.fund_rank, fund_monthly_object.risk, fund.minimum_investment,
                  fund.minimum_sip_investment, fund.minimum_withdrawal, fund.minimum_balance,
                  fund.mapped_benchmark.mstar_id,  fund.sip_dates, fund.type_of_fund, fund.bse_neft_scheme_code,
                  fund.bse_rgts_scheme_code, fund.amc_code, sep=' ')
            answer = input('y to save')
            if answer == 'y':
                fund.save()
                fund_monthly_object.save()


# Creates a row to be updated using cron
models.CachedData.objects.create(key="most_popular_funds", value={})


# Use the MS provided risk o meter data to fill
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

# fund_monthly_objects = models.FundDataPointsChangeMonthly.objects.all()
# for fund in fund_monthly_objects:
#     add_riskometer_data(fund)
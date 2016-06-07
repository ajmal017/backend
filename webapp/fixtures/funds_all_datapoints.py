from django.db.models import Min

from external_api import morningstar
from core import models
from core.models import Fund
from profiles.models import User
from profiles import utils
import requests
import datetime

morningstar_object = morningstar.MorningStarBackend()
all_funds = Fund.objects.all()

morningstar_object.get_data_points_for_fund_data_points_change_monthly()
morningstar_object.get_data_points_for_fund_data_points_change_daily()
morningstar_object.get_data_points_for_equity()
morningstar_object.get_data_points_for_sectors()
morningstar_object.get_data_points_for_debt()

if all_funds.count() is 30:
    for fund in all_funds:
        morningstar_object.get_historical_data_points(fund.mstar_id)


index_map = {}
url = 'http://api.morningstar.com/v2/service/mf/l82q5ufg7cumeb01/universeid/ttr83nzvyxn4lrvs?accesscode=zy46g7rbbzici5cci8nau20l930zgg5c&format=json'
indices = requests.get(url).json()

for index in indices['data']:
    index_map[index.get('_id')] = datetime.datetime.strptime(index.get('api').get('FSCBI-InceptionDate'),"%Y-%m-%d").date()

for k, v in index_map.items():
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

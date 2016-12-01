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
from external_api import models as api_models
from core.utils import get_current_invested_value_date
from core.models import Fund
from core import models, constants
from profiles.models import User
from profiles import utils
from webapp.conf import settings
from django.core.files import File
import os
import requests
import datetime
import csv

DUMMY_ANALYSIS = "A fund with top-of-mind recall in the large-cap category, this fund stayed true-to-label through three market cycles over the last 20 years. It has rarely slipped below four-five stars throughout its 20-year tenure. The fund typically holds about 35-40 stocks, striving to maintain adequate diversification across companies and sectors. It adopts a buy-hold approach, with the average holding period for individual stocks at around two years. The fund's investment style leans towards growth at a reasonable price. The fund selects stocks based on classic fundamental metrics such as high RoCE, good management and the ability to deliver sustainable earnings growth."


def read_csv_and_populate_fund_data(csv_file_name):
    """
    :return:
    """
    data_reader = csv.reader(open(csv_file_name), delimiter=',', quotechar='"')

    for row in data_reader:
        if row[0] != 'mstar_id':
            fund = models.Fund.objects.update_or_create(mstar_id=row[0])
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



NON_MS_DATA_FOR_FUNDS = 'webapp/fixtures/liquid_funds.csv'  # replace it relevant csv file that you create. You can always  update these records via admin manually.
read_csv_and_populate_fund_data(NON_MS_DATA_FOR_FUNDS)


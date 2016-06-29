# -*- coding: utf-8 -*-
from enum import IntEnum
from dateutil.relativedelta import relativedelta

from django.contrib.postgres.fields import HStoreField, ArrayField
from django.db import models
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from djutil.models import TimeStampedModel

import profiles.models as profile_models
from webapp.conf import settings
from webapp.apps import random_with_N_digits
from . import manager, constants
from payment import models as payment_models

from datetime import timedelta, date


class Question(TimeStampedModel):
    """
    Model for questions for assess, plan
    """

    TYPE_CHOICES = (
        ('C', 'Checkbox'),
        ('R', 'Radio'),
        ('T', 'Text'),
        ('B', 'Blanks'),
        ('M', 'Multiple Text')
    )

    CATEGORY_CHOICE = (
        (constants.ASSESS, 'Assess'),
        (constants.PLAN, 'Plan'),
        (constants.RETIREMENT, 'Retirement'),
        (constants.TAX_SAVING, 'Tax Saving'),
        (constants.BUY_PROPERTY, 'Buy Property'),
        (constants.EDUCATION, 'Higher Education'),
        (constants.WEDDING, 'Save for Wedding'),
        (constants.OTHER_EVENT, 'Other Events'),
        (constants.INVEST, 'Invest')
    )

    question_id = models.CharField(max_length=254, blank=True)
    type = models.CharField(max_length=3, choices=TYPE_CHOICES, blank=True, default="")
    question_for = models.CharField(_('category'), max_length=254, choices=CATEGORY_CHOICE)  # this field is to define whether we are using the question for assessment,retirement plan etc.
    text = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_required = models.BooleanField(_('required'), default=False)
    is_deleted = models.BooleanField(_('deleted'), default=False)
    metadata = HStoreField(blank=True, null=True)  # For storing any extra requirement fields in future
    default_score = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    order = models.IntegerField(default=0)
    objects = manager.QuestionManager()

    def __str__(self):
        return str(self.id) + str(" " + self.get_type_display() + " " + self.get_question_for_display() + " " +str(self.question_id))

    class Meta:
        unique_together = (('order', 'question_for'), ('question_id', 'question_for'))


class Option(TimeStampedModel):
    """
    Model for options for questions
    """
    option_id = models.CharField(max_length=254, blank=True)
    text = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name="options")
    is_deleted = models.BooleanField(_('deleted'), default=False)
    metadata = HStoreField(blank=True, null=True)  # For storing any extra requirement fields in future
    weight = models.FloatField(null=True, blank=True)
    objects = manager.OptionManager()

    class Meta:
        unique_together = (('question', 'option_id'),)

    def __str__(self):
        return str(self.text) + " " + str(self.question.id)

class RiskProfile(models.Model):
    """
    Model for risk profiles description
    """
    name = models.CharField(max_length=200)
    min_score = models.FloatField(blank=False, null=False)
    max_score = models.FloatField(blank=False, null=False)
    description = models.TextField()

    def __str__(self):
        return str(self.name)


class Indices(models.Model):
    """
    Model to store index name and mstar_id
    """
    mstar_id = models.CharField(max_length=50, unique=True)
    index_name = models.CharField(max_length=100)
    inception_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.index_name)


class FundHouse(models.Model):
    """
    Model to store parent name of funds
    """
    name = models.CharField(max_length=50, unique=True)
    url1 = models.URLField(null=True, blank=True, verbose_name=('OD url'))
    url2 = models.URLField(null=True, blank=True, verbose_name=('KIAM url'))

    def __str__(self):
        return str(self.name)


class Fund(TimeStampedModel):
    """
    Stores basic information about the scheme/ mutual fund
    These values are one time thing and would not change one the database is done(mostly :P)
    """
    TYPE_CHOICES = (
        ('E', 'Equity'),
        ('D', 'Debt'),
        ('T', 'ELSS')
    )
    mapped_benchmark = models.ForeignKey(Indices, null=True, blank=True)
    isin = models.CharField(max_length=50, unique=True)  # Example : INF179K01UT0
    mstar_id = models.CharField(max_length=50, unique=True)  # Example : F00000PDZV,
    fund_id = models.CharField(max_length=50)  # Example : FSGBR071MG,
    legal_name = models.CharField(max_length=255)  # Example : HDFC Equity Fund -Direct Plan - Growth Option
    fund_standard_name = models.CharField(max_length=255)   # Example : HDFC Equity
    branding_name = models.CharField(max_length=255)  # Example : HDFC
    broad_category_group = models.CharField(max_length=50)  # Example : Equity
    legal_structure = models.CharField(max_length=50)  # Example : Open Ended Investment Company
    category_name = models.CharField(max_length=50)  # Example : Large-Cap
    inception_date = models.DateField()  # Example : 2013-01-01 The date on which a mutual fund began its operations.
    type_of_fund = models.CharField(max_length=1, choices=TYPE_CHOICES)
    benchmark = models.CharField(max_length=255, blank=True)  # The name of the primary benchmark as assigned in the fund Prospectus
    minimum_investment = models.FloatField(null=False, blank=True)  # The minimum amount an investor must invest when purchasing a fund.
    minimum_sip_investment = models.FloatField(null=False, blank=True) # The minimum amount an investor must invest when buying additional shares of a fund.
    fund_rank = models.IntegerField(null=True)
    image_url = models.ImageField(upload_to=constants.FUND_IMAGE_PATH, max_length=700, blank=True, null=True)
    category_code = models.CharField(max_length=100, null=True, blank=True)
    bse_neft_scheme_code = models.CharField(_('Scheme Code when investment amount is below Rs. 2 lakhs '),
                                            max_length=50, null=True, blank=True)
    bse_rgts_scheme_code = models.CharField(_('Scheme Code when investment amount is above Rs. 2 lakhs '),
                                            max_length=50, null=True, blank=True)
    amc_code = models.CharField(max_length=100, null=True, blank=True)
    sip_dates = ArrayField(models.IntegerField(), null=True)
    is_enabled = models.BooleanField(_('is enabled'), default=False)
    fund_house = models.ForeignKey(FundHouse, null=True, blank=True)
    analysis = models.TextField(null=True, blank=True)
    minimum_withdrawal = models.FloatField(null=True, blank=True)
    minimum_balance = models.FloatField(null=True, blank=True)
    objects = manager.FundManager()

    def __str__(self):
        return str(self.type_of_fund + " " + self.legal_name)

    @property
    def fund_name(self):
        """
        returns legal name when asked for fund name
        """
        return self.legal_name

    def get_three_year_return(self):
        try:
            return round(FundDataPointsChangeDaily.objects.get(fund=self.id).return_three_year, 2)
        except FundDataPointsChangeDaily.DoesNotExist:
            # TODO dummy value till morning star api works completely
            return constants.DUMMY_THREE_YEAR_RETURN

    def get_one_year_return(self):
        """
        :return:one year return of fund
        """
        try:
            return FundDataPointsChangeDaily.objects.get(fund=self.id).return_one_year
        except FundDataPointsChangeDaily.DoesNotExist:
            # TODO dummy value till morning star api works completely
            return constants.DUMMY_THREE_YEAR_RETURN

    class Meta:
        ordering = ['type_of_fund', 'fund_rank']


class Portfolio(TimeStampedModel):
    """
    Store the portfolio information
    """
    user = models.ForeignKey(profile_models.User)
    elss_percentage = models.FloatField(null=False, blank=False)  # these are weighted sum of pertectage of elss
    debt_percentage = models.FloatField(null=False, blank=False)  # these are weighted sum of pertectage of debt
    equity_percentage = models.FloatField(null=False, blank=False)  # these are weighted sum of pertectage of credit
    total_sum_invested = models.FloatField(null=True, blank=True, default=0.00)
    returns_value = models.FloatField(null=True, blank=True, default=0.00)
    returns_percentage = models.FloatField(null=True, blank=True, default=0.00) # change from intial investment
    # yesterday_gain = models.FloatField(null=True, blank=True, default=0.00) # change from yesterday
    # rank = models.IntegerField(null=True, blank=True)
    has_invested = models.BooleanField(_('has invested'), default=False)
    is_deleted = models.BooleanField(_('is deleted'), default=False)
    investment_date = models.DateField()

    def get_rank(self):
        """
        :return: global ranking for the Leader Board.
        """

        return Portfolio.objects.filter(returns_percentage__gte=self.returns_percentage, has_invested=True).count()

    def __str__(self):
        return str(self.user) + str(self.id)


class PortfolioItem(TimeStampedModel):
    """
    Store the items/funds of each portfolio
    """
    TYPE_CHOICES = (
        ('E', 'Equity'),
        ('D', 'Debt'),
        ('T', 'ELSS')
    )
    portfolio = models.ForeignKey(Portfolio)
    fund = models.ForeignKey(Fund)

    # Example : Equity its good to have though is equal to fund.broad_category_group
    broad_category_group = models.CharField(max_length=1, choices=TYPE_CHOICES)

    sip = models.FloatField(null=True, blank=True, default=0.00)
    lumpsum = models.FloatField(null=True, blank=True, default=0.00)
    sum_invested = models.FloatField(null=True, blank=True, default=0.00)
    returns_value = models.FloatField(null=True, blank=True, default=0.00)
    returns_percentage = models.FloatField(null=True, blank=True, default=0.00) # change from intial investment
    one_day_previous_portfolio_value = models.FloatField(null=True, blank=True, default=0.00)
    one_day_return = models.FloatField(null=True, blank=True, default=0.00)
    investment_date = models.DateField(blank=True, null=True)

    class Meta:
        unique_together = (('portfolio', 'fund'),)

    def __str__(self):
        return str(self.portfolio.user.email + " " + self.fund.fund_name + " " + self.broad_category_group + '' +
                   str(self.fund_id))

    def set_values(self, latest_index_date=None):
        # find latest nav and date from fund data points change daily table
        fund_latest_nav_object = HistoricalFundData.objects.filter(fund_id=self.fund).latest('created_at')
        fund_latest_nav = fund_latest_nav_object.nav
        fund_latest_nav_date = fund_latest_nav_object.date

        # if fund latest date is more then latest index date get nav on latest index date
        if latest_index_date is not None:
            if fund_latest_nav_date > latest_index_date:
                fund_latest_nav_object = HistoricalFundData.objects.get(fund_id=self.fund, date=latest_index_date)
                fund_latest_nav = fund_latest_nav_object.nav
                fund_latest_nav_date = fund_latest_nav_object.date

        # get one previous working day date and nav
        if fund_latest_nav_date.isoweekday() == 7:
            fund_one_previous_date = fund_latest_nav_date - timedelta(days=3)
        elif fund_latest_nav_date.isoweekday() == 6:
            fund_one_previous_date = fund_latest_nav_date - timedelta(days=2)
        else:
            fund_one_previous_date = fund_latest_nav_date - timedelta(days=1)
        one_previous_nav = HistoricalFundData.objects.get(fund_id=self.fund, date=fund_one_previous_date).nav

        # get nav on investment date(portfolios modified at is considered as investment date fr virtual dashboard)
        investment_date = self.portfolio.modified_at.date()
        if investment_date > latest_index_date:
            investment_date = latest_index_date
        months = relativedelta(date.today(), investment_date).months
        days = relativedelta(date.today(), investment_date).days
        time_since_invest = months + (1 if days >= 0 else 0)
        duration_date = investment_date + relativedelta(months=months, days=days)
        time_since_invest += relativedelta(date.today(), duration_date).years * 12

        try:
            fund_nav_on_investment = HistoricalFundData.objects.get(fund_id=self.fund, date=investment_date).nav
        except HistoricalFundData.DoesNotExist:
            fund_nav_on_investment = fund_latest_nav

        self.sum_invested = float(self.lumpsum) + (float(self.sip) * time_since_invest)
        normal_return_percentage = (fund_latest_nav - fund_nav_on_investment) / fund_nav_on_investment
        self._generate_xirr(normal_return_percentage, (fund_latest_nav_date - investment_date).days)
        self.returns_value = self.sum_invested * normal_return_percentage
        self.one_day_return = (fund_latest_nav - one_previous_nav) * self.sum_invested / fund_nav_on_investment
        self.one_day_previous_portfolio_value = self.sum_invested * (
            1 + (one_previous_nav - fund_nav_on_investment)/ fund_nav_on_investment)

    def _generate_xirr(self, simple_return, number_of_days):
        """
        generates xirr based on simple return and days

        :param simple_return: simple return in number_of_days
        :param days: the number of days
        :return:
        """
        try:
            r1 = ((1 + simple_return) ** (1 / number_of_days)) - 1
            self.returns_percentage = ((1 + r1) ** (365)) - 1
        except ZeroDivisionError:
            self.returns_percentage = 0


class Answer(TimeStampedModel):
    """
    Model for selected choices from options
    """
    question = models.ForeignKey(Question, related_name="questions")
    option = models.ForeignKey(Option, related_name="option", blank=True, null=True)
    user = models.ForeignKey(profile_models.User, related_name="user")
    is_deleted = models.BooleanField(_('deleted'), default=False)
    metadata = HStoreField(blank=True, null=True)  # For storing any extra requirement fields in future
    text = models.TextField(blank=True, null=True)
    portfolio = models.ForeignKey(Portfolio, null=True, blank=True, default=None)
    objects = manager.AnswerManager()

    def __str__(self):
        return str(self.question.question_id + " " + self.question.question_for) + " " + str(self.metadata) + " " + \
               str(self.option) + " " + str(self.text)

    class Meta:
        unique_together = (("question", "option", "user", "metadata"),)


class PlanAssestAllocation(TimeStampedModel):
    """
    Model for assest allocations
    Each of these *_allocation have an hstore value of the format
    {"debt" : "x", "equity" : "y", "elss" : "z"}
    """
    user = models.ForeignKey(profile_models.User)
    retirement_allocation = HStoreField(blank=True, null=True)
    tax_allocation = HStoreField(blank=True, null=True)
    property_allocation = HStoreField(blank=True, null=True)
    education_allocation = HStoreField(blank=True, null=True)
    wedding_allocation = HStoreField(blank=True, null=True)
    event_allocation = HStoreField(blank=True, null=True)
    invest_allocation = HStoreField(blank=True, null=True)
    portfolio = models.ForeignKey(Portfolio, null=True, blank=True, default=None)

    def __str__(self):
        return str(self.user)

    
class FundDataPointsChangeMonthly(TimeStampedModel):
    """
    Data points which needs to be updated weekly
    """
    fund = models.ForeignKey(Fund)
    star_rating = models.IntegerField()  # A star rating between 1 to 5
    risk = models.CharField(max_length=50)
    max_front_load = models.FloatField()
    max_deferred_load = models.CharField(max_length=200, default='Nil')
    expense_ratio = models.FloatField()
    managers = HStoreField()
    investment_strategy = models.TextField()

    def __str__(self):
        return str(self.id)

    def mstar_id(self):
        return self.fund.mstar_id


class FundDataPointsChangeDaily(TimeStampedModel):
    """
    Data points which needs to be updated daily
    """
    fund = models.ForeignKey(Fund, related_name="fund")
    aum = models.BigIntegerField()
    capital_gain = models.FloatField()
    capital_gain_percentage = models.FloatField()
    day_end_date = models.DateField()
    day_end_nav = models.FloatField()
    currency = models.CharField(max_length=100)
    return_one_year = models.FloatField()
    return_three_year = models.FloatField()
    return_five_year = models.FloatField()
    return_one_month = models.FloatField()
    return_three_month = models.FloatField()
    return_one_day = models.FloatField()
    beta = models.FloatField(null=False, blank=False)

    def __str__(self):
        return str(self.fund_id)


class EquityFunds(TimeStampedModel):
    """
    Stores data about the Equity Funds
    """
    fund = models.ForeignKey(Fund)
    number_of_holdings_total = models.BigIntegerField()
    top_ten_holdings = models.FloatField()
    portfolio_turnover = models.FloatField()
    number_of_holdings_top_three_portfolios = HStoreField(blank=False, null=False)

    def __str__(self):
        return str(self.fund.legal_name)


class TopThreeSectors(models.Model):
    """
    Stores data about top three sectors
    """
    equity_fund = models.ForeignKey(EquityFunds)
    first_name = models.CharField(max_length=100)
    first_weightage = models.FloatField()
    second_name = models.CharField(max_length=100)
    second_weightage = models.FloatField()
    third_name = models.CharField(max_length=100)
    third_weightage = models.FloatField()

    def __str__(self):
        return str(self.equity_fund.fund.legal_name)


class DebtFunds(TimeStampedModel):
    """
    Stores data about the DebtFunds
    """
    fund = models.ForeignKey(Fund)
    number_of_holdings_total = models.BigIntegerField()
    top_ten_holdings = models.FloatField()
    average_maturity = models.FloatField()
    modified_duration = models.FloatField()
    yield_to_maturity = models.FloatField()
    number_of_holdings_top_three_portfolios = HStoreField(blank=False, null=False)
    credit_quality_a = models.FloatField()
    credit_quality_aa = models.FloatField()
    credit_quality_aaa = models.FloatField()
    average_credit_quality = models.CharField(max_length=10)

    def __str__(self):
        return str(self.fund.legal_name)


class UserEmail(TimeStampedModel):
    """
    Stores email of user from website
    """
    user_email = models.EmailField(max_length=254, unique=True)

    def __str__(self):
        return str(self.user_email)

    class Meta:
        ordering = ['-modified_at']


class HistoricalFundData(TimeStampedModel):
    """
    Stores historical data (nav and date of nav)  for funds
    """
    fund_id = models.ForeignKey(Fund, blank=False, null=False)
    date = models.DateField(blank=False, null=False)
    nav = models.FloatField(blank=False, null=False)

    def __str__(self):
        return str(self.fund_id) + ' ' + str(self.fund_id_id) + ' ' + str(self.date)

    class Meta:
        ordering = ['-modified_at']


class HistoricalIndexData(TimeStampedModel):
    """
    Stores historical data (nav and date of nav)  for indices
    """
    index = models.ForeignKey(Indices)
    date = models.DateField(blank=False, null=False)
    nav = models.FloatField(blank=False, null=False)

    def __str__(self):
        return str(self.index.index_name)

    class Meta:
        ordering = ['-modified_at']


class HistoricalCategoryData(TimeStampedModel):
    """
    Model to store historical data(nav and date of nav) for categories
    """
    category_code = models.CharField(max_length=100)
    date = models.DateField(blank=False, null=False)
    nav = models.FloatField(blank=False, null=False)

    class Meta:
        ordering = ['-modified_at']


class FundRedeemItem(TimeStampedModel):
    """
    Model to store the historical data for Redemption
    """
    portfolio_item = models.ForeignKey(PortfolioItem)
    redeem_amount = models.FloatField(default=0.00)
    invested_redeem_amount = models.FloatField(default=0.00)
    unit_redeemed = models.FloatField(null=True, blank=True)
    redeem_date = models.DateField(null=True, blank=True, default=None)
    is_verified = models.BooleanField(_('is verified'), default=False)
    is_cancelled = models.BooleanField(_('is cancelled'), default=False)
    is_all_units_redeemed = models.BooleanField(_('Redeem all units ?'), default=False)


    def __str__(self):
        return str(self.portfolio_item.fund.legal_name)

    def get_transaction_date(self):
        """
        Returns the date of redeem
        """
        return self.created_at.date()

    def get_redeem_date(self):
        """
        Returns the date of redeem
        """
        redeem_status = self.redeemdetail_set.all()[0].redeem_status
        if self.is_cancelled == True:
            return "Cancelled"
        elif redeem_status == constants.PENDING:
            return '-'
        elif redeem_status == constants.ONGOING:
            return "Pending"
        elif redeem_status == constants.CANCELLED:
            return "Cancelled"
        return str(self.redeem_date.strftime("%d-%m-%y"))

    def get_unit_redeemed(self):
        """
        Returns the units redeemed, rounded off to 3 decimal points
        """
        if self.unit_redeemed:
            try:
                return format(self.unit_redeemed, '.3f')
            except ValueError:
                return self.unit_redeemed
        return "-"

    def get_redeem_amount(self):
        return round((self.redeem_amount) * -1.0, 2)

    def save(self, *args, **kwargs):
        """
        creates a check while saving instance of model, if is_verified is True then unit must be redeemed.
        """
        if self.is_verified and not self.unit_redeemed:
            return
        if self.is_cancelled:
            self.unit_redeemed = None
            self.redeem_date = None
            self.is_verified = False

        if self.pk:
            historical_fund_data_objects = HistoricalFundData.objects.order_by('fund_id__id', '-date').distinct('fund_id__id').select_related('fund_id')
            historical_fund_id = {historical_object.fund_id.id: historical_object.date for historical_object in historical_fund_data_objects}

            if self.redeem_date and not self.unit_redeemed and not self.is_cancelled:
                if self.redeem_date <= historical_fund_id[self.portfolio_item.fund.id]:
                    nav = HistoricalFundData.objects.get(date=self.redeem_date, fund_id=self.portfolio_item.fund).nav
                    unit_redeemed = round(self.redeem_amount / nav, 3)
                    self.unit_redeemed = unit_redeemed
                    self.is_verified = True

            if self.redeem_date and not self.is_verified and not self.is_cancelled and self.redeem_amount==0.00:
                if self.redeem_date <= historical_fund_id[self.portfolio_item.fund.id]:
                    nav_on_redeem_date = HistoricalFundData.objects.get(fund_id=self.portfolio_item.fund,
                                                                        date=self.redeem_date)
                    self.redeem_amount = self.unit_redeemed * nav_on_redeem_date.nav
                    self.is_verified = True
        return super(FundRedeemItem, self).save(*args, **kwargs)


class RedeemDetail(TimeStampedModel):
    """
    A model to group all FundRedeemItem which are related to same fund for any redeem order placed.
    """
    class RedeemStatus(IntEnum):
        """
        this is used for the choices of redeem detail status field.
        """
        Pending = 0
        Ongoing = 1
        Complete = 2
        Cancelled = 3

    redeem_id = models.CharField(max_length=10, unique=True, default=0000000000, verbose_name=_('Redeem Id'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    fund = models.ForeignKey(Fund, null=True, blank=True, default=None)
    fund_redeem_items = models.ManyToManyField(FundRedeemItem)
    redeem_amount = models.FloatField(default=0.00)
    invested_redeem_amount = models.FloatField(default=0.00)
    unit_redeemed = models.FloatField(null=True, blank=True)
    redeem_date = models.DateField(null=True, blank=True, default=None)
    is_verified = models.BooleanField(_('is verified'), default=False)
    is_cancelled = models.BooleanField(_('is cancelled'), default=False)
    is_all_units_redeemed = models.BooleanField(_('Redeem all units ?'), default=False)
    redeem_status = models.IntegerField(choices=[(x.value, x.name) for x in RedeemStatus],
                                        default=RedeemStatus.Pending.value)

    def __str__(self):
        return str(self.redeem_id + ' ' + self.user.email)

    def get_transaction_date(self):
        """
        Returns the date of redeem
        """
        return self.created_at.date()

    def get_redeem_date(self):
        """
        Returns the date of redeem
        """
        redeem_status = self.groupedredeemdetail_set.all()[0].redeem_status
        if self.is_cancelled == True:
            return "Cancelled"
        elif redeem_status == constants.PENDING:
            return 'Pending'
        elif redeem_status == constants.ONGOING:
            return "In Process"
        elif redeem_status == constants.CANCELLED:
            return "Cancelled"
        return str(self.redeem_date.strftime("%d-%m-%y"))

    def get_unit_redeemed(self):
        """
        Returns the units redeemed, rounded off to 3 decimal points
        """
        if self.is_all_units_redeemed and not self.is_verified and not self.is_cancelled:
            return "All units"
        if self.unit_redeemed:
            try:
                return str("-" + format(self.unit_redeemed, '.3f'))
            except ValueError:
                return self.unit_redeemed
        return "-"

    def get_redeem_amount(self):
        return round((self.redeem_amount) * -1.0, 2)

    def units_invested_in_portfolio_item(self, portfolio_item):
        """
        """
        unit_alloted__sum = FundOrderItem.objects.filter(
        portfolio_item=portfolio_item, is_verified=True).aggregate(Sum('unit_alloted'))['unit_alloted__sum']
        if unit_alloted__sum == None:
            unit_alloted__sum = 0.0
        unit_redeemed__sum = FundRedeemItem.objects.filter(
            portfolio_item=portfolio_item, is_verified=True).aggregate(Sum('unit_redeemed'))['unit_redeemed__sum']
        if unit_redeemed__sum == None:
            unit_redeemed__sum = 0.0

        return unit_alloted__sum - unit_redeemed__sum

    def save(self, *args, **kwargs):
        # Makes sure a redeem_id is generated when any Pending state Redeem detail is created.
        if self.redeem_id == 0:
            self.redeem_id = "RR" + str(random_with_N_digits(8))

        # Makes sure all fund_redeem_items are marked called when anyone changes redeem status to  Cancelled state
        if self.redeem_status == 3:
            for fund_redeem_item in self.fund_redeem_items.all():
                fund_redeem_item.is_cancelled = True
                fund_redeem_item.save()

        # Makes sure when redeem date is changed its reflected in fund redeem
        if self.pk:
            if self.unit_redeemed or self.unit_redeemed == 0.0:
                redeem = {}
                total_units = 0.0
                for fund_redeem_item in self.fund_redeem_items.all():
                    units = self.units_invested_in_portfolio_item(fund_redeem_item.portfolio_item)
                    redeem[fund_redeem_item.portfolio_item.id] = units
                    total_units += units

                for fund_redeem_item in self.fund_redeem_items.all():
                    if total_units:
                        fund_redeem_item.unit_redeemed = self.unit_redeemed * redeem[fund_redeem_item.portfolio_item.id]/total_units
                    else:
                        fund_redeem_item.unit_redeemed = total_units
                    fund_redeem_item.save()

        if self.pk:
            if self.invested_redeem_amount:
                redeem = {}
                total_units = 0.0
                for fund_redeem_item in self.fund_redeem_items.all():
                    units = self.units_invested_in_portfolio_item(fund_redeem_item.portfolio_item)
                    redeem[fund_redeem_item.portfolio_item.id] = units
                    total_units += units
                if total_units:
                    for fund_redeem_item in self.fund_redeem_items.all():
                        fund_redeem_item.invested_redeem_amount = self.invested_redeem_amount * redeem[
                            fund_redeem_item.portfolio_item.id] / total_units
                        fund_redeem_item.save()

        if self.pk:
            if self.redeem_amount:
                redeem = {}
                total_units = 0.0
                for fund_redeem_item in self.fund_redeem_items.all():
                    units = self.units_invested_in_portfolio_item(fund_redeem_item.portfolio_item)
                    redeem[fund_redeem_item.portfolio_item.id] = units
                    total_units += units

                if total_units:
                    for fund_redeem_item in self.fund_redeem_items.all():
                        fund_redeem_item.redeem_amount = self.redeem_amount * redeem[
                            fund_redeem_item.portfolio_item.id] / total_units
                        fund_redeem_item.save()

        historical_fund_data_objects = HistoricalFundData.objects.order_by('fund_id__id', '-date').distinct('fund_id__id').select_related('fund_id')
        historical_fund_id = {historical_object.fund_id.id: historical_object.date for historical_object in historical_fund_data_objects}

        # Makes sure when redeem date is changed its reflected in fund redeem
        if self.redeem_date:
            for fund_redeem_item in self.fund_redeem_items.all():
                fund_redeem_item.redeem_date = self.redeem_date
                fund_redeem_item.save()

        if self.pk:
            if self.redeem_date and not self.is_cancelled and not self.is_verified and not self.unit_redeemed:
                if self.redeem_date <= historical_fund_id[self.fund.id]:
                    nav = HistoricalFundData.objects.get(date=self.redeem_date, fund_id=self.fund).nav
                    unit_redeemed = round(self.redeem_amount / nav, 3)
                    self.unit_redeemed = unit_redeemed
                    self.is_verified = True

        if self.pk:
            if not self.is_cancelled and not self.is_verified and self.redeem_amount==0.00:
                if self.redeem_date and self.redeem_date <= historical_fund_id[self.fund.id]:
                    nav_on_redeem_date = HistoricalFundData.objects.get(fund_id=self.fund, date=self.redeem_date)
                    self.redeem_amount = self.unit_redeemed * nav_on_redeem_date.nav
                    self.is_verified = True

        return super(RedeemDetail, self).save(*args, **kwargs)


class GroupedRedeemDetail(TimeStampedModel):
    """
    A model to group all RedeemDetail of one order
    """
    class RedeemStatus(IntEnum):
        """
        this is used for the choices of grouped redeem detail status field.
        """
        Pending = 0
        Ongoing = 1
        Complete = 2
        Cancelled = 3

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    redeem_details = models.ManyToManyField(RedeemDetail)
    redeem_status = models.IntegerField(choices=[(x.value, x.name) for x in RedeemStatus],
                                        default=RedeemStatus.Pending.value)

    def __str__(self):
        return str(self.id) + ' ' + self.user.email

    def save(self, *args, **kwargs):

        # Makes sure all redeem details are marked cancelled when anyone changes redeem status to Cancelled state
        if self.redeem_status == 3:
            for redeem_detail in self.redeem_details.all():
                redeem_detail.is_cancelled = True
                redeem_detail.redeem_status = 3
                redeem_detail.save()

        # Makes sure all redeem details are marked ongoing too when anyone changes redeem status to Ongoing state
        if self.redeem_status == 1:
            for redeem_detail in self.redeem_details.all():
                redeem_detail.redeem_status = 1
                redeem_detail.save()
        return super(GroupedRedeemDetail, self).save(*args, **kwargs)


class FundOrderItem(TimeStampedModel):
    """
    Model to store the order item at time of payment
    """
    portfolio_item = models.ForeignKey(PortfolioItem)
    order_amount = models.FloatField(default=0.00)
    allotment_date = models.DateField(null=True, blank=True, default=None)
    next_allotment_date = models.DateField(null=True, blank=True, default=None)
    is_verified = models.BooleanField(_('is verified'), default=False)
    is_cancelled = models.BooleanField(_('is cancelled'), default=False)
    unit_alloted = models.FloatField(null=True, blank=True)
    agreed_sip = models.FloatField(default=0.00)
    agreed_lumpsum = models.FloatField(default=0.00)
    bse_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    internal_ref_no = models.CharField(max_length=10, unique=True, default=0000000000)

    def __str__(self):
        return str(self.portfolio_item.fund.legal_name)

    def get_allotment_date(self):
        """
        Returns the date of redeem
        """
        order_status = self.orderdetail_set.all()[0].order_status
        if self.is_cancelled == True:
            return "Cancelled"
        elif order_status == constants.PENDING:
            return 'Pending'
        elif order_status == constants.ONGOING:
            return "In Process"
        elif order_status == constants.CANCELLED:
            return "Cancelled"
        return str(self.allotment_date.strftime("%d-%m-%y"))

    def get_unit_alloted(self):
        """
        Returns the units alloted, rounded off to 3 decimal points
        """
        if self.unit_alloted:
            try:
                return format(self.unit_alloted, '.3f')
            except ValueError:
                return self.unit_alloted
        return "-"

    def get_transaction_date(self):
        """
        Return the date of transaction of that item
        """
        return self.created_at.date()

    def get_valid_start_date(self, fund_id, send_date):
        """
        generates valid start date for a prticular fund
        :param fund_id: id of a particular fund
        :param send_date: base date to be used as base date for finding valid start date
        :return: next valid start date
        """
        sip_dates = Fund.objects.get(id=fund_id).sip_dates
        sip_dates.sort()
        next_month = (send_date + timedelta(30))
        day = next_month.day
        if day > sip_dates[-1]:
            next_month += timedelta(30)
            next_month = next_month.replace(day=sip_dates[0])
            return next_month
        modified_day = next(date[1] for date in enumerate(sip_dates) if date[1] >= day)
        next_month = next_month.replace(day=modified_day)
        return next_month

    def save(self, *args, **kwargs):
        """
        creates a check while saving instance of model, if is_verified is True then unit must be alloted.
        """
        if self.is_verified and not self.unit_alloted:
            return
        if self.is_cancelled:
            self.unit_alloted = None
            self.next_allotment_date = None
            self.is_verified = False
            self.allotment_date = None

        # Code to set alloment date if possible and also assigns next_allotment_date
        historical_fund_data_objects = HistoricalFundData.objects.order_by('fund_id__id', '-date').distinct('fund_id__id').select_related('fund_id')
        historical_fund_id = {historical_object.fund_id.id: historical_object.date for historical_object in historical_fund_data_objects}
        if self.allotment_date and not self.unit_alloted and not self.is_cancelled:
            if self.allotment_date <= historical_fund_id[self.portfolio_item.fund.id]:
                nav = HistoricalFundData.objects.get(date=self.allotment_date, fund_id=self.portfolio_item.fund).nav
                unit_alloted = round(self.order_amount / nav, 3)
                self.unit_alloted = unit_alloted
                self.is_verified = True
                if not self.orderdetail_set.all()[0].is_lumpsum:
                    next_allotment_date = self.get_valid_start_date(self.portfolio_item.fund.id, self.allotment_date)
                    self.next_allotment_date = next_allotment_date

        return super(FundOrderItem, self).save(*args, **kwargs)


class OrderDetail(TimeStampedModel):
    """
    Model to store the order details at time of payment
    """
    class OrderStatus(IntEnum):
        """
        this is used for the choices of relationship_with_investor field.
        """
        Pending = 0
        Ongoing = 1
        Complete = 2
        Cancelled = 3

    order_id = models.CharField(max_length=10, unique=True, default=0000000000)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    fund_order_items = models.ManyToManyField(FundOrderItem)
    is_lumpsum = models.BooleanField(_('is first order'), default=False)
    order_status = models.IntegerField(choices=[(x.value, x.name) for x in OrderStatus],
                                        default=OrderStatus.Pending.value)
    transaction = models.ForeignKey(payment_models.Transaction, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id == 0:
            self.order_id = "OO" + str(random_with_N_digits(8))
        if self.order_status == 3:
            for fund_order_item in self.fund_order_items.all():
                fund_order_item.is_cancelled = True
                fund_order_item.save()
            if self.is_lumpsum:
                related_portfolio = self.fund_order_items.all()[0].portfolio_item.portfolio
                related_portfolio.is_deleted = True
                related_portfolio.save()
        return super(OrderDetail, self).save(*args, **kwargs)

    def __str__(self):
        return str(self.order_id + ' ' + self.user.email)


class ExchangeRate(models.Model):
    """
    Model to save exchange rate in case morning star api for exchange rate fails for a day
    """
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)


class FolioNumber(models.Model):
    """
    Model to store folio number of funds
    """
    folio_number = models.CharField(max_length=100)
    user = models.ForeignKey(profile_models.User)
    fund_house = models.ForeignKey(FundHouse, null=True, blank=True)

    class Meta:
        unique_together = (('user', 'fund_house'),)

    def __str__(self):
        return str(self.folio_number)


class PortfolioPerformance(models.Model):
    """
    Model to store current and invested amount of user
    """
    user = models.ForeignKey(profile_models.User)
    date = models.DateField(default=None)
    current_amount = models.FloatField()
    invested_amount = models.FloatField()
    xirr = models.FloatField(default=0.00)

    class Meta:
        unique_together = (('user', 'date'),)

    def __str__(self):
        return str(self.user.email)


class CachedData(TimeStampedModel):
    """
    A model for maintaining key value pairs of Cache data
    It is used right now for most popular funds with key set as "most_popular_funds"
    """
    key = models.CharField(max_length=100, null=True, blank=True, unique=True)
    value = HStoreField(blank=True, null=True)

    def __str__(self):
        return str(self.id)
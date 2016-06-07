from rest_framework import serializers

from . import models, helpers
from profiles import models as profile_models


class RiskProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for risk profile get
    """
    class Meta:
        """

        """
        model = models.RiskProfile


class PortfolioItemSerializer(serializers.ModelSerializer):
    """
    Serializer for portfolio item
    """

    class Meta:
        """

        """
        model = models.PortfolioItem


class PortfolioSerializer(serializers.ModelSerializer):
    """
    Serializer for portfolio
    """
    portfolio_items = PortfolioItemSerializer(source="portfolioitem_set.all", many=True)

    class Meta:
        """

        """
        model = models.Portfolio


class SwapFundsSerializer(serializers.ModelSerializer):
    """
    Serializer for swapping the funds of a portfolio
    """

    real_fund = serializers.PrimaryKeyRelatedField(queryset=models.Fund.objects.all(), required=True)
    swapped_fund = serializers.PrimaryKeyRelatedField(queryset=models.Fund.objects.all(), required=True)

    class Meta:
        """

        """
        model = models.PortfolioItem
        fields = ("real_fund", "swapped_fund")


class FundSerializer(serializers.ModelSerializer):
    """
    Serializer for fund
    """
    class Meta:
        model = models.Fund
        exclude = ['mapped_benchmark']


class FundDataPointsChangeMonthlySerializer(serializers.ModelSerializer):
    """
    Serializer for fud data points that change monthly
    """
    class Meta:
        model = models.FundDataPointsChangeMonthly
        exclude = ('fund', 'id')


class FundDataPointsChangeDailySerializer(serializers.ModelSerializer):
    """
    Serializer for fud data points that change daily
    """
    class Meta:
        model = models.FundDataPointsChangeDaily
        exclude = ('fund', 'id')


class EquityFundSerializer(serializers.ModelSerializer):
    """
    Serializer for equity funds
    """
    class Meta:
        model = models.EquityFunds
        exclude = ('fund', 'id')


class SectorFundSerializer(serializers.ModelSerializer):
    """
    Serializer for sectors
    """
    class Meta:
        model = models.TopThreeSectors
        exclude = ('equity_fund', 'id')

class DebtFundSerializer(serializers.ModelSerializer):
    """
    Serializer for debt funds
    """
    class Meta:
        model = models.DebtFunds
        exclude = ('fund', 'id')


class UserEmailSerializer(serializers.ModelSerializer):
    """
    A class to serialize and deserialize the user email instances
    """

    class Meta:
        model = models.UserEmail


class AssessSerializer(serializers.Serializer):
    """
    Serializer for assess post api
    """
    A1 = serializers.CharField(max_length=3, required=True)
    A2 = serializers.CharField(max_length=3, required=True)
    A3 = serializers.CharField(max_length=3, required=True)
    A4 = serializers.CharField(max_length=3, required=True)
    A5 = serializers.CharField(max_length=3, required=True)
    A6 = serializers.CharField(max_length=3, required=True)


class PlanSerializer(serializers.Serializer):
    """
    Serializer for plan post api
    """
    P1 = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    P2 = serializers.ListField(required=False)
    P4 = serializers.CharField(max_length=3, allow_blank=True, allow_null=True, required=False)
    P5 = serializers.CharField(max_length=50, required=True)
    P6 = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)
    P7 = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)


class RetirementSerializer(serializers.Serializer):
    """
    Serializer for plan post api
    """
    current_age = serializers.IntegerField(required=True)
    retirement_age = serializers.IntegerField(required=True)
    monthly_investment = serializers.IntegerField(required=True)
    floating_sip = serializers.BooleanField(required=True)
    grow_sip = serializers.IntegerField(required=True)
    allocation = serializers.DictField(required=True)


class InvestSerializer(serializers.Serializer):
    """
    Serializer for invest post api
    """
    term = serializers.IntegerField(required=True)
    sip = serializers.IntegerField(required=True)
    lumpsum = serializers.IntegerField(required=True)
    floating_sip = serializers.BooleanField(required=True)
    grow_sip = serializers.IntegerField(required=True)
    allocation = serializers.DictField(required=True)


class TaxSerializer(serializers.Serializer):
    """
    Serializer for tax post api
    """
    estimate_needed = serializers.BooleanField(required=True)
    pff = serializers.IntegerField(required=True)
    insurance = serializers.IntegerField(required=True)
    loan = serializers.IntegerField(required=True)
    elss = serializers.IntegerField(required=True)
    amount_allowed = serializers.IntegerField(required=True)
    amount_invested = serializers.IntegerField(required=True)


class GenericGoalSerializer(serializers.Serializer):
    """
    Serializer for generic goal post api
    """
    corpus = serializers.IntegerField(required=True)
    term = serializers.IntegerField(required=True)
    sip = serializers.IntegerField(required=True)
    lumpsum = serializers.IntegerField(required=True)
    allocation = serializers.DictField(required=True)


class FundSerializerForFundDividedIntoCategory(serializers.ModelSerializer):
    """
    Fund serializer for fund divided by category api
    """
    three_year_return = serializers.FloatField(source="get_three_year_return")

    class Meta:
        model = models.Fund
        fields = ("id", "fund_name", "three_year_return")


class LeaderBoardSerializer(serializers.ModelSerializer):
    """
    Investor Information Serializer used to display investor leader board ranking
    """

    rank = serializers.IntegerField(source='get_rank')
    user_id = serializers.CharField(source='user.id')
    returns_percentage = serializers.FloatField(source="total_xirr")

    class Meta:
        model = profile_models.AggregatePortfolio
        fields = ('returns_percentage', 'rank', 'user_id')


class LeaderBoardUserSerializer(serializers.ModelSerializer):
    """
    Investor Information Serializer used to display investor leader board ranking
    """

    rank = serializers.IntegerField(source='get_rank')
    name = serializers.CharField(source='user.investorinfo.applicant_name')
    user_id = serializers.CharField(source='user.id')
    returns_percentage = serializers.FloatField(source="total_xirr")

    class Meta:
        model = profile_models.AggregatePortfolio
        fields = ('returns_percentage', 'rank', 'name', 'user_id')


class RedeemSerializer(serializers.Serializer):
    """
    Investor Information Serializer used to display investor leader board ranking
    """

    fund_id = serializers.IntegerField(required=True)
    redeem_amount = serializers.FloatField(required=True)


class RedeemAddSerializer(serializers.Serializer):
    """
    Investor Information Serializer used to display investor leader board ranking
    """

    data = RedeemSerializer(many=True)
    total_amount = serializers.FloatField(required=True)


class FundOrderItemSerializer(serializers.ModelSerializer):
    """
    Fund order item Serializer used to display fund order item detail
    """

    fund_name = serializers.CharField(source='portfolio_item.fund.fund_name')
    transaction_date = serializers.DateField(source='get_transaction_date')
    allotment_date = serializers.CharField(source='get_allotment_date')
    unit_alloted = serializers.CharField(source='get_unit_alloted')

    class Meta:
        model = models.FundOrderItem
        fields = ('id', 'fund_name', 'unit_alloted', 'allotment_date', 'is_verified', 'order_amount',
                  'transaction_date')


class FundRedeemItemSerializer(serializers.ModelSerializer):
    """
    Fund order item Serializer used to display fund order item detail
    """

    fund_name = serializers.CharField(source='portfolio_item.fund.fund_name')
    transaction_date = serializers.DateField(source='get_transaction_date')
    allotment_date = serializers.CharField(source='get_redeem_date')
    unit_alloted = serializers.CharField(source='get_unit_redeemed')
    order_amount = serializers.FloatField(source='get_redeem_amount')

    class Meta:
        model = models.FundRedeemItem
        fields = ('id', 'fund_name', 'unit_alloted', 'allotment_date', 'is_verified', 'order_amount',
                  'transaction_date')


class FutureFundOrderItemSerializer(serializers.ModelSerializer):
    """
    Fund order item Serializer used to display futuristic fund order item detail
    """

    fund_name = serializers.CharField(source='portfolio_item.fund.fund_name')
    transaction_date = serializers.SerializerMethodField()
    allotment_date = serializers.SerializerMethodField()
    unit_alloted = serializers.SerializerMethodField()
    order_amount = serializers.SerializerMethodField()
    is_verified = serializers.SerializerMethodField()

    def get_allotment_date(self, obj):
        """
        returns future sip
        """
        return "Future Sip"

    def get_unit_alloted(self, obj):
        """
        returns unit alloted which in this case is empty
        """
        return "-"

    def get_order_amount(self, obj):
        """
        returns agreed sip when asked for order amount
        """
        return obj.agreed_sip

    def get_is_verified(self, obj):
        """
        returns verification status
        """
        return False

    def get_transaction_date(self, obj):
        """
        returns next allotment date when asked for transaction date
        """
        if obj.next_allotment_date:
            return obj.next_allotment_date.date().strftime("%d-%m-%y")
        else:
            return helpers.get_valid_start_date(obj.portfolio_item.fund.id).date().strftime("%d-%m-%y")

    class Meta:
        model = models.FundOrderItem
        fields = ('id', 'fund_name', 'unit_alloted', 'allotment_date', 'is_verified', 'order_amount',
                  'transaction_date')

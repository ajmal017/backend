from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse

from . import models
from profiles.utils import is_investable

admin.site.register(models.RiskProfile)
admin.site.register(models.LiquidFunds)

class OpinionsInline(admin.StackedInline):
    """
    Create a inline admin form for option addtion
    """
    model = models.Option


class QuestionAdmin(admin.ModelAdmin):
    """
    Hooks up question admin form with inline form
    disables the delete button
    """
    inlines = [OpinionsInline]
    readonly_fields = ('question_id','type', 'question_for', 'text', 'description', 'is_required', 'is_deleted', 'metadata', 'default_score', 'weight', 'order',)
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class UserFilter(SimpleListFilter):
    """
    to create custom filter for user's is_investor_info
    """
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        """
        gives the filter list for userfilter
        """
        return (
            ('True', 'True'),
            ('False', 'False'),
        )

    def queryset(self, request, queryset):
        """
        :returns: list of user with is_investor_info true if
         filter asked is true and vice versa
        """
        if self.value() == 'True':
            return queryset.filter(user__is_investor_info=True)
        elif self.value() == 'False':
            return queryset.filter(user__is_investor_info=False)


class OrderDetailAdmin(admin.ModelAdmin):
    """
    modify oder detail admin to include
    1. custom filter
    2. custom list display
    """
    list_filter = ['order_status', 'is_lumpsum', UserFilter]
    list_display = ['user', 'order_id', 'order_status', 'created_at', 'bank_mandate', 'button3', 'button4', 'bank_mandate_button','button5']
    search_fields = ['order_id', 'user__email']
    readonly_fields = ('user', 'transaction', 'order_id', 'list_of_fund_order_items')
    exclude = ('fund_order_items', )
    actions = None

    def form_url(self, id, legal_name):
        """
        returns a url formed for a particular fund_order_item
        :param id: id associated with a fund_order_item
        """
        url = reverse("admin:core_fundorderitem_change", args=[id])
        return mark_safe(u'<a href=%s target="_blank">%s</a>' % (url, legal_name))

    def list_of_fund_order_items(self, obj):
        """
        returns list of fund_order_item related to a order detail
        :param obj: contains an instance to fund order item object
        """
        return mark_safe(u"<br>".join([self.form_url(fund_order_item.id, fund_order_item.portfolio_item.fund.legal_name) for fund_order_item in obj.fund_order_items.all()]))

    list_of_fund_order_items.allow_tags = True
    form_url.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False


    def button3(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """

        return mark_safe('<input type="button" class="order_pipe" value="Generate Order File">')
    button3.short_description = 'Generate Order Pipe File'
    button3.allow_tags = True

    def button4(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """

        return mark_safe('<input type="button" class="xsip_registration" value="Generate Xsip registration">')
    button4.short_description = 'Generate XSIP registration'
    button4.allow_tags = True
    
    def button5(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """

        return mark_safe('<input type="button" class="send_transaction_complete_mail"  value="Send Mail for Transaction Complete">')
    button5.short_description = 'Send Mail for Transaction Complete'
    button5.allow_tags = True

    def bank_mandate_button(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button for generating bank mandate, see page no:68 in BSE StARMF File Structures.pdf
        """

        return mark_safe('<input type="button" class="bank_mandate_button" value="Generate Bank mandate">')
    bank_mandate_button.short_description = 'Generate Bank Mandate Pipe File'
    bank_mandate_button.allow_tags = True


class RedeemDetailAdmin(admin.ModelAdmin):
    """
    including list display and filters in admin
    disable the delete option
    make the fields readonly
    """
    list_filter = ['redeem_status']
    list_display = ['user', 'redeem_id', 'redeem_status']
    search_fields = ['redeem_id', 'user__email']
    readonly_fields = ('user', 'redeem_id', 'list_of_fund_redeem_items')
    exclude = ('fund_redeem_items', )
    actions = None

    def form_url(self, id, legal_name):
        """
        returns a url formed for a particular fund_order_item
        :param id: id associated with a fund_order_item
        """
        url = reverse("admin:core_fundredeemitem_change", args=[id])
        return mark_safe(u'<a href=%s target="_blank">%s</a>' % (url, legal_name))

    def list_of_fund_redeem_items(self, obj):
        """
        returns list of fund_order_item related to a order detail
        :param obj: contains an instance to fund order item object
        """
        return mark_safe(u"<br>".join([self.form_url(fund_redeem_item.id, fund_redeem_item.portfolio_item.fund.legal_name) for fund_redeem_item in obj.fund_redeem_items.all()]))

    list_of_fund_redeem_items.allow_tags = True
    form_url.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False


class GroupedRedeemDetailAdmin(admin.ModelAdmin):
    """
    including list display and filters in admin
    disable the delete option
    make the fields readonly
    """
    list_filter = ['redeem_status']
    list_display = ['user', 'redeem_status', 'id', 'redeem_detail_button']
    search_fields = ['user__email']
    readonly_fields = ('user', 'list_of_redeem_items')
    exclude = ('redeem_details', )
    actions = None

    def form_url(self, id, fund):
        """
        returns a url formed for a particular redeem detail
        :param id: id associated with a redeem_detail
        """
        url = reverse("admin:core_fundredeemitem_change", args=[id])
        return mark_safe(u'<a href=%s target="_blank">%s</a>' % (url, fund.legal_name))

    def list_of_redeem_items(self, obj):
        """
        returns list of redeem details related to a grouped redeemed detail
        :param obj: contains an instance to grouped redeem detail object
        """
        return mark_safe(u"<br>".join([self.form_url(redeem_item.id, redeem_item.portfolio_item.fund) for redeem_item in obj.fundredeemitem_set.all()]))

    list_of_redeem_items.allow_tags = True
    form_url.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def redeem_detail_button(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """

        return mark_safe('<input type="button" class="redeem_pipe" value="Generate Redeem File">')
    redeem_detail_button.short_description = 'Generate Redeem Pipe File'
    redeem_detail_button.allow_tags = True


class FundAdmin(admin.ModelAdmin):
    """
    defining list display and list editable
    disable the option of deleting
    """

    list_display = ('legal_name', 'fund_rank', 'minimum_investment', 'minimum_sip_investment', 'type_of_fund',
                    'image_url', 'mapped_benchmark')
    list_editable = ('fund_rank', 'minimum_investment', 'minimum_sip_investment', 'type_of_fund', 'image_url',
                     'mapped_benchmark')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

class FundVendorInfoAdmin(admin.ModelAdmin):
    """
    defining list display and list editable
    disable the option of deleting
    """

    list_display = ('fund', 'vendor', 'neft_scheme_code', 'rtgs_scheme_code')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

class HistoricalFundDataAdmin(admin.ModelAdmin):
    """
    to display in form of fund id, date, nav
    make fund non editable
    disable the option to delete
    """

    list_display = ('fund_id', 'date', 'nav')
    readonly_fields=('fund_id',)
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class HistoricalCategoryDataAdmin(admin.ModelAdmin):
    """
    to display in form of fund id, date, nav
    disable the option to delete
    """

    list_display = ('category_code', 'date', 'nav')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class HistoricalIndexDataAdmin(admin.ModelAdmin):
    """
    to display in form of fund id, date, nav
    make index non editable
    disable the option to delete
    """

    list_display = ('index', 'date', 'nav')
    readonly_fields=('index',)
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class FundDataPointsChangeDailyAdmin(admin.ModelAdmin):
    """
    to display in form of fund and aum
    disable the option of deleting fund data
    """

    list_display = ('fund', 'aum', 'day_end_nav', 'day_end_date')
    list_editable = ('aum',)
    readonly_fields=('fund',)
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class FundDataPointsChangeMonthlyAdmin(admin.ModelAdmin):
    """
    to display in form of fund and aum
    disable the option of deleting fund data
    """

    list_display = ('fund', 'mstar_id', 'risk')
    list_editable = ('risk',)
    readonly_fields=('fund',)
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class PortfolioAdmin(admin.ModelAdmin):
    """
    defining list filter
    disable the deletion option
    make all amount of read only type
    """
    list_display = ['user', 'has_invested', 'vault_completed']
    list_filter = ['has_invested']
    search_fields = ['user__email']
    readonly_fields = ('elss_percentage', 'debt_percentage', 'equity_percentage','liquid_percentage', 'total_sum_invested', 'returns_value', 'returns_percentage', 'list_of_goals')
    actions = None

    def form_url(self, goal_id, category):
        """
        returns a url formed for a particular redeem detail
        :param id: id associated with a redeem_detail
        """
        url = reverse("admin:core_goal_change", args=[goal_id])
        return mark_safe(u'<a href=%s target="_blank">%s</a>' % (url, category))

    def list_of_goals(self, obj):
        """
        returns list of redeem details related to a grouped redeemed detail
        :param obj: contains an instance to grouped redeem detail object
        """
        return mark_safe(u"<br>".join([self.form_url(goal.id, goal.category) for goal in obj.goal_set.all()]))

    list_of_goals.allow_tags = True
    form_url.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

    def vault_completed(self, obj):
        """
        returns vault completion  detail alongside each item
        """
        return is_investable(obj.user)
    vault_completed.short_description = 'Vault Completed'


class FundOrderItemAdmin(admin.ModelAdmin):
    """
    defining list editable
    """
    list_display = ['portfolio_item', 'order_amount', 'created_at', 'allotment_date', 'orderid']
    list_editable = ['allotment_date']
    search_fields = ['portfolio_item__portfolio__user__email', 'portfolio_item__portfolio__user__phone_number']
    readonly_fields = ('portfolio_item', )

    def has_delete_permission(self, request, obj=None):
        return False

    def orderid(self, instance):
        """
        returns the orderid for each fundorderitem
        """
        return instance.orderdetail_set.all()[0].order_id

class FundRedeemItemAdmin(admin.ModelAdmin):
    """
    defining list editable
    """
    list_display = ['portfolio_item', 'redeem_amount', 'redeemid', 'created_at', 'grouped_redeem']
    search_fields = ['portfolio_item__portfolio__user__email', 'portfolio_item__portfolio__user__phone_number', 'grouped_redeem__id']
    readonly_fields = ('portfolio_item', )

    def has_delete_permission(self, request, obj=None):
        return False

    def redeemid(self, instance):
        """
        returns the redeemid for each fundredeemtem
        """
        return instance.id

class PortfolioItemAdmin(admin.ModelAdmin):
    """
    defining list editable
    diasable the deletion option
    """
    list_display = ['portfolio__user', 'portfolio__id', 'goal', 'fund']
    search_fields = ['portfolio__user__email', 'portfolio__user__phone_number', 'portfolio__id', 'goal__id']
    readonly_fields=('portfolio', 'sip', 'lumpsum', 'sum_invested', 'returns_value', 'returns_percentage', 'one_day_previous_portfolio_value', 'one_day_return')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class FolioNumberAdmin(admin.ModelAdmin):
    """
    defining search fields
    search fields: user's email, user's phone number
    """
    search_fields = ['user__email', 'user__phone_number']
    list_display = ['user', 'fund_house', 'folio_number']


class AnswerAdmin(admin.ModelAdmin):
    """
    defining display list and search fields
    display list: question id, answer, options
    search fields: user's email, user's phone number
    """
    list_display = ['question_id', 'text', 'option', 'goal']
    readonly_fields = ('user',)
    search_fields = ['user__email', 'user__phone_number']
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class DebtFundsAdmin(admin.ModelAdmin):
    """
    defining search fields
    search fields: fund's legal name
    """
    readonly_fields = ('fund',)
    search_fields = ['fund__legal_name']
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False
    
class LiquidFundsAdmin(admin.ModelAdmin):
    """
    defining search fields
    search fields: fund's legal name
    """
    readonly_fields = ('fund',)
    search_fields = ['fund__legal_name']
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class EquityFundsAdmin(admin.ModelAdmin):
    """
    defining search fields
    search fields: fund's legal name
    """
    readonly_fields = ('fund',)
    search_fields = ['fund__legal_name']
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class FundHouseAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting the fund house
    """
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class OptionAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting the fund house
    make fields of type readonly
    """
    readonly_fields = ('question', 'option_id', 'text', 'is_deleted', 'metadata', 'weight')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class IndicesAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting the fund house
    make fields of type readonly
    """
    readonly_fields = ('mstar_id', 'index_name', 'inception_date')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class TopThreeSectorsAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting the fund house
    make fields of type readonly
    """
    readonly_fields = ('equity_fund', )
    search_fields = ['equity_fund__fund__legal_name']
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class PlanAssestAllocationAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting
    """
    readonly_fields = ('user', 'retirement_allocation', 'tax_allocation', 'property_allocation', 'education_allocation', 'wedding_allocation', 'event_allocation', 'invest_allocation', 'portfolio')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class UserEmailAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting
    """
    readonly_fields = ('user_email', )
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

class GoalAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting
    """
    list_filter = [UserFilter, 'category']
    list_display = ['id', 'user', 'name', 'category', 'portfolio', 'created_at']
    search_fields = ['category', 'user__email','portfolio__id']
    readonly_fields = ('user', 'name', 'category', 'portfolio', 'duration', 'asset_allocation', 'list_of_portfolio_items')
    actions = None

    def form_url(self, item_id, item):
        """
        returns a url formed for a particular redeem detail
        :param id: id associated with a redeem_detail
        """
        url = reverse("admin:core_portfolioitem_change", args=[item_id])
        return mark_safe(u'<a href=%s target="_blank">%s</a>' % (url, item))

    def list_of_portfolio_items(self, obj):
        """
        returns list of redeem details related to a grouped redeemed detail
        :param obj: contains an instance to grouped redeem detail object
        """
        return mark_safe(u"<br>".join([self.form_url(portfolio_item.id, portfolio_item) for portfolio_item in obj.portfolioitem_set.all()]))

    list_of_portfolio_items.allow_tags = True
    form_url.allow_tags = True

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(models.Answer, AnswerAdmin)
admin.site.register(models.FolioNumber, FolioNumberAdmin)
admin.site.register(models.Fund, FundAdmin)
admin.site.register(models.Question, QuestionAdmin)
admin.site.register(models.HistoricalFundData, HistoricalFundDataAdmin)
admin.site.register(models.HistoricalCategoryData, HistoricalCategoryDataAdmin)
admin.site.register(models.HistoricalIndexData, HistoricalIndexDataAdmin)
admin.site.register(models.FundDataPointsChangeDaily, FundDataPointsChangeDailyAdmin)
admin.site.register(models.FundDataPointsChangeMonthly, FundDataPointsChangeMonthlyAdmin)
admin.site.register(models.Portfolio, PortfolioAdmin)
admin.site.register(models.OrderDetail, OrderDetailAdmin)
admin.site.register(models.RedeemDetail, RedeemDetailAdmin)
admin.site.register(models.GroupedRedeemDetail, GroupedRedeemDetailAdmin)
admin.site.register(models.FundRedeemItem, FundRedeemItemAdmin)
admin.site.register(models.FundOrderItem, FundOrderItemAdmin)
admin.site.register(models.PortfolioItem, PortfolioItemAdmin)
admin.site.register(models.DebtFunds, DebtFundsAdmin)
admin.site.register(models.EquityFunds, EquityFundsAdmin)
admin.site.register(models.FundHouse, FundHouseAdmin)
admin.site.register(models.Option, OptionAdmin)
admin.site.register(models.Indices, IndicesAdmin)
admin.site.register(models.TopThreeSectors, TopThreeSectorsAdmin)
admin.site.register(models.PlanAssestAllocation, PlanAssestAllocationAdmin)
admin.site.register(models.UserEmail, UserEmailAdmin)
admin.site.register(models.FundVendorInfo, FundVendorInfoAdmin)
admin.site.register(models.Goal, GoalAdmin)

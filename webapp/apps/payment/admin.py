from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from rangefilter.filter import DateRangeFilter
from django.shortcuts import render

from . import models

from external_api.bse import billdesk_payment

class TransactionAdmin(admin.ModelAdmin):
    """
    add functionality to admin transaction model
    disable deleting option
    don't show bank account number
    make fields readonly
    """
    search_fields = ['user__email', 'user__phone_number']
    list_display = ['get_user_email', 'biller_id', 'txn_amount', 'txn_status', 'txn_time']
    list_filter = ['txn_status', ('txn_time', DateRangeFilter)]

    readonly_fields = ('user', 'order_details')
    exclude = ('txt_merchant_user_ref_no',)
    date_hierarchy = 'txn_time'
    actions = ['generate_bse_pipe_file']

    # disable delete action as well as delete button.
    def get_actions(self, request):
        """
        removes the delete selected users option from the drop down list of actions.
        :param request: the django request.
        :return: the list of actions without the delete action.
        """
        actions = super(TransactionAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False

    def get_user_email(self, obj):
        return obj.user.email

    def form_url(self, id):
        """
        returns a url formed for a particular order detail
        :param id: id associated with a order detail
        """
        url = reverse("admin:core_orderdetail_change", args=[id])
        return mark_safe(u'<a href=%s target="_blank">%s</a>' % (url, id))

    def order_details(self, obj):
        """
        returns link of order details related to a transaction
        :param obj: contains an instance to order detail object
        """
        return mark_safe(u"<br>".join([self.form_url(order_detail.id) for order_detail in obj.orderdetail_set.all()]))

    def generate_bse_pipe_file(self, request, queryset):
        """
        :param modeladmin:
        :param request:
        :param queryset: selected Transactions
        :return:call a function that returns pipe separated file of selected id
        """
        txn_list = queryset
        billDeskPayment_object = billdesk_payment.BillDeskPayment()
        response, error = billDeskPayment_object.generateBSEUploadFile(txn_list)
        if isinstance(response, list):
            self.message_user(request, "Error encountered." + error, level="error")
            context = dict(failed_orders_list=response)
            return render(request, 'admin/payment/transaction/failure.html', context)
        else:
            message = mark_safe("Successfully generated the bulk client master upload file.<a href='/"+"/".join(response.split("/")[-2:])+"'>Click here.</a>")
            self.message_user(request, message, level="success")


    order_details.allow_tags = True
    form_url.allow_tags = True

    get_user_email.short_description = 'User email'

admin.site.register(models.Transaction, TransactionAdmin)

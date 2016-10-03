from django.contrib import admin
from django.forms import TextInput, Textarea
from django.db import models as internal_models
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from django.shortcuts import render

from import_export import resources
from import_export.admin import ImportExportMixin
from import_export.widgets import ForeignKeyWidget
from import_export.fields import Field

from . import models
from external_api.bulk_order_entry import generate_client_pipe
from external_api.bulk_order_entry import generate_client_fatca_pipe


class BseOrKra(admin.SimpleListFilter):
    title = 'Bse Or Kra'
    parameter_name = 'verified'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        """
        return (
            ('Bse registered', _('Bse registered')),
            ('Kra verified but not BSE registered', _('Kra verified but not BSE registered')),
        )

    def queryset(self, request, queryset):
        """
        Compare the requested value (either 'registered' or 'verified')
        Checks for Bse registered OR checks
        Is Kra verifed but not Bse registered.
        """
        if self.value() == 'Bse registered':
            return queryset.filter(bse_registered=True)
        if self.value() == 'Kra verified but not BSE registered':
            investors = models.InvestorInfo.objects.filter(kra_verified=1)
            users = [investor.user.id for investor in investors]
            return queryset.filter(id__in=users, bse_registered=False).exclude(signature="")


class KraVerified(admin.SimpleListFilter):
    title = 'kra verified'
    parameter_name = 'kra_verified'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        """
        return (
            ('Yes', _('Yes')),
            ('No', _('No')),
        )

    def queryset(self, request, queryset):
        """
        Compare the requested value (either 'Yes' or 'No')
        Checks for Kra verified.
        """
        if self.value() == 'Yes':
            investors = models.InvestorInfo.objects.select_related('user').filter(kra_verified=1)
            users = [investor.user.id for investor in investors]
            return queryset.filter(id__in=users).exclude(signature="")
        if self.value() == 'No':
            investors = models.InvestorInfo.objects.select_related('user').filter(kra_verified=0)
            users = [investor.user.id for investor in investors]
            return queryset.filter(id__in=users)


class VaultComplete(admin.SimpleListFilter):
    title = 'Vault Complete'
    parameter_name = 'vault'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        """
        return (
            ('Vault Complete', _('Vault Complete')),
            ('Vault Incomplete', _('Vault Incomplete')),
        )

    def queryset(self, request, queryset):
        """
        Segregates a user as vault complete or not
        """
        if self.value() == 'Vault Complete':
            return queryset.exclude(signature="")
        if self.value() == 'Vault Incomplete':
            return queryset.filter(signature="")


class UserAdmin(admin.ModelAdmin):
    """
    to achieve:
    1. Changing User Phone number or email id
    2. To add remarks against a user
    3. Be able to trigger a email id verification from admin panel
    4. Showing total online users at a time
    """
    formfield_overrides = {
        internal_models.CharField: {'widget': TextInput(attrs={'size': '10'})},
        internal_models.EmailField: {'widget': TextInput(attrs={'size': '17'})},
        internal_models.TextField: {'widget': Textarea(attrs={'rows': '2', 'cols': '40'})},
    }
    search_fields = ['phone_number', 'email', 'finaskus_id']
    list_display = ['id', 'email', 'phone_number', 'get_vault_complete', 'get_kra_verification', 'bse_registered',
                    'tiff_mailed', 'tiff_accepted', 'kyc_mailed', 'kyc_accepted', 'mandate_status', 'xsip_status',
                    'finaskus_id', 'mandate_reg_no', 'remarks', 'button', 'button1', 'button2', 'button3', 'button4']
    list_editable = ['email', 'phone_number', 'remarks', 'finaskus_id', 'mandate_reg_no']
    list_filter = ['phone_number_verified', 'email_verified', 'mandate_status', BseOrKra, VaultComplete, KraVerified]
    exclude = ('password', 'id', 'username', 'last_login', )
    empty_value_display = 'unknown'
    actions = ['generate_client_ucc_pipe_file', 'generate_client_fatca_pipe_file']

    # disable delete action as well as delete button.
    def get_actions(self, request):
        """
        removes the delete selected users option from the drop down list of actions.
        :param request: the django request.
        :return: the list of actions without the delete action.
        """
        actions = super(UserAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        removes the delete red button inside each user object.
        :param request: the django request.
        :param obj: None by default.
        :return: To disable we return False
        """
        return False

    def generate_client_ucc_pipe_file(self, request, queryset):
        """

        :param modeladmin:
        :param request:
        :param queryset: selected users
        :return:call a function that returns pipe separated file of selected id
        """

        user_id_list = []
        for item in queryset:
            user_id_list.append(item.id)
        response = generate_client_pipe(user_id_list)

        if isinstance(response, list):
            self.message_user(request, "Error encountered.", level="error")
            context = dict(failed_users_list=response)
            return render(request, 'admin/profiles/user/failure.html', context)
        else:
            message = mark_safe("Successfully generated the bulk client master upload file.<a href='/"+"/".join(response.split("/")[-2:])+"'>Click here.</a>")
            self.message_user(request, message, level="success")

    def generate_client_fatca_pipe_file(self, request, queryset):
        """

        :param modeladmin:
        :param request:
        :param queryset: selected users
        :return:call a function that returns pipe separated file of selected id
        """
        user_id_list = []
        for item in queryset:
            user_id_list.append(item.id)
        response = generate_client_fatca_pipe(user_id_list)

        if isinstance(response, list):
            self.message_user(request, "Error encountered.", level="error")
            context = dict(failed_users_list=response)
            return render(request, 'admin/profiles/user/failure.html', context)
        else:
            message = mark_safe("Successfully generated the bulk client fatca upload file.<a href='/"+"/".join(response.split("/")[-2:])+"'>Click here.</a>")
            self.message_user(request, message, level="success")

    def button(self, obj):
        """
        :param obj: an obj of User admin
        :return: a button
        """
        return mark_safe('<input type="button" class="email" value="Resend Email">')
    button.short_description = 'Resend Email'
    button.allow_tags = True

    def button1(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """

        return mark_safe('<input type="button" class="investor_pdf" value="Generate Investor PDF">')
    button1.short_description = 'Generate Investor Pdf'
    button1.allow_tags = True

    def button3(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """

        return mark_safe('<input type="button" class="kyc_pdf" value="Generate Kyc PDF">')
    button3.short_description = 'Generate Kyc Pdf'
    button3.allow_tags = True

    def button2(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button
        """
        return mark_safe('<input type="button" class="tiff" value="Generate Tiff">')
    button2.short_description = 'Generate Tiff'
    button2.allow_tags = True

    def button4(self, obj):
        """
        :param obj: an obj of user Admin
        :return: a button to generate the mandate_pdf
        """
        return mark_safe('<input type="button" class="mandate" value="Generate Bank Mandate">')
    button4.short_description = 'Generate Bank Mandate'
    button4.allow_tags = True

    def get_kra_verification(self, obj):
        """
        To show kra verification on user admin
        """
        try:
            return obj.investorinfo.kra_verified
        except Exception:
            return False
    get_kra_verification.short_description = 'kra verification'

    def get_vault_complete(self, obj):
        """
        To show if user's vault is complete
        """

        return True if obj.signature != "" else False
    get_vault_complete.short_description = 'Vault complete'

    def changelist_view(self, request):
        """
        calculating total active users to display in admin panel
        """
        return super(UserAdmin, self).changelist_view(
            request, extra_context={
                'active_user': self.model.objects.filter(is_active=True).count()

            })


class AppointmentDetailsResource(resources.ModelResource):
    """
    defining the feilds to be exported by AppointmentDetailsAdmin
    """
    name = Field(column_name='First name', attribute='user', widget=ForeignKeyWidget(models.User, "first_name"))
    last_name = Field(column_name='Last name', attribute='user', widget=ForeignKeyWidget(models.User, "last_name"))
    phone_no = Field(column_name='Phone no', attribute='user', widget=ForeignKeyWidget(models.User, "phone_number"))
    address = Field(column_name='Complete Address', attribute='address', widget=ForeignKeyWidget(models.Address,
                                                                                        "address_line_1"))
    nearest_landmark = Field(column_name='Nearest Landmark', attribute='address',
                             widget=ForeignKeyWidget(models.Address, "nearest_landmark"))
    pincode = Field(column_name='Pincode', attribute='address', widget=ForeignKeyWidget(models.Address, 'pincode'))

    class meta:
        model = models.AppointmentDetails
        fields = ('name', 'last_name', 'phone_no', 'address', 'nearest_landmark', 'pincode', 'date', 'time')
        export_order = ('name', 'last_name', 'phone_no', 'nearest_landmark', 'date', 'time', 'address', 'pincode')


class AppointmentDetailsAdmin(ImportExportMixin, admin.ModelAdmin):
    """
    to achieve:
    1. Appointment details for documents pick up
    2. Display list on basis of user name and address
    """
    list_display = ['get_user_name', 'get_address',]
    resource_class = AppointmentDetailsResource
    list_filter = ['status']

    def get_user_name(self, obj):
        """
        To get the full_name of user
        """
        return obj.user.get_full_name()
    get_user_name.admin_order_field = 'user'
    get_user_name.short_description = 'User Name'

    def get_address(self, obj):
        """
        to get combined address and pincode
        """
        address = obj.address.address_line_1
        pinode = obj.address.nearest_landmark
        name = address + pinode
        return name
    get_address.admin_order_field = 'address'  #Allows column order sorting
    get_address.short_description = 'Address'  #Renames column head


class ContactInfoAdmin(admin.ModelAdmin):
    """
    list display on basis of user and communication address
    """
    readonly_fields = ['user']
    list_display = ['user', 'communication_address']
    # searchable by email in contact info model not user model
    search_fields = ['email']

    # disable delete action as well as delete button.
    def get_actions(self, request):
        """
        removes the delete selected contact info option from the drop down list of actions.
        :param request: the django request.
        :return: the list of actions without the delete action.
        """
        actions = super(ContactInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        removes the delete red button inside each user object.
        :param request: the django request.
        :param obj: None by default.
        :return: To disable we return False
        """
        return False


class VerificationSMSCodeAdmin(admin.ModelAdmin):
    """
    to show:
    1. users who didnot verfy OTP
    2. Search on basis of user email and phone number
    """
    search_fields = ['user__email', 'user__phone_number']
    readonly_fields = ('user', 'sms_code')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request):
        """
        calculate total records in VerificationSMSCode
        """
        return super(VerificationSMSCodeAdmin, self).changelist_view(
            request, extra_context={
                'object': self.model.objects.all().count()

            })


class EmailCodeAdmin(admin.ModelAdmin):
    """
    to show:
    1. users who didnot verfy Email
    2. Search on basis of user email and phone number
    """
    search_fields = ['user__email', 'user__phone_number']
    readonly_fields = ('user', 'code', 'expires_at')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request):
        """
        calculate total records in EmailCode
        """
        return super(EmailCodeAdmin, self).changelist_view(
            request, extra_context={
                'object': self.model.objects.all().count()

            })


class InvestorInfoAdmin(admin.ModelAdmin):
    """
    to get the list filter
    """
    list_filter = ['kra_verified']
    search_fields = ['user__email']
    exclude = ("account_number",)
    readonly_fields = ['user']

    # disable delete action as well as delete button.
    def get_actions(self, request):
        """
        removes the delete selected investor info option from the drop down list of actions.
        :param request: the django request.
        :return: the list of actions without the delete action.
        """
        actions = super(InvestorInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        removes the delete red button inside each user object.
        :param request: the django request.
        :param obj: None by default.
        :return: To disable we return False
        """
        return False


class InvestorBankDetails(admin.ModelAdmin):
    """
    to get searchable by email field for investor bank details
    """
    search_fields = ['user__email']
    exclude = ['account_number']

    # disable delete action as well as delete button.
    def get_actions(self, request):
        """
        removes the delete selected investor bank details option from the drop down list of actions.
        :param request: the django request.
        :return: the list of actions without the delete action.
        """
        actions = super(InvestorBankDetails, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        removes the delete red button inside each user object.
        :param request: the django request.
        :param obj: None by default.
        :return: To disable we return False
        """
        return False


class NomineeInfoAdmin(admin.ModelAdmin):
    """
    to get searchable by email id
    """
    search_fields = ['user__email']
    readonly_fields = ['user']

    # disable delete nominee info as well as delete button.
    def get_actions(self, request):
        """
        removes the delete selected nominee info option from the drop down list of actions.
        :param request: the django request.
        :return: the list of actions without the delete action.
        """
        actions = super(NomineeInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        """
        removes the delete red button inside each user object.
        :param request: the django request.
        :param obj: None by default.
        :return: To disable we return False
        """
        return False


class AddressAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting the fund house
    """
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class UserChangedPhoneNumberAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting
    """
    readonly_fields=('user', 'sms_code', 'phone_number')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class AggregatePortfolioAdmin(admin.ModelAdmin):
    """
    disbale the option of deleting
    """
    readonly_fields=('user', 'total_xirr', 'update_date')
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(models.User, UserAdmin)
admin.site.register(models.VerificationSMSCode,VerificationSMSCodeAdmin)
admin.site.register(models.EmailCode,EmailCodeAdmin)
admin.site.register(models.InvestorInfo, InvestorInfoAdmin)
admin.site.register(models.Address, AddressAdmin)
admin.site.register(models.ContactInfo, ContactInfoAdmin)
admin.site.register(models.NomineeInfo, NomineeInfoAdmin)
admin.site.register(models.AggregatePortfolio, AggregatePortfolioAdmin)
admin.site.register(models.InvestorBankDetails, InvestorBankDetails)
admin.site.register(models.AppointmentDetails, AppointmentDetailsAdmin)
admin.site.register(models.UserChangedPhoneNumber, UserChangedPhoneNumberAdmin)

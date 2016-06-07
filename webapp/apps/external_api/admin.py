from django.contrib import admin

from import_export.admin import ImportExportMixin

from . import models


class PincodeAdmin(admin.ModelAdmin):
    """
    to display list on basis of city, state, pincode
    """
    list_display = ['city', 'state', 'pincode']
    filter = ['city']
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False


class VerifiablePincodeAdmin(admin.ModelAdmin):
    """
    to achieve:
    1. Pin codes master, along with list of pincodes served or Districts served
    """
    filter_horizontal = ['pincode']


class BankDetailsAdmin(ImportExportMixin, admin.ModelAdmin):
    """
    disable delete option
    To import iifc codes
    """
    actions = None

    def has_delete_permission(self, request, obj=None):
        return False

class SMSAdmin(admin.ModelAdmin):
    """
    to achieve:
    1. Adds searchable feature via to field
    """
    search_fields = ['to']

admin.site.register(models.SMS, SMSAdmin)
admin.site.register(models.VerifiablePincode, VerifiablePincodeAdmin)
admin.site.register(models.Pincode, PincodeAdmin)
admin.site.register(models.BankDetails, BankDetailsAdmin)


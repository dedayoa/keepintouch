from django.contrib import admin

# Register your models here.

from import_export.admin import ImportExportMixin
from country_dialcode.models import Prefix
from country_dialcode.admin import PrefixAdmin
from .models import KITBilling, KITServicePlan, KITSystem, EmailReport, SMSReport, \
                    SMSRateTable

class MyPrefixAdmin(ImportExportMixin, PrefixAdmin):
    pass

class KITBillingAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(KITBillingAdmin, self).get_queryset(request)
        
        return qs.filter(kit_admin__is_admin=True)

    
    
class SMSRateTableAdmin(ImportExportMixin, admin.ModelAdmin):
    
    list_display = ("dialcode","sms_units")


class EmailReportAdmin(admin.ModelAdmin):
    
    list_display = ('__str__','status','created')
    
class SMSReportAdmin(admin.ModelAdmin):
    
    list_display = ('__str__','status','created')

admin.site.register(KITBilling, KITBillingAdmin)
admin.site.register(KITServicePlan)
admin.site.register(KITSystem)
admin.site.register(SMSRateTable, SMSRateTableAdmin)
admin.site.register(EmailReport, EmailReportAdmin)
admin.site.register(SMSReport, SMSReportAdmin)
admin.site.unregister(Prefix)
admin.site.register(Prefix, MyPrefixAdmin)


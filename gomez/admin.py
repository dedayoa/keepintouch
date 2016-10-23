from django.contrib import admin

# Register your models here.

from import_export.admin import ImportExportMixin
from country_dialcode.models import Prefix
from country_dialcode.admin import PrefixAdmin
from .models import KITBilling, KITServicePlan, KITSystem, EmailReport, SMSReport, \
                    SMSRateTable, Product, Order, Invoice, OrderLine, PaymentMethod


class SMSRateTableInline(admin.TabularInline):
    
    model = SMSRateTable

class MyPrefixAdmin(ImportExportMixin, PrefixAdmin):
    inlines = [
        SMSRateTableInline,
    ]
    list_display = ('prefix','destination','get_sms_rate')
    
    def get_sms_rate(self, obj):
        return obj.smsratetable.sms_units
    get_sms_rate.short_description = 'SMS Rate'

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

admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Invoice)
admin.site.register(OrderLine)
admin.site.register(PaymentMethod)


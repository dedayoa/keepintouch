from django.contrib import admin

# Register your models here.

from .models import SMSDeliveryReport, SMSDeliveryReportHistory, SMSDeliveryReportTransaction

class SMSDeliveryReportHistoryAdmin(admin.ModelAdmin):
    
    list_display = ('id','created') 

admin.site.register(SMSDeliveryReport)
admin.site.register(SMSDeliveryReportHistory, SMSDeliveryReportHistoryAdmin)
admin.site.register(SMSDeliveryReportTransaction)
from django.contrib import admin

# Register your models here.

from .models import SMSDeliveryReport, SMSDeliveryReportHistory, SMSDeliveryReportTransaction,\
                    EmailDeliveryReport, EmailEventHistory

class SMSDeliveryReportHistoryAdmin(admin.ModelAdmin):
    
    list_display = ('id','created')
    
class SMSDeliveryReportTransactionAdmin(admin.ModelAdmin):
    
    list_display = ('body','date_received','status')

admin.site.register(SMSDeliveryReport)
admin.site.register(SMSDeliveryReportHistory, SMSDeliveryReportHistoryAdmin)
admin.site.register(SMSDeliveryReportTransaction, SMSDeliveryReportTransactionAdmin)
admin.site.register(EmailDeliveryReport)


from django.contrib import admin

# Register your models here.

from .models import SMSDeliveryReport, SMSDeliveryReportHistory, SMSDeliveryReportTransaction,\
                    EmailDeliveryReport, EmailEventHistory

class SMSDeliveryReportAdmin(admin.ModelAdmin):
    def recipient(self, obj):
        return obj.to_phone.as_international
    
    list_display = ('sms_sender','recipient','msg_status')


class SMSDeliveryReportHistoryAdmin(admin.ModelAdmin):
    
    list_display = ('id','created')
    
class SMSDeliveryReportTransactionAdmin(admin.ModelAdmin):
    
    list_display = ('body','date_received','status')
    
    
class EmailDeliveryReportAdmin(admin.ModelAdmin):
    list_display = ('from_email','to_email','msg_status','created')

admin.site.register(SMSDeliveryReport, SMSDeliveryReportAdmin)
admin.site.register(SMSDeliveryReportHistory, SMSDeliveryReportHistoryAdmin)
admin.site.register(SMSDeliveryReportTransaction, SMSDeliveryReportTransactionAdmin)
admin.site.register(EmailDeliveryReport, EmailDeliveryReportAdmin)


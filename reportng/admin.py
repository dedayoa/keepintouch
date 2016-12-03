from django.contrib import admin

# Register your models here.

from .models import SMSDeliveryReport, SMSDeliveryReportHistory, SMSDeliveryReportTransaction,\
                    EmailDeliveryReport, EmailEventHistory, CallDetailReportTransaction, CallDetailReport,\
                    EmailReportTransaction

class SMSDeliveryReportAdmin(admin.ModelAdmin):
    def recipient(self, obj):
        return obj.to_phone.as_international
    
    list_display = ('sms_sender','recipient','msg_status')


class SMSDeliveryReportHistoryAdmin(admin.ModelAdmin):
    
    list_display = ('id','created')
    
class SMSDeliveryReportTransactionAdmin(admin.ModelAdmin):
    
    list_display = ('body','date_received','status')
    
class CallDetailReportAdmin(admin.ModelAdmin):
    
    list_display = ('a_leg_call_start','a_leg_called_number','b_leg_called_number','get_total_call_cost')
    
    
class CallDetailReportTransactionAdmin(admin.ModelAdmin):
    
    list_display = ('call_uuid','date_received','status')
    
    
class EmailDeliveryReportAdmin(admin.ModelAdmin):
    list_display = ('from_email','to_email','msg_status','created')
    
class EmailReportTransactionAdmin(admin.ModelAdmin):
    
    list_display = ('body','date_received','status')

admin.site.register(SMSDeliveryReport, SMSDeliveryReportAdmin)
admin.site.register(SMSDeliveryReportHistory, SMSDeliveryReportHistoryAdmin)
admin.site.register(SMSDeliveryReportTransaction, SMSDeliveryReportTransactionAdmin)
admin.site.register(CallDetailReportTransaction, CallDetailReportTransactionAdmin)
admin.site.register(EmailDeliveryReport, EmailDeliveryReportAdmin)
admin.site.register(CallDetailReport, CallDetailReportAdmin)
admin.site.register(EmailReportTransaction, EmailReportTransactionAdmin)


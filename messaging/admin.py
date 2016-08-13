from django.contrib import admin

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages,\
                    QueuedMessages, EmailReport, SMSReport, ReminderMessaging, Reminder

class EmailReportAdmin(admin.ModelAdmin):
    
    list_display = ('__str__','status','created')
    
class SMSReportAdmin(admin.ModelAdmin):
    
    list_display = ('status','created')


admin.site.register(StandardMessaging)
admin.site.register(AdvancedMessaging)
admin.site.register(ProcessedMessages)
admin.site.register(QueuedMessages)
admin.site.register(EmailReport, EmailReportAdmin)
admin.site.register(SMSReport, SMSReportAdmin)
admin.site.register(ReminderMessaging)
admin.site.register(Reminder)

from django.contrib import admin

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages,\
                    QueuedMessages, IssueFeedback, ReminderMessaging, Reminder,\
                    RunningMessage, FailedEmailMessage, FailedSMSMessage, FailedKITMessage



admin.site.register(StandardMessaging)
admin.site.register(AdvancedMessaging)
admin.site.register(ProcessedMessages)
admin.site.register(QueuedMessages)
admin.site.register(ReminderMessaging)
admin.site.register(Reminder)
admin.site.register(RunningMessage)
admin.site.register(FailedEmailMessage)
admin.site.register(FailedSMSMessage)
admin.site.register(FailedKITMessage)
admin.site.register(IssueFeedback)

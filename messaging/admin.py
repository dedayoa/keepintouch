from django.contrib import admin

from .models import StandardMessaging, AdvancedMessaging, ProcessedMessages,\
                    QueuedMessages

admin.site.register(StandardMessaging)
admin.site.register(AdvancedMessaging)
admin.site.register(ProcessedMessages)
admin.site.register(QueuedMessages)

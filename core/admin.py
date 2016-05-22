from django.contrib import admin

# Register your models here.

from .models import CoAdmin, Contact, CoUser, MessageTemplate, \
                    Event, PublicEvent, SentMessage, SMTPSetting, CoGroup

class ContactAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event)
admin.site.register(PublicEvent)
admin.site.register(Contact)
admin.site.register(SentMessage)
admin.site.register(MessageTemplate)
admin.site.register(SMTPSetting)
admin.site.register(CoAdmin)
admin.site.register(CoUser)
admin.site.register(CoGroup)

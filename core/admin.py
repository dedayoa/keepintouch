from django.contrib import admin

# Register your models here.

from .models import Contact, KITUser, MessageTemplate, \
                    Event, PublicEvent, SentMessage, SMTPSetting, CoUserGroup

class ContactAdmin(admin.ModelAdmin):

    list_display = ('first_name','last_name','active')


admin.site.register(Event)
admin.site.register(PublicEvent)
admin.site.register(Contact, ContactAdmin)
admin.site.register(SentMessage)
admin.site.register(MessageTemplate)
admin.site.register(SMTPSetting)
admin.site.register(KITUser)
admin.site.register(CoUserGroup)

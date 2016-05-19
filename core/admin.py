from django.contrib import admin

# Register your models here.

from .models import CoAdmin, Contact, ContactList, CoUser, Event, Message, SMTPSetting, CoGroup

class ContactAdmin(admin.ModelAdmin):
    pass


admin.site.register(Event)
admin.site.register(Contact)
admin.site.register(Message)
admin.site.register(ContactList)
admin.site.register(SMTPSetting)
admin.site.register(CoAdmin)
admin.site.register(CoUser)
admin.site.register(CoGroup)

from django.contrib import admin

# Register your modelx here.

from .models import Contact, KITUser, Event, PublicEvent, MessageTemplate, \
                    SentMessage, SMTPSetting, CoUserGroup, ContactGroup, FundsTransfer,\
                    UploadedContact, CustomData, KITUBalance, KITActivationCode,\
                    OrganizationContact


class ContactAdmin(admin.ModelAdmin):
    
    search_fields = ['first_name','last_name','email','phone']

    list_display = ('first_name','last_name','active')
    
class KITUserAdmin(admin.ModelAdmin):
    
    def user_group(self, obj):
        return ", ".join(p.title for p in obj.groups_adminover.all())
    user_group.short_description = "Groups Admin Over"
    
    list_display = ('user','parent','is_admin','user_group','ip_address')

class CoUserGroupAdmin(admin.ModelAdmin):
    
    list_display = ('title','kit_admin')
    
    
class KITActivationCodeAdmin(admin.ModelAdmin):
    list_display = ('user','email_activation_code','phone_activation_code','created','expired')

    
class KITUBalanceAdmin(admin.ModelAdmin):
    
    list_display = ('kit_user','user_balance')
    
    def get_queryset(self, request):
        qs = super(KITUBalanceAdmin, self).get_queryset(request)
        
        if request.user.is_staff and not request.user.is_superuser:
            return qs.filter(kit_user__is_admin=True)
        else:
            return qs


    
admin.site.register(Event)
admin.site.register(PublicEvent)
admin.site.register(UploadedContact)
admin.site.register(FundsTransfer)
admin.site.register(KITUBalance, KITUBalanceAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(ContactGroup)
admin.site.register(SentMessage)
admin.site.register(CustomData)
admin.site.register(MessageTemplate)
admin.site.register(SMTPSetting)
admin.site.register(KITUser, KITUserAdmin)
admin.site.register(OrganizationContact)
admin.site.register(KITActivationCode, KITActivationCodeAdmin)
admin.site.register(CoUserGroup, CoUserGroupAdmin)

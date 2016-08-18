from django.contrib import admin

# Register your models here.

from .models import KITBilling, KITServicePlan, KITSystem, IssueFeedback

class KITBillingAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(KITBillingAdmin, self).get_queryset(request)
        
        return qs.filter(kit_admin__is_admin=True)


admin.site.register(KITBilling, KITBillingAdmin)
admin.site.register(KITServicePlan)
admin.site.register(KITSystem)
admin.site.register(IssueFeedback)

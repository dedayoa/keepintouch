from django.contrib import admin

# Register your models here.

from .models import KITBilling, KITServicePlan, KITSystem, IssueFeedback, CustomData

admin.site.register(KITBilling)
admin.site.register(KITServicePlan)
admin.site.register(KITSystem)
admin.site.register(IssueFeedback)
admin.site.register(CustomData)
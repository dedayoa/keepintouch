from django.contrib import admin

# Register your models here.

from .models import KITBilling, KITServicePlan, KITSystem

admin.site.register(KITBilling)
admin.site.register(KITServicePlan)
admin.site.register(KITSystem)
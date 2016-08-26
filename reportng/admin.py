from django.contrib import admin

# Register your models here.

from .models import SMSDeliveryReport, SMSDeliveryReportHistory

admin.site.register(SMSDeliveryReport)
admin.site.register(SMSDeliveryReportHistory)
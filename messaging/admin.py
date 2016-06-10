from django.contrib import admin

from .models import StandardMessaging, AdvancedMessaging

admin.site.register(StandardMessaging)
admin.site.register(AdvancedMessaging)

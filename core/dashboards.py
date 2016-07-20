'''
Created on Jul 20, 2016

@author: Dayo
'''
import datetime

from django.db.models import Count
from django.utils import timezone
from controlcenter import Dashboard, widgets
from messaging.models import QueuedMessages, ProcessedMessages
from .models import PublicEvent


class PublicEventWidget(widgets.ItemList):
    
    title = 'Public Anniversaries'
    model = PublicEvent
    list_display = []
    
class InTouchDashboard(Dashboard):
    widgets = (
        PublicEventWidget,
    )
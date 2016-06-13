'''
Created on Jun 12, 2016

@author: Dayo
'''
import django_filters

from .models import ProcessedMessages

class ProcessedMessagesFilter(django_filters.FilterSet):
    
    
    MSG_TYPE = (
        ('ADVANCED',' Advanced'),
        ('STANDARD',' Standard')
                )
    
    message_type = django_filters.ChoiceFilter(label="Filter by Message Type", choices=MSG_TYPE)
    
    
    class Meta:
        model = ProcessedMessages
        fields = ['message_type']
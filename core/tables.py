'''
Created on May 23, 2016

@author: Dayo
'''

import django_tables2 as tables
from django_tables2.utils import A
from .models import Contact, MessageTemplate, Event, PublicEvent,\
                    CoUser, CoAccount, SMTPSetting


class TableSelectColumn(tables.CheckBoxColumn):
    
    def render(self):
        return self

class ContactTable(tables.Table):
    
    select = tables.CheckBoxColumn(accessor='pk')
    first_name = tables.LinkColumn(verbose_name="First Name", text=lambda t: t.first_name, args=[A('pk')])
    last_name = tables.Column(verbose_name="Last Name")

    class Meta:
        model = Contact
        fields = ('select','first_name','last_name','group')
        
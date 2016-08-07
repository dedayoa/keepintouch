'''
Created on Aug 3, 2016

@author: Dayo
'''

import os

import django_tables2 as tables
from django_tables2.utils import A
from django.utils.safestring import mark_safe
from django.utils.html import format_html

from .models import CustomData


class CustomDataStoreTable(tables.Table):
    
    namespace = tables.LinkColumn(verbose_name="Namespace")
    system_id_field = tables.Column(verbose_name="Identity Field")
    identity_column_name = tables.Column(verbose_name="ID Key")
    created = tables.Column(verbose_name="Created")
        
    def render_namespace(self, record):        
        return format_html('<code><a href="{}" class="namespace_link">{}</a></code>',record.get_absolute_url(), record.namespace)
    
    class Meta:
        model = CustomData
        fields = ('namespace','system_id_field','identity_column_name','created')
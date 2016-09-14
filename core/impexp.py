'''
Created on Jul 22, 2016

@author: Dayo
'''
from import_export import resources, fields
from .models import Contact
from core.models import KITUser
from import_export.widgets import ForeignKeyWidget

import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException


class ContactResource(resources.ModelResource):
    #first_name = fields.Field(column_name='firstname')
    #last_name = fields.Field(column_name='lastname')
    #kit_user = fields.Field(widget=ForeignKeyWidget(KITUser,'id'))
    
    #def __init__(self, *args, **kwargs):
    #    self.kuid = kwargs.pop('kuserid')
    #    super(ContactResource, self).__init__(*args, **kwargs)
    #    self.kit_user = fields.Field(default=self.kuid, widget=ForeignKeyWidget(KITUser,'id'))
    
    class Meta:
        model = Contact
        skip_unchanged = True
        report_skipped = True
        import_id_fields = ('email','phone','kit_user')
        exclude = ('slug','last_modified', 'created','active')
    
    def for_delete(self, row, instance):
        
        if not (self.fields['phone'].clean(row) or self.fields['email'].clean(row)):
            return True
        if not self.fields['first_name'].clean(row):
            return True
        try:
            phonenumbers.parse(self.fields['phone'].clean(row), 'NG')
        except NumberParseException:
            return True
        
    
        
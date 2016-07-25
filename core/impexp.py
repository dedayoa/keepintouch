'''
Created on Jul 22, 2016

@author: Dayo
'''
from import_export import resources, fields
from .models import Contact
from core.models import KITUser
from import_export.widgets import ForeignKeyWidget


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
        report_skipped = False
        import_id_fields = ('email','phone')
        exclude = ('slug','last_modified', 'created','active')
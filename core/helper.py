'''
Created on May 27, 2016

@author: Dayo
'''

import tablib
import uuid
from crispy_forms.helper import FormHelper

from django.shortcuts import get_object_or_404
from django.utils.text import slugify 
from django.core.files.base import ContentFile

from django_downloadview import VirtualDownloadView

from .models import UploadedContact


class EventFormSetHelper(FormHelper):
    
    def __init__(self, *args, **kwargs):
        super(EventFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        

from django.core.mail import send_mail

class TestSMTPSetting():
    pass



class UploadedContactsDownloadView(VirtualDownloadView):
    def get_file(self, **kwargs):
        """Return wrapper on ``six.StringIO`` object."""
        fid = self.kwargs.get('id')
        up_contact = get_object_or_404(UploadedContact, pk=fid)
        
        ds = tablib.Dataset()
        ds.dict = up_contact.file_json
        file_name = '{}_{}.xls'.format(slugify(up_contact.name),str(uuid.uuid4()))
        return ContentFile(ds.xls, name=file_name)
        '''
        if up_contact.file_extension == 'csv':        
            ds = tablib.Dataset()
            ds.dict = up_contact.file_json
            file_name = '{}_{}.csv'.format(slugify(up_contact.name),str(uuid.uuid4()))
            return ContentFile(ds.csv, name=file_name)
            
        elif up_contact.file_extension == 'xls':
            ds = tablib.Dataset()
            ds.dict = up_contact.file_json
            file_name = '{}_{}.xls'.format(slugify(up_contact.name),str(uuid.uuid4()))
            return ContentFile(ds.xls, name=file_name)'''
        
        #file_obj = StringIO(u"Hello world!\n")
        #return VirtualFile(file_obj, name='hello-world.txt')

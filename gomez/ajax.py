'''
Created on Jul 28, 2016

@author: Dayo
'''

import tablib
import uuid
import os
import base64
from cryptography.fernet import Fernet

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile, File
from django.utils.text import slugify

from .forms import IssueFeedbackForm, CustomDataIngestForm
from .models import CustomData
#from munch import munchify



def us_slugify(value, seperator='-'):
    return slugify(value).replace('-', seperator)

def clean_header(header):
    d_hdrs = []
    x = 1
    for item in header:
        if item in d_hdrs:
            item = str(item)+"_"+x
        d_hdrs.append(us_slugify(item, '_'))
        x+=1
    return d_hdrs

@ajax
@login_required
def submit_issue_fb(request):
    
    if request.method == "POST":
        
        form = IssueFeedbackForm(request.POST, request.FILES)
        if not form.is_valid():
            return {'errors':form.errors.as_json(escape_html=True)}
        else:
            obj = form.save(commit=False)
            obj.submitter = request.user.kituser
            obj.save()
            return {'result':'Feedback Received.<br />Thank You'}
        
        
@ajax
@login_required        
def upload_custom_data(request):
    

    
    if request.method == "POST":
        
        form = CustomDataIngestForm(request.POST, request.FILES)
        
        if not form.is_valid():
            return {'errors': form.errors.as_json()}
        else:
            result_dict = {}
            
            upinfile = request.FILES.get('file')
            uqf_ptr = request.POST.get('unique_field')
            
            idata_headers = tablib.Dataset().load(upinfile.read()).headers
            #idata_headers[:] = [us_slugify(s, '_') for s in idata_headers]
            
            result_dict['idata_headers'] = clean_header(idata_headers)
            
            upinfile.seek(0)
            
            fext = os.path.splitext(str(upinfile))[1]
            file_path = os.path.join(settings.MEDIA_ROOT, 'tmp/'+str(uuid.uuid4())+fext)
            upfile_path = default_storage.save(file_path, ContentFile(upinfile.read()))
            
            aix = bytes(settings.SECRET_KEY[:32],'utf-8')
            f = Fernet(base64.urlsafe_b64encode(aix))
            token = f.encrypt(bytes(upfile_path,'utf-8'))
            
            result_dict['token'] = token
            result_dict['unqf_idfr'] = uqf_ptr
            
            return {"result" : result_dict}



@ajax
@login_required
def process_1_custom_data(request):
    
    if request.method == "POST":
        enc_file_loc = request.POST.get("token")
        id_fld_ptr = request.POST.get("identity_fld_ptr")
        unqf_idfr = request.POST.get("unqf_idfr")
        
        aix = bytes(settings.SECRET_KEY[:32],'utf-8')
        f = Fernet(base64.urlsafe_b64encode(aix))
        file_loc = (f.decrypt(bytes(enc_file_loc,'utf-8'))).decode('utf-8')
        fext = os.path.splitext(str(file_loc))[1]
        '''
        'owner': {
            'name': 'Bob',
            'other_pets': 'Fishy'
        },
        'owner2': {
            'name': 'Tim',
            'other_pets': 'Crabby'
        },
        '''
        def process_data(ds_in_dict, identity_column_name):
            #converts a standard ds.dict into more accessible json
            new_dict = {}
            new_inner_dict = {}
            for row in ds_in_dict:
                for k,v in row.items():
                    if k==identity_column_name:
                        new_dict[v] = new_inner_dict
                    else:
                        new_inner_dict[k] = v
                new_inner_dict = {}
            return new_dict
        
        
        def process_dataset(ds):
            
            ds.headers[:] = clean_header(ds.headers)
            
            if unqf_idfr == "coid":
                t = CustomData.objects.create(
                    identity_column_name =  ds.headers[int(id_fld_ptr)],
                    system_id_field = unqf_idfr,
                    headers = ds.headers,
                    data = process_data(ds.dict, ds.headers[int(id_fld_ptr)]),
                    data_table = ds.dict,
                    created_by = request.user.kituser
                )
                return t
            elif unqf_idfr == "doid":
                t = CustomData.objects.create(
                    identity_column_name =  ds.headers[int(id_fld_ptr)],
                    system_id_field = unqf_idfr,
                    headers = ds.headers,
                    data = process_data(ds.dict, ds.headers[int(id_fld_ptr)]),
                    data_table = ds.dict,
                    created_by = request.user.kituser
                )
                return t
            
        
        
        if (fext[1:]).lower() == 'csv':
            with open(file_loc, 'r') as f:         
                dataset = tablib.Dataset().load(f.read(), format="csv")
                result = process_dataset(dataset)
            return {"result":result}
        else:
            with open(file_loc,'rb') as f:
                dataset = tablib.Dataset().load(f.read(), format="xls")
                result = process_dataset(dataset)
            return {"result":result}
            

@ajax
@login_required        
def get_custom_data_ajax(request, pk):
    
    if request.method == "GET":
        result_dict = {}
        custd = CustomData.objects.get(pk=pk)
        result_dict["data_table"] = custd.data_table
        result_dict["headers"] = custd.headers
        result_dict["identity_field"] = custd.system_id_field
        result_dict["id_key"] = custd.identity_column_name
        
        return {"result":result_dict}
        
@ajax
@login_required          
def delete_custom_data_ajax(request, pk):
    
    if request.method == "POST":
        result = CustomData.objects.get(pk=pk, created_by=request.user.kituser).delete()
        return {"result":result}
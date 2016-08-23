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

#from munch import munchify


        
        

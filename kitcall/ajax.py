'''
Created on Nov 8, 2016

@author: Dayo
'''

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax


@ajax
@login_required
def call_number(request, pn):
    pass
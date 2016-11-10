'''
Created on Nov 8, 2016

@author: Dayo
'''

from django.contrib.auth.decorators import login_required
from django_ajax.decorators import ajax
from .helper import CallHelper, return_all_level_err

@ajax
@login_required
def call_number(request, pn):
    
    if request.method == "GET":
        k = CallHelper(pn, request.user.kituser)
        resp = k.make_my_call()
        if resp[0] == 0:            
            return {'result':resp[1]}
        else:
            return {'errors':return_all_level_err(resp[1])}
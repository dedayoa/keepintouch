'''
Created on Jun 15, 2016

@author: Dayo
'''
from django import template

register = template.Library()

import json


@register.filter()
def tojson(value):
    """returns a JSON representation of PGSQL's JSONB"""
    return json.dumps(value)
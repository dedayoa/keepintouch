'''
Created on Aug 3, 2016

@author: Dayo
'''
from django import template

register = template.Library()

from ..models import Contact

'''
@register.filter()
def cdata(value, args):
    g = Contact.objects.get(pk = value)
    h = g.customdata_set.get(pk = args)
    return h
'''
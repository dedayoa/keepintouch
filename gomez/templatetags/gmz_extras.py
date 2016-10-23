'''
Created on Oct 9, 2016

@author: Dayo
'''

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter()
@stringfilter
def splittolist(value):
    return value.splitlines()
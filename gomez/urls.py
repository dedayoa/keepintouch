'''
Created on Jul 13, 2016

@author: Dayo
'''

from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^settings/', include([
        url(r'^my/system/$', SystemSettingsUpdateView.as_view(), name='system-settings'),
        url(r'^account/expired/$', SubscriptionExpired.as_view(), name='account-expired'),
                
                
    ])),
               
    url(r'^order/', include([
            url(r'^start/$', OrderStart.as_view(), name='order-start'),
            url(r'^(?P<order_id>[A-Z0-9]{10})/$', OrderCart.as_view(), name='order-cart'),
            url(r'^(?P<order_id>[A-Z0-9]{10})/update/$', UpdateCart.as_view(), name='order-update'),
            url(r'^(?P<order_id>[A-Z0-9]{10})/item/(?P<id>\d+)/delete/$', DeleteCartItem.as_view(), name='order-delete-item'),
            url(r'^checkout/$', OrderCheckout.as_view(), name='order-checkout'),
            #url(r'^paynow/$', get_qpc_stats, name='order-checkout'),
    ])),
]
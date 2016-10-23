from django.views.generic import UpdateView, View

from .models import KITSystem, Product, KITBilling, Order, OrderLine
from .forms import SystemSettingsForm

from django.shortcuts import render, get_object_or_404
from ipware.ip import get_real_ip

import prices
import logging
from django.http.response import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

logger = logging.getLogger(__name__)
    
class SystemSettingsUpdateView(UpdateView):
    
    model = KITSystem
    form_class = SystemSettingsForm
    template_name = 'gomez/system_settings.html'
    
    def get_object(self, queryset=None):
        return self.request.user.kituser.kitsystem
    
    def get_context_data(self, **kwargs):
        params = super(SystemSettingsUpdateView, self).get_context_data(**kwargs)
        params["syssetid"] = self.object.pk
        return params
    
    def get_queryset(self):
        # user should not be able to view the settings of other users
        qs = super(SystemSettingsUpdateView, self).get_queryset()
        return qs.filter(kit_admin=self.request.user.kituser)


class SubscriptionExpired(View):
    
    template = 'gomez/order/subscription_expired_landing_page.html'
    params = {}
    
    def get(self, request):
        subsc_plans = Product.objects.filter(meta__type='subscription', meta__sub_type='plan', active=True).order_by('price').values()
        user_plan = KITBilling.objects.get(kit_admin = request.user.kituser).service_plan
        # if order exists, then renew...and provide other options in case user wants to upgrade or downgrade
        # else provide all the options
        self.params["subscription_products"] = subsc_plans
        
        return render(request, self.template, self.params)

class OrderStart(View):
    
    
    params = {}
    
    def get(self, request):
        product_id = request.GET.get('product_id')
        if request.GET.get('action') == 'renew':
            # return the cart with the ministore
            # get the existing subscription order
            try:
                current_order = request.user.kituser.order
                
            except AttributeError:
                # no order exists
                pass #log this
            
        elif request.GET.get('action') == 'resub':
            # get product to subscribe for
            subsc_product = Product.objects.get(pk=product_id)

            # create order
            corder = Order.objects.create(
                    ip_address = get_real_ip(request),
                    customer = request.user.kituser,
                    billing_address = request.user.kituser.address,
                                          )            
            # create orderline
            porderl = OrderLine.objects.create(
                    product = subsc_product,
                    unit_price_net = subsc_product.price.net,
                    unit_price_gross = subsc_product.price.gross,
                    billing_cycle = OrderLine.ANNUALLY,
                    quantity = 1,
                    order = corder
                    )
            corder.total = porderl.product.price
            corder.save()
            return HttpResponseRedirect(reverse('gomez:order-cart', kwargs={'order_id':corder.order_number}))  


class OrderCart(View):
    
    params = {}
    template = 'gomez/order/order_start.html'
    
    def get(self, request, order_id):
        
        corder = get_object_or_404(Order, order_number=order_id)
        
        self.params['mini_store'] = Product.objects.exclude(meta__type="subscription").exclude(active=False).\
                                    values('name','description','meta','price')
        
        self.params['corder'] = corder
        self.params['title'] = "Order {}".format(corder.order_number)
    
        self.params['corder_p_items'] = corder.get_items().values()
        
        return render(request, self.template, self.params)
    
class UpdateCart(View):

    
    def post(self, request, order_id):
        print(request.POST)
        for itemline in request.POST:
            if itemline.isnumeric():
                OrderLine.objects.get(pk=itemline).change_quantity(request.POST.get(itemline))
        # update order summary
        order = Order.objects.get(order_number=order_id)
        total = sum([item.get_line_total() for item in order], prices.Price(0, currency=settings.DEFAULT_CURRENCY))
        order.total = total
        order.save()
        
        return HttpResponseRedirect(reverse('gomez:order-cart', args=[order_id]))



class DeleteCartItem(View):
    
    pass

class OrderCheckout(View):
    pass
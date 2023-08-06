from decimal import Decimal
from django.conf import settings
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.http import urlencode
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from livesettings import config_get_group, config_value
from payment.config import gateway_live
from payment.utils import get_processor_by_key
from payment.views import payship
from satchmo_store.shop.models import Cart
from satchmo_store.shop.models import Order, OrderPayment
from satchmo_store.contact.models import Contact
from satchmo_utils.dynamic import lookup_url, lookup_template
from satchmo_utils.views import bad_or_missing
from sys import exc_info
from traceback import format_exception
import logging
import urllib2
from django.views.decorators.csrf import csrf_exempt
from django_payworld.utils import calculate_hash


log = logging.getLogger()

def pay_ship_info(request):
    return payship.base_pay_ship_info(request,
        config_get_group('PAYMENT_SATCHMO_PAYMENT_PAYWORLD'), payship.simple_pay_ship_process_form,
        'shop/checkout/payworld/pay_ship.html')
pay_ship_info = never_cache(pay_ship_info)

def confirm_info(request):
    payment_module = config_get_group('PAYMENT_SATCHMO_PAYMENT_PAYWORLD')

    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0 and not order.is_partially_paid:
        template = lookup_template(payment_module, 'shop/checkout/empty_cart.html')
        return render_to_response(template,
                                  context_instance=RequestContext(request))

    # Check if the order is still valid
    if not order.validate(request):
        context = RequestContext(request,
                                 {'message': _('Your order is no longer valid.')})
        return render_to_response('shop/404.html', context_instance=context)

    template = lookup_template(payment_module, 'shop/checkout/payworld/confirm.html')
    if payment_module.LIVE.value:
        log.debug("live order on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.BUSINESS.value
    else:
        url = payment_module.POST_TEST_URL.value
        account = payment_module.BUSINESS_TEST.value

    try:
        cart = Cart.objects.from_request(request)
    except:
        cart = None
    try:
        contact = Contact.objects.from_request(request)
    except:
        contact = None
    if cart and contact:
        cart.customer = contact
        log.debug(':::Updating Cart %s for %s' % (cart, contact))
        cart.save()

    order_total=str(round(float(order.total), 2))

    processor_module = payment_module.MODULE.load_module('processor')
    processor = processor_module.PaymentProcessor(payment_module)
    processor.create_pending_payment(order=order)

    ctx = RequestContext(request, {'order': order,
     'post_url': url,
     'order_id': order.id,
     'order_total': order_total,
     'order_details': order.notes,
     'default_view_tax': False,
     'business': account,
     'store_id': payment_module.STORE_ID.value,
     'PAYMENT_LIVE' : gateway_live(payment_module)
    })

    return render_to_response(template, context_instance=ctx)
confirm_info = never_cache(confirm_info)

@csrf_exempt
def ipn(request):
    """PayWorld IPN (Instant Payment Notification)
    Cornfirms that payment has been completed and marks invoice as paid.
    Adapted from IPN cgi script provided at http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/456361
    Rewrited for payworld
    """
    payment_module = config_get_group('PAYMENT_SATCHMO_PAYMENT_PAYWORLD')
    if payment_module.LIVE.value:
        log.debug("Live IPN on %s", payment_module.KEY.value)
        account = payment_module.BUSINESS.value
    else:
        log.debug("Test IPN on %s", payment_module.KEY.value)
        account = payment_module.BUSINESS_TEST.value

    try:
        data = request.POST
        log.debug("PayWorld IPN data: " + repr(data))
        if not confirm_ipn_data(data, payment_module.SECRET_CODE.value):
            log.info("Ignoring IPN data for invalid payment.")
            return HttpResponse()

        invoice = data['order_id']
        txn_id = data['transaction_id']
        gross = data['order_total']

        if not OrderPayment.objects.filter(transaction_id=txn_id).count():
            # If the payment hasn't already been processed:
            order = Order.objects.get(pk=invoice)
            if float(gross) != float(order.total):
                log.warn("Gross and total aren't equal: %s and %s. Report it to PayWorld support." % (gross, order.total))
                return HttpResponse()

            order.add_status(status='New', notes=_("Paid through PayWorld."))
            processor = get_processor_by_key('PAYMENT_SATCHMO_PAYMENT_PAYWORLD')
            payment = processor.record_payment(order=order, amount=gross, transaction_id=txn_id)

            # Added to track total sold for each product
            for item in order.orderitem_set.all():
                product = item.product
                product.total_sold += item.quantity
                product.items_in_stock -= item.quantity
                product.save()

            # Clean up cart now
            for cart in Cart.objects.filter(customer=order.contact):
                cart.empty()



    except:
        log.exception(''.join(format_exception(*exc_info())))

    return HttpResponse()

def confirm_ipn_data(data, secret):
    """
    Verify transaction sign
    """
    # data is the form data that was submitted to the IPN URL.

    hash_summ = calculate_hash(data, secret)
    if hash_summ == data['hash']:
        log.info("PayWorld IPN data verification was successful.")
    else:
        log.info("PayWorld IPN data verification failed.")
        return False

    return True

@csrf_exempt
def success(request):
    """
    The order has been succesfully processed.
    We clear out the cart but let the payment processing get called by IPN
    """
    try:
        data = request.POST
        invoice = data['order_id']
        transaction = data['transaction_id']
        result_message = data['result_message']
        order = Order.objects.get(pk=invoice)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))

#    del request.session['orderID']
    context = RequestContext(request,
        {
            'order': order,
            'transaction': transaction,
            'result_message': result_message
        })
    return render_to_response('shop/checkout/payworld/success.html', context)

success = never_cache(success)

@csrf_exempt
def failure(request):
    """
    The order processing has been failed
    """
    try:
        data = request.POST
        invoice = data['order_id']
        result_message = data['result_message']
        order = Order.objects.get(pk=invoice)

    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))

    context = RequestContext(request, 
        {
            'order': order,
            'result_message': result_message
        })
    return render_to_response('shop/checkout/payworld/failure.html', context)

failure = never_cache(failure)


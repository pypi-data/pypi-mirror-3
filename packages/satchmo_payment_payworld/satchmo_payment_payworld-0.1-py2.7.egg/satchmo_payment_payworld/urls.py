from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
     (r'^$', 'satchmo_payment_payworld.views.pay_ship_info', {'SSL': ssl}, 'SATCHMO_PAYMENT_PAYWORLD_satchmo_checkout-step2'),
     (r'^confirm/$', 'satchmo_payment_payworld.views.confirm_info', {'SSL': ssl}, 'SATCHMO_PAYMENT_PAYWORLD_satchmo_checkout-step3'),
     (r'^success/$', 'satchmo_payment_payworld.views.success', {'SSL': ssl}, 'SATCHMO_PAYMENT_PAYWORLD_satchmo_checkout-success'),
     (r'^failure/$', 'satchmo_payment_payworld.views.failure', {'SSL': ssl}, 'SATCHMO_PAYMENT_PAYWORLD_satchmo_checkout-failure'),
     (r'^ipn/$', 'satchmo_payment_payworld.views.ipn', {'SSL': ssl}, 'SATCHMO_PAYMENT_PAYWORLD_satchmo_checkout-ipn'),
     (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order',
         {'SSL' : ssl, 'key' : 'PAYWORLD'}, 'SATCHMO_PAYMENT_PAYWORLD_satchmo_checkout_free-confirm')
)

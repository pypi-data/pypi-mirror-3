from livesettings import *
from django.utils.translation import ugettext_lazy as _

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_SATCHMO_PAYMENT_PAYWORLD',
    _('Payworld Payment Module Settings'),
    ordering = 101)

config_register_list(

StringValue(PAYMENT_GROUP,
    'POST_URL',
    description=_('Post URL'),
    help_text=_('The Payworld URL for real transaction posting.'),
    default="https://pay-world.ru/paymentsystem/enter/"),

StringValue(PAYMENT_GROUP,
    'POST_TEST_URL',
    description=_('Post URL'),
    help_text=_('The Payworld URL for test transaction posting.'),
    default="https://pay-world.ru/paymentsystem/enter-test/"),

StringValue(PAYMENT_GROUP,
    'BUSINESS',
    description=_('Payworld account email'),
    help_text=_('The email address for your payworld account'),
    default=""),

StringValue(PAYMENT_GROUP,
    'BUSINESS_TEST',
    description=_('Payworld test account email'),
    help_text=_('The email address for testing your payworld account'),
    default=""),

StringValue(PAYMENT_GROUP,
    'STORE_ID',
    description=_('Store id'),
    help_text=_('The store id from your payworld account settings'),
    default=""),

StringValue(PAYMENT_GROUP,
    'SECRET_CODE',
    description=_('Secret code'),
    help_text=_('Store secret code from your payworld account settings'),
    default=""),

BooleanValue(PAYMENT_GROUP,
    'LIVE',
    description=_("Accept real payments"),
    help_text=_("False if you want to be in test mode"),
    default=False),

ModuleValue(PAYMENT_GROUP,
    'MODULE',
    description=_('Implementation module'),
    hidden=True,
    default = 'satchmo_payment_payworld'),

StringValue(PAYMENT_GROUP,
    'KEY',
    description=_("Module key"),
    hidden=True,
    default = 'SATCHMO_PAYMENT_PAYWORLD'),

StringValue(PAYMENT_GROUP,
    'LABEL',
    description=_('English name for this group on the checkout screens'),
    default = 'PayWorld',
    dummy = _('PayWorld'), # Force this to appear on po-files
    help_text = _('This will be passed to the translation utility')),

StringValue(PAYMENT_GROUP,
    'URL_BASE',
    description=_('The url base used for constructing urlpatterns which will use this module'),
    default = '^payworld/'),

BooleanValue(PAYMENT_GROUP,
    'EXTRA_LOGGING',
    description=_("Verbose logs"),
    help_text=_("Add extensive logs during post."),
    default=False)
)

PAYMENT_GROUP['TEMPLATE_OVERRIDES'] = {
    'shop/checkout/confirm.html' : 'shop/checkout/payworld/confirm.html',
}

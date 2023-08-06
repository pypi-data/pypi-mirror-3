from payment.modules.base import HeadlessPaymentProcessor

class PaymentProcessor(HeadlessPaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('satchmo_payment_payworld', settings)

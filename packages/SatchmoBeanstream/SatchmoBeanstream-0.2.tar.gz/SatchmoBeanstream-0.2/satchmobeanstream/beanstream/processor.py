"""
Payment processor for Beanstream backend
"""

ugettext_lazy = lambda x: x
_ = ugettext_lazy

from django.conf import settings as django_settings
from payment.modules.base import BasePaymentProcessor, ProcessorResult
from pybeanstream.classes import BeanClient, BaseBeanClientException, \
    BeanUserError, BeanSystemError
from decimal import Decimal
from payment.forms import CreditPayShipForm

# To use an alternate form, you need to monkeypatch.
FORM = CreditPayShipForm


class PaymentProcessor(BasePaymentProcessor):

    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('beanstream', settings)
        self._initialize_payment_gateway()

    def _initialize_payment_gateway(self):
       
        self.client = BeanClient(
            django_settings.BEANSTREAM_CREDENTIALS['username'],
            django_settings.BEANSTREAM_CREDENTIALS['password'],
            django_settings.BEANSTREAM_CREDENTIALS['merchant_id'],
            )

    def authorize_payment(self, order=None, testing=False, amount=None ):
        """
        """
        raise NotImplementedError('This is not implemented')

    def can_authorize(self):
        """
        Authorization not implemented, can only purchase at the moment.
        """
        return False

    def capture_payment(self, testing=False, amount=None, order=None):
        """
        This is used to automatically process payment.
        TODO: If a "partial amount" is authorized, void pre-auth request.
        """
        if order == None:
            order = self.order

        if amount is None:
            amount = order.balance

        cc = order.credit_card

        if order.paid_in_full:
            self.log_extra('%s is paid in full, no payment attempted.', order)
            payment = self.record_failure(
                amount=order.balance,
                transaction_id=str(order.id),
                )
            return ProcessorResult(self.key, False, _("No charge needed, paid in full."), payment)

        if cc:
            self.log_extra('Authorizing payment of %s for %s', amount, order)

            if not cc.decryptedCC:
                error = _('Credit Card Number not Available, perhaps you have waited too long to checkout?')
                payment = self.record_failure(
                    amount=order.balance,
                    transaction_id=str(order.id),
                    )
                return ProcessorResult(self.key, False, error, payment)

            else:
                try:
                    args = (
                        ' '.join((order.contact.first_name,
                                  order.contact.last_name)),
                        str(cc.decryptedCC),
                        str(cc.ccv),
                        "%02d" % Decimal(cc.expire_month),
                        "%02d" % Decimal(str(cc.expire_year)[2:]),
                        str(order.balance),
                        str(order.id),
                        str(order.contact.email),
                        order.bill_addressee,
                        str(order.contact.primary_phone),
                        order.bill_street1,
                        order.bill_city,
                        order.bill_state,
                        order.bill_postal_code,
                        order.bill_country,
                        )

                    kwargs = dict(cust_address_line2=order.bill_street2)

                    response = self.client.purchase_request(*args, **kwargs)

                    if response.trnApproved:
                        payment = self.record_payment(
                            amount=amount,
                            reason_code="0",
                            transaction_id=response.trnId,
                            )
                        return ProcessorResult(self.key, True, _('Success'), payment)
                    else:
                        payment = self.record_failure(
                            amount=order.balance,
                            transaction_id=str(order.id),
                            reason_code=response.messageId,
                            details=response.messageText,
                            )
                        return ProcessorResult(self.key, False,
                                               _('Payment declined'), payment)
                except BeanUserError, e:
                    payment = self.record_failure(
                        amount=order.balance,
                        transaction_id=str(order.id),
                        reason_code='Bad format',
                        details=str(e)
                        )
                    return ProcessorResult(self.key, False,
                                           _('Request badly formatted, please contact support.'), payment)

                except BeanSystemError, e:
                    payment = self.record_failure(
                        amount=order.balance,
                        transaction_id=str(order.id),
                        reason_code='SystemError',
                        details=str(e)
                        )
                    return ProcessorResult(self.key, False,
                                           _('Error with payment processor'), payment)
        else:
            error = 'CC Number unavailable'
            payment = self.record_failure(
                amount=order.balance,
                transaction_id=str(order.id),
                details=error)
            return ProcessorResult(self.key, False, error, payment)


    def capture_authorized_payment(self, authorization, amount=None):
        """
        """
        raise NotImplementedError('This is not implemented')

    def release_authorized_payment(self, order=None, auth=None, testing=False ):
        """Release a previously authorized payment."""
        raise NotImplementedError('This is not implemented')

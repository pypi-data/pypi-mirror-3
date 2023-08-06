from zope.interface import implements
from Products.Five.browser import BrowserView
from pcommerce.core.interfaces import IPaymentView
from pcommerce.payment.ogone.data import OgonePaymentData


class OgonePayment(BrowserView):
    implements(IPaymentView)

    def __init__(self, payment, request):
        self.payment = payment
        self.context = payment.context
        self.request = request

    def validate(self):
        """
        validate the form.
        No parameters to be checked, so return True
        """
        return True

    def process(self):
        return OgonePaymentData()

    def renders(self):
        return False

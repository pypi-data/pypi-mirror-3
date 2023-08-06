from zope.interface import implements
from Products.Five.browser import BrowserView
from pcommerce.core.interfaces import IPaymentProcessor
from pcommerce.core.interfaces import IPaymentView
from ..status_codes import get_status_description


class ProcessOgone(BrowserView):
    """process Ogone payments
    """

    implements(IPaymentView)

    def __init__(self, context, request):
        super(ProcessOgone, self).__init__(context, request)
        self.context = context
        self.request = request
        self.form = self.context.REQUEST.form

    def status_description(self):
        """ return the ogone status description """
        return get_status_description(int(self.form['STATUS']))

    def processOrder(self):
        """ do the actual processing in the plugin """
        processor = IPaymentProcessor(self.context)
        orderId = self.form.get('orderID', '')
        return processor.processOrder(orderId, 'pcommerce.payment.ogone')

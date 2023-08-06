import urllib
import math

from zope.interface import implements, Interface
from zope.component import adapts
from zope.component import getUtility
from zope.i18n.interfaces import IUserPreferredLanguages
from Products.CMFCore.utils import getToolByName
from plone.registry.interfaces import IRegistry

from pcommerce.core.interfaces import IPaymentMethod
from pcommerce.core.currency import CurrencyAware
from pcommerce.core import PCommerceMessageFactory as _
from pcommerce.payment.ogone.interfaces import IOgonePayment, IOgoneSettings

from security import OgoneSignature
from status_codes import get_status_category, SUCCESS_STATUS


class OgonePayment(object):
    implements(IPaymentMethod, IOgonePayment)
    adapts(Interface)

    title = _(u'Ogone')
    description = _('Payment using Ogone')
    icon = u'++resource++pcommerce_payment_ogone_icon.jpg'
    logo = u'++resource++pcommerce_payment_ogone_logo.jpg'

    def __init__(self, context):
        self.context = context
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IOgoneSettings)

    def __getattr__(self, name):
        if hasattr(self.settings, name):
            return getattr(self.settings, name)
        raise AttributeError

    def getLanguage(self):
        """
        Ogone requires en_EN or en_US language id
        We are parsing the request to get the right
        Note: took this code from getpaid.ogone (thanks)
        """
        languages = IUserPreferredLanguages(self.context.REQUEST)
        langs = languages.getPreferredLanguages()
        if langs:
            language = langs[0]
        else:
            plone_props = getToolByName(self.context, 'portal_properties')
            language = plone_props.site_properties.default_language
        language = language.split('-')
        if len(language) == 1:
            language.append(language[0])
        language = language[:2]
        return "_".join(language)

    def mailInfo(self, order, lang=None, customer=False):
        return _('ogone_mailinfo', default=u"Payment processed over Ogone")

    def verifyPayment(self, order):
        """
        check whether the returned values from Ogone are valid
        we check the returned SHASign is the same as our calculated one
        to prevent fraude
        """
        params = self.context.REQUEST.form

        # sanity check..
        if int(params['orderID']) != order.orderid:
            return False

        if get_status_category(int(params['STATUS'])) != SUCCESS_STATUS:
            return False

        signer = OgoneSignature(params, 'sha512', self.sha_out_password)
        return params['SHASIGN'] == signer.signature()

    def action(self, order):
        """"""
        url = '%s/%%s' % (self.context.absolute_url())
        language = self.getLanguage()
        price = CurrencyAware(order.totalincl)
        params = {
                'PSPID': self.pspid,
                'ORDERID': order.orderid,
                'CURRENCY': order.currency.upper() or self.currency or 'EUR',
                'AMOUNT': int(math.ceil(price.getRoundedValue(0.01) * 100)),
                'LANGUAGE': language,
                'ACCEPTURL': url % 'processOgone',
                'DECLINEURL': url % 'payment.failed',
                'EXCEPTIONURL': url % 'payment.failed',
                'CANCELURL': url % 'payment.cancel',
                # TODO: add custom colors
                }
        signer = OgoneSignature(params, 'sha512', self.sha_in_password)
        params['SHASign'] = signer.signature()
        arguments = urllib.urlencode(params)
        action_url = "%s?%s" % (self.server_url, arguments)
        return action_url

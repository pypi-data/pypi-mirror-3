from zope.interface import Interface
from zope import schema
from pcommerce.payment.ogone import MessageFactory as _


class IOgonePayment(Interface):
    """ Ogone payment plugin
    """


class IOgoneSettings(Interface):

    server_url = schema.TextLine(title=_(u"Ogone Server URL"),
            description=_(u"Test or production URL"),
            required=True,
            default=u'https://secure.ogone.com/ncol/test/orderstandard.asp',)

    pspid = schema.TextLine(title=_(u"pspid"),
            description=_(u"the PSP ID"),
            required=True,
            default=u'')

    currency = schema.TextLine(title=_(u"Currency"),
            description=_(u"Currency as known in Ogone (e.g. USD, EUR)"),
            required=True,
            default=u'EUR')

    # should be schema.Password field, but 2 passwords on one form
    # don't work for some reason.. could be a firefox being smart issue
    sha_in_password = schema.TextLine(title=_(u"SHA In Passphrase"),
            description=_(u"SHA IN password as configured in Ogone"),
            required=True,
            default=u'')

    # should be schema.Password field, but 2 passwords on one form
    # don't work for some reason..
    sha_out_password = schema.TextLine(title=_(u"SHA Out Passphrase"),
            description=_(u"SHA OUT password as configurd in Ogone"),
            required=True,
            default=u'')

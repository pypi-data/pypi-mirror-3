from zope.interface import Interface
from collective.flattr import flattrMessageFactory as _
from collective.flattr.vocab import buttons_vocab
from zope import schema

class ICollectiveFlattr(Interface):
    """ describe some properties used for the flattr buttons """

    base_url = schema.TextLine(title=_(u'Base Url'),
        description=_(u'Url registered at flattr. If you leave this field empty, it will be calculated!'),
        required=True)

    button_type = schema.Choice(title=_(u'Type of flattr button'),
        default=u'Compact Counter',
        description=_(u'Select the type of flattr button to be shown'),
        required=True,
        vocabulary=buttons_vocab)

    customer_key = schema.TextLine(title=_(u'Customer key'),
        description=_(u'Also called application key. You must register your web app at flattr to get the key'),
        default=u'',
        required=True)

    customer_secret = schema.TextLine(title=_(u'Customer secret'),
        description=_(u'Also called application secret. You must register your web app at flattr to get the key'),
        default=u'',
        required=True)

    access_token = schema.TextLine(title=_(u'Access token'),
        description=_(u'Your access token will be set automatically after allowing your web app on flattr'),
        default=u'',
        required=False)

    access_token_type = schema.TextLine(title=_(u'Access token type'),
        description=_(u'Your access secret will be set automatically after allowing your web app on flattr'),
        default=u'',
        required=False)

    access_token_url = schema.URI(title=_(u'Access token URL'),
        description=_(u'URL to flattrs api'),
        default='https://flattr.com/oauth/token',
        required=True)

    authorize_url = schema.URI(title=_(u'Authorize URL'),
        description=_(u'URL to flattrs api'),
        default='https://flattr.com/oauth/authorize',
        required=True)

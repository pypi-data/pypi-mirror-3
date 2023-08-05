import logging
from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface
from plone.app.form.widgets.wysiwygwidget import WYSIWYGWidget
from zope.interface import implements
from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.flattr.interfaces import ICollectiveFlattr

from plone.app.portlets.portlets import base
from plone.portlets.interfaces import IPortletDataProvider

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.flattr import flattrMessageFactory as _

from zope.i18nmessageid import MessageFactory
__ = MessageFactory("plone")

from collective.flattr.vocab import buttons_vocab


logger = logging.getLogger('collective.flattr.portlets.flattrportlet')


class IFlattrPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    button_type = schema.Choice(title=_(u'Type of flattr button'),
        default=u'Large Counter',
        description=_(u'Select the type of flattr button to be shown'),
        required=True,
        vocabulary=buttons_vocab)

    thing_url = schema.TextLine(title=_(u'Url for your thing'),
        description=_(u'Url for your thing, e.g. http://flattr.com/thing/408580/Chris-wirre-Gedankenwelt or just 408580/Chris-wirre-Gedankenwelt'),
        required=True)

    text = schema.Text(title=_(u'Text'),
        description=_(u'Write a few words... will be shown above the button'),
        required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFlattrPortlet)

    button_type = u'Large Counter'
    thing_url = u''
    text = u''

    def __init__(self, button_type=u'Large Counter', thing_url=u'', text=u''):
        self.button_type = button_type
        self.thing_url = thing_url
        self.text = text


    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return __(u"Flattr portlet")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('flattrportlet.pt')

    def update(self):
        """  """
        super(Renderer, self).update()

        thing_url = self.data.thing_url
        if thing_url:
            if not thing_url.startswith('http://'):
                thing_url = 'http://flattr.com/thing/%s' % thing_url

        self.thing_url = thing_url
        button_type = u'flattr;button:large'
        button_class = u'FlattrButton'
        button_style = u'display:none;'
        if self.data.button_type == u'Compact Counter':
            button_type = u'flattr;button:compact;'
        elif self.data.button_type == u'Static':
            button_type = u''

        self.button_type = button_type

        registry = getUtility(IRegistry)
        try:
            proxy = registry.forInterface(ICollectiveFlattr)
            base_url = proxy.base_url
        except KeyError:
            # This occurs if collective.flattr is not installed.
            base_url = ''
        if not base_url:
            base_url = self.request.SERVER_URL
        self.base_url = base_url

    def transformed(self, mt='text/x-html-safe'):
        """Use the safe_html transform to protect text output. This also
        ensures that resolve UID links are transformed into real links.
        """
        orig = self.data.text
        context = aq_inner(self.context)
        # if there is no text inserted, orig is propably None. That causes
        # a defect.
        if orig is None:
            orig = u''
        if not isinstance(orig, unicode):
            # Apply a potentially lossy transformation, and hope we stored
            # utf-8 text. There were bugs in earlier versions of this portlet
            # which stored text directly as sent by the browser, which could
            # be any encoding in the world.
            orig = unicode(orig, 'utf-8', 'ignore')
            logger.warn("Flattr portlet at %s has stored non-unicode text. "
                        "Assuming utf-8 encoding." % context.absolute_url())

        # Portal transforms needs encoded strings
        orig = orig.encode('utf-8')

        transformer = getToolByName(context, 'portal_transforms')
        data = transformer.convertTo(mt, orig,
                                     context=context, mimetype='text/html')
        result = data.getData()
        if result:
            return unicode(result, 'utf-8')
        return None


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFlattrPortlet)

    def create(self, data):
        return Assignment(**data)


# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFlattrPortlet)
    form_fields['text'].custom_widget = WYSIWYGWidget

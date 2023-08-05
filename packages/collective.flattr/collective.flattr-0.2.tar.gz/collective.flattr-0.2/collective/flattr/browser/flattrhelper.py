from zope.interface import Interface
from zope.interface import implements


class IFlattrHelper(Interface):
    """ Some little helpers """


class FlattrHelper(object):
    """ Some little helpers """

    implements(IFlattrHelper)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def getFlattrUrl(self):
        """ Returns flattrs api url with leaded http or https """
        if self.request.URL.startswith('https://'):
            return 'https://api.flattr.com'
        return 'http://api.flattr.com'

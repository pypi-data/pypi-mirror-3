from Products.Five import BrowserView
from rt.vuvuzela import vuvuzelaMessageFactory as _
from zope.interface import implements, Interface

class IVuvuzelaView(Interface):
    """
    Vuvuzela view interface
    """

    def play():
        """Peeeeeeeeeeee"""


class VuvuzelaView(BrowserView):
    """
    Vuvuzela browser view
    """
    implements(IVuvuzelaView)

    def play(self):
        """
        Play vuvuzela
        """
        return _(u'I play vuvuzela')

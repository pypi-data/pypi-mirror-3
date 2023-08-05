from zope.interface import Interface, Attribute
from zope import schema


class IMailable(Interface):
    """An object that can provide an email address."""

    def UID():
        """Unique identifier.
        """
        pass

    email = Attribute('email')


class IZestEmailHiderLayer(Interface):
    """Browser layer marker interface.

    plone.browserlayer adds this to the request when our package is
    installed in the Plone Site.
    """

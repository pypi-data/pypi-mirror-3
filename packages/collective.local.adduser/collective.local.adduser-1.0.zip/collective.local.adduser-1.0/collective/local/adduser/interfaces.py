from zope.interface import Interface
from zope import schema
from zope.component.interfaces import IObjectEvent


class IAddNewUser(Interface):
    """Include a add new user link to the sharing tab.
    """


class IUserLocallyAdded(IObjectEvent):
    """Event notified when a user is locally added to an object via
    the 'add new user' link and has a least one role.
    """

    userid = schema.TextLine(title=u"User id of the created user.")

    roles = schema.List(title=u"List of local roles given to userid on object.")

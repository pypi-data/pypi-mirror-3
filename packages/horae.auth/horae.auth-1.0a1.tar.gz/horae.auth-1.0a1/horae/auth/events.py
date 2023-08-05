from zope.component.interfaces import ObjectEvent
from zope.interface import implements

from horae.auth.interfaces import ISharingModifiedEvent


class SharingModifiedEvent(ObjectEvent):
    """ An objects sharing has been modified
    """
    implements(ISharingModifiedEvent)

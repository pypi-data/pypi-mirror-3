from Products.ATContentTypes.interface.interfaces import IATContentType
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.ATContentTypes.interface.folder import IATFolder

# This is a marker interface. By having PressRelease declare that it implements
# IPressRelease, we are asserting that it also supports IATNewsItem and 
# everything that interface declares

class IPressRelease(IATNewsItem):
    """Press release marker interface
    """

class IPressClip(IATNewsItem):
    """Press Clip marker interface
    """

class IPressContact(IATContentType):
    """Press Contact marker interface
    """

class IPressRoom(IATFolder):
    """Press Clip marker interface
    """

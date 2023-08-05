#
# Zope 3.1-style messagefactory module for Zope <= 2.9 (Zope 3.1)
#
# For PressRoom stolen from CMFPlone by naro

# BBB: Zope 2.8 / Zope X3.0

from zope.i18nmessageid import MessageIDFactory
msg_factory = MessageIDFactory('pressroom')

def PressRoomMessageFactory(ustr, default=None, mapping=None):
    message = msg_factory(ustr, default)
    if mapping is not None:
        message.mapping.update(mapping)
    return message


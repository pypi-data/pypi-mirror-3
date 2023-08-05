from zope.i18nmessageid import MessageFactory
name = 'fourdigits.portlet.twitter'
FourdigitsPortletTwitterMessageFactory = MessageFactory(name)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

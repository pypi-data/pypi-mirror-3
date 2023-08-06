from zope.i18nmessageid import MessageFactory

xmMessageFactory = MessageFactory('xm.theme')

# Allow restricted Python to import the  module
from AccessControl import allow_module
allow_module('xm.theme')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

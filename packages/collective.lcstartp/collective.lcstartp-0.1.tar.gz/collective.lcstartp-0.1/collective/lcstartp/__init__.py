# -*- extra stuff goes here -*-
from zope.i18nmessageid import MessageFactory

lcStartPageMessageFactory = MessageFactory('collective.lcstartp')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

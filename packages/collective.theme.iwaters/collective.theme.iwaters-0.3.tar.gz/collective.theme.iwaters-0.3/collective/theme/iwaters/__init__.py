# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory('collective.theme.iwaters')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

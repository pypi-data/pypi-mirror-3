# -*- coding: utf-8 -*-
from sc.psc.policy import patches
from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory('sc.psc.policy')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""


patches.run()

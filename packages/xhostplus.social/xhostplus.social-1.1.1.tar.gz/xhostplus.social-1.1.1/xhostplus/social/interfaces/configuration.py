# -*- coding: utf-8 -*-

"""Configlet interfaces using zope.formlib
"""

from zope.interface import Interface
from zope import schema

from xhostplus.social import socialMessageFactory as _

class ISocialConfiguration(Interface):

    two_click_buttons = schema.Bool(
        title=_(u"2 click buttons"),
        description=_(u"Enables the 2 click buttons with enhanced privacy."),
        default=False,
    )

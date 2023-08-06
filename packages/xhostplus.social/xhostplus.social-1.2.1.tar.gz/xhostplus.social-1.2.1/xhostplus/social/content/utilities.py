# -*- coding: utf-8 -*-

"""Utilities to store the settings
"""

from zope.interface import implements
from zope.component import getUtility
from zope.schema.fieldproperty import FieldProperty
from xhostplus.social.interfaces.configuration import ISocialConfiguration

from OFS.SimpleItem import SimpleItem

def social_configuration_adapter(context):
    return getUtility(ISocialConfiguration, context=context)

class SocialConfiguration(SimpleItem):
    implements(ISocialConfiguration)

    two_click_buttons = FieldProperty(ISocialConfiguration['two_click_buttons'])

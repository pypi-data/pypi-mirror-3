# -*- coding: utf-8 -*-
# $Id: __init__.py 78443 2009-01-06 13:44:52Z glenfant $
"""Actions portlet package"""

from zope.i18nmessageid import MessageFactory
ActionsPortletMessageFactory = MessageFactory('collective.portlet.actions')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    return

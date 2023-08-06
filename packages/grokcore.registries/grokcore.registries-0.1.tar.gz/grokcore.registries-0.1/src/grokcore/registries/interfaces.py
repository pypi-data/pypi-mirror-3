##############################################################################
#
# Copyright (c) 2006-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Grok interfaces
"""

from zope.configuration.fields import GlobalObject
from zope.interface import Interface
from zope.schema import TextLine


class IRegisterInDirective(Interface):
    """Use the specified registry for registering the contained components.
    """
    name = TextLine(
        title=u"Registration name",
        description=u"Name under which the registry is or will be registered.",
        required=False)

    registry = GlobalObject(
        title=u"Registry",
        description=u"Python path to the registry to use.",
        required=False)

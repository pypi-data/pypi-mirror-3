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
"""Base classes for Grok application components.

When an application developer builds a Grok-based application, the
classes they define each typically inherit from one of the base classes
provided here.

"""

from grokcore.component.util import provideUtility
from grokcore.registries.utils import query_registry, contextualSiteManager
from zope.component.globalregistry import GlobalAdapterRegistry
from zope.component.interfaces import IComponents, IComponentLookup
from zope.component.registry import Components
from zope.interface import implements, directlyProvides
from zope.location import Location


class BaseComponents(Location, Components):
    implements(IComponentLookup)

    def __init__(self, parent, name, bases=()):
        self.__name__ = name
        self.__parent__ = parent
        self._init_registries()
        self._init_registrations()
        self.__bases__ = tuple(bases)

    def _init_registries(self):
        self.adapters = GlobalAdapterRegistry(self, 'adapters')
        self.utilities = GlobalAdapterRegistry(self, 'utilities')

    def __reduce__(self):
        # Global site managers are pickled as global objects
        return query_registry, (self.__name__, self.__parent__)


def create_components_registry(parent=None, name='', bases=()):
    if parent is None:
        parent = contextualSiteManager()
    registry = BaseComponents(parent, name, bases)
    directlyProvides(registry, IComponents)
    provideUtility(registry, provides=IComponents, name=name)
    return registry

#############################################################################
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
"""Grokkers for Grok-configured components.

This `meta` module contains the actual grokker mechanisms for which the
Grok web framework is named.  A directive in the adjacent `meta.zcml`
file directs the `martian` library to scan this file, where it discovers
and registers the grokkers you see below.  The grokkers are then active
and available as `martian` recursively examines the packages and modules
of a Grok-based web application.

"""
from zope.component.hooks import setSite, getSite
from grokcore.registries.components import query_registry
from zope.configuration.config import GroupingContextDecorator
from zope.configuration.exceptions import ConfigurationError


class ConfigurationWrapperSite(object):
    """This a minimal fake Site, the only responsibility it has
    is to store our registry as a SiteManager and return it later.
    This is needed to fool siteinfo via setSite, zope.component.zcml.handler
    will grab the registry via zope.component.getSiteManager() then.
    """
    def __init__(self, sm):
        self.sm = sm

    def getSiteManager(self):
        return self.sm


def setActiveRegistry(context, registry):
    context.original = getSite()
    fakeSite = ConfigurationWrapperSite(registry)
    setSite(fakeSite)


def resetOriginalRegistry(context):
    setSite(context.original)


class RegisterIn(GroupingContextDecorator):

    # Marker that this directive has been used in the path
    registryChanged = True

    # Storage for the original site
    original = None

    def __init__(self, context, name="", registry=None, **kw):
        if not (bool(name) ^ bool(registry)):
            raise ConfigurationError(
                'You need to provide either the name of the registry or the '
                'registry object for the ``registerIn`` directive.')

        if hasattr(context, 'registryChanged') and context.registryChanged:
            raise ConfigurationError(
                'Nested ``registerIn`` directives are not permitted.')

        super(RegisterIn, self).__init__(context, **kw)

        if registry is None:
            self.registry = query_registry(name)
            if self.registry is None:
                raise ConfigurationError(
                    'No registry component given and no registry registered'
                    ' under the name %r' % name)
        else:
            self.registry = registry

    def before(self):
        self.context.action(
            discriminator=None,
            callable=setActiveRegistry,
            args=(self, self.registry),
            )

    def after(self):
        self.context.action(
            discriminator=None,
            callable=resetOriginalRegistry,
            args=(self,),
            )

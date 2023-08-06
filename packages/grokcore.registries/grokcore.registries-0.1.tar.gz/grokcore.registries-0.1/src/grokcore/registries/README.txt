===================
grokcore.registries
===================

With the help of this package you are now able to create
your on BaseComponents Registries. thanks to a zcml
directive, ´registerIn´, you can choose in which
Registry your grok Components will be registered.

Setup
-----

The first thing we have to do is to create an instance of
a BaseComponents Regsitry. For this task we use the
create_components_registry.

  >>> from grokcore.registries import create_components_registry
  >>> from zope.component.interfaces import IComponents
  >>> import zope.component

  >>> myRegistry = create_components_registry(name="myRegistry")

  >>> myRegistry
  <BaseComponents myRegistry>

  >>> IComponents.providedBy(myRegistry)
  True


It's possible to create a chain of Registries you have to provide
your Bases in the third argument of the create_components_registry.

  >>> myOtherRegistry = create_components_registry(
  ...     zope.component.globalSiteManager, 'myRegistry', (myRegistry,))
  >>> myOtherRegistry.__bases__
  (<BaseComponents myRegistry>,)


Basic Working
-------------

  >>> custom = create_components_registry(
  ...     zope.component.globalSiteManager, 'custom')

Let's make sure that the parent of the custom registry is the base registry:

  >>> custom.__parent__
  <BaseGlobalComponents base>

We make the custom Registry a Utility:

  >>> from zope.component.interfaces import IComponents
  >>> zope.component.provideUtility(custom, IComponents, 'custom')

  >>> custom = zope.component.getUtility(IComponents, name='custom')
  >>> custom
  <BaseComponents custom>


Now the registerIn function comes into the game. We register all stuff
from ´registries.global´ to the GlobalSiteManager, and the contents of
´registries.local´ to our custom Registry.


  >>> from zope.configuration import xmlconfig

  >>> context = xmlconfig.string('''
  ... <configure i18n_domain="zope">
  ...   <include package="zope.component" file="meta.zcml" />
  ...   <include package="grokcore.registries" file="meta.zcml" />
  ... </configure>
  ... ''')

  >>> context = xmlconfig.string('''
  ... <configure xmlns="http://namespaces.zope.org/zope"
  ...            xmlns:grok="http://namespaces.zope.org/grok"
  ...            i18n_domain="zope">
  ...
  ...   <include package="grokcore.component" file="meta.zcml" />
  ...
  ...   <grok:grok package="grokcore.registries.tests.registries.global" />
  ...   <registerIn registry="README.custom">
  ...     <grok:grok package="grokcore.registries.tests.registries.local" />
  ...   </registerIn>
  ...
  ... </configure>
  ... ''', context=context)

Now we can verify if we found our Components in the valid registries.
We start in searching in the GlobalSiteManager:


  >>> from grokcore.registries.tests.registries.interfaces import IExample
  >>> zope.component.getUtility(IExample, name="global")
  <grokcore.registries.tests.registries.global.MyExample object at ...>

  >>> zope.component.getUtility(IExample, name="local")
  Traceback (most recent call last):
  ...
  ComponentLookupError: (<InterfaceClass grokcore.registries.tests.registries.interfaces.IExample>, 'local')


Now we use our ´custom´ one:

  >>> custom.getUtility(IExample, name="local")
  <grokcore.registries.tests.registries.local.MyExample object at ...>


Using BaseRegistries (Stacked Registries)
-----------------------------------------

  >>> from zope.component.registry import Components
  >>> sm = Components()

  >>> sm.__bases__
  ()

  >>> sm.getUtility(IExample, name="local")
  Traceback (most recent call last):
  ...
  ComponentLookupError: (<InterfaceClass grokcore.registries.tests.registries.interfaces.IExample>, 'local')

If we stack our "custom" registry, in to the GlobalSiteManager we found all registries 

  >>> sm.__bases__ += (custom,)
  >>> sm.__bases__
  (<BaseComponents custom>,)

  >>> sm.getUtility(IExample, name="local")
  <grokcore.registries.tests.registries.local.MyExample object at 0...>

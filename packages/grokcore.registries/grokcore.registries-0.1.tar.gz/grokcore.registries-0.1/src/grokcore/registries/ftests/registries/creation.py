"""
  >>> my_registry
  <BaseComponents my_registry>

  >>> from zope.component.interfaces import IComponents
  >>> IComponents.providedBy(my_registry)
  True

  >>> chained_registry
  <BaseComponents chained_registry>

  >>> chained_registry.__bases__
  (<BaseComponents my_registry>,)
"""

import zope.component
from grokcore.registries import create_components_registry

my_registry = create_components_registry(name="my_registry")

chained_registry = create_components_registry(
    zope.component.globalSiteManager,
    'chained_registry',
    (my_registry,),
    )

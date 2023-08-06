"""
  >>> from pprint import pprint
  >>> from zope.component import getUtilitiesFor
  >>> from zope.component.interfaces import IComponents

  >>> registries = getUtilitiesFor(IComponents)
  >>> pprint([x for x in registries])
  [(u'chained_registry', <BaseComponents chained_registry>),
   (u'specialRegistry', <BaseComponents specialRegistry>),
   (u'my_registry', <BaseComponents my_registry>)]
"""
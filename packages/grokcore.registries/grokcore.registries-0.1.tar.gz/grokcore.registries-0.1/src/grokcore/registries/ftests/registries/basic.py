"""
 >>> from zope.component import getUtility
 >>> from grokcore.registries.tests.registries.interfaces import IExample

 >>> getUtility(IExample, name=u'global')
 <grokcore.registries.tests.registries.global.MyExample object at ...>

 >>> getUtility(IExample, name=u'local')
 Traceback (most recent call last):
 ...
 ComponentLookupError: (<InterfaceClass grokcore.registries.tests.registries.interfaces.IExample>, u'local')

 >>> specialRegistry.getUtility(IExample, name=u'local')
 <grokcore.registries.tests.registries.local.MyExample object at ...>
"""

from grokcore.registries import create_components_registry


specialRegistry = create_components_registry(name="specialRegistry")

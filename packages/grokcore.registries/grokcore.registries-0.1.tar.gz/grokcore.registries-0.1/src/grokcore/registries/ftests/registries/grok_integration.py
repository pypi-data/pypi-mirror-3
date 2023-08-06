"""
 >>> root = {}
 >>> root['app'] = MyApplication()

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

 >>> from zope.component.hooks import setSite
 >>> app = root['app']
 >>> setSite(root['app'])

 >>> getUtility(IExample, name=u'local')
 <grokcore.registries.tests.registries.local.MyExample object at ...>

 >>> setSite()

"""

from zope.component.registry import Components
from grokcore.registries.ftests.registries.basic import specialRegistry


class MyApplication(object):

    def __init__(self):
        self._sm = Components()

    def getSiteManager(self):
        current = self._sm
        current.__bases__ += (specialRegistry,)
        return current

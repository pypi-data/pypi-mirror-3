import grokcore.component as grok
from grokcore.registries.tests.registries.interfaces import IExample


class MyExample(grok.GlobalUtility):
    grok.name('override')
    grok.implements(IExample)

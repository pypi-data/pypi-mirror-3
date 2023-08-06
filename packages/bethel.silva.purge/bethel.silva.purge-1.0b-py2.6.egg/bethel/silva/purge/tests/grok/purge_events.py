from five import grok
from zope.component import getUtility
from z3c.caching.interfaces import IPurgeEvent
from silva.core.interfaces import IVersion

from bethel.silva.purge.interfaces import IPurgingService


@grok.subscribe(IPurgeEvent)
def simple_purge(event):
    context = event.object
    service = getUtility(IPurgingService, context=context)
    if not hasattr(service.aq_explicit, 'test_counter'):
        service.test_counter = []
    service.test_counter.append(event.object)

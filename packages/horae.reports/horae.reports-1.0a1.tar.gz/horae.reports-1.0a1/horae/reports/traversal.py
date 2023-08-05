import grok

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IRequest
from zope.location import LocationProxy

from horae.reports import interfaces


class ReportsLocationProxy(LocationProxy):
    def traverse(self, name):
        obj = self.get_object(name)
        if obj is not None:
            obj = LocationProxy(obj, self, str(obj.id))
        return obj


class ReportsNamespaceTraverser(grok.MultiAdapter):
    """ Reports namespace traverser
    """
    grok.name('reports')
    grok.adapts(interfaces.IReportsContext, IRequest)
    grok.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return ReportsLocationProxy(interfaces.IReports(self.context), self.context, '++reports++')

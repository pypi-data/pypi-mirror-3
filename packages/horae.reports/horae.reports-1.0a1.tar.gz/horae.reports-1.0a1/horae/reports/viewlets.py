import grok

from zope import interface

from horae.layout import layout
from horae.layout.viewlets import ContentAfterManager
from horae.search import search

from horae.reports import interfaces

grok.templatedir('viewlet_templates')


class CreateReport(layout.Viewlet):
    """ Renders a button to create a report from the current search
    """
    grok.viewletmanager(ContentAfterManager)
    grok.context(interface.Interface)
    grok.view(search.AdvancedSearch)
    grok.order(10)

    def update(self):
        self.url = self.view.url(interfaces.IReports(self.context), 'create') if len(self.view.query_data()) else None

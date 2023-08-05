import grok

from zope.publisher.interfaces.browser import IBrowserRequest
from zope.i18n import translate
from zope.location import LocationProxy
from zope.security import checkPermission
from zope.security.interfaces import Unauthorized

from megrok import navigation

from horae.core import utils
from horae.core.interfaces import IHorae
from horae.auth.utils import displayUser
from horae.layout import layout
from horae.layout import objects
from horae.layout.interfaces import IViewsMenu, IActionsMenu, IMainNavigation, IObjectTableActionsProvider
from horae.layout import _ as _la
from horae.ticketing import _ as _t
from horae.lifecycle import _ as _l
from horae.search import search

from horae.reports import _
from horae.reports import interfaces
from horae.reports import reports

grok.templatedir('templates')


class Reports(objects.ObjectOverview):
    """ Overview of all available reports
    """
    grok.context(interfaces.IReports)
    grok.require('zope.View')
    grok.name('index')

    columns = [('name', _t(u'Name')), ('creator', _l(u'Creator')), ('creation_date', _l(u'Creation date')), ('actions', u'')]
    container_iface = interfaces.IReports
    label = _(u'Reports')

    def row_factory(self, object, columns, request):
        row = super(Reports, self).row_factory(object, columns, request)
        row['name'] = '<a href="%s">%s</a>' % (self.url(object), object.name)
        row['creator'] = displayUser(object.creator)
        row['creation_date'] = utils.formatDateTime(object.creation_date, request)
        return row

    def add(self):
        return False

    def objects(self):
        return list(self.context.objects(contextual=isinstance(self.context, LocationProxy)))

    def url(self, obj=None, name=None, data=None):
        if interfaces.IReport.providedBy(obj) and isinstance(self.context, LocationProxy):
            obj = LocationProxy(obj, self.context, str(obj.id))
        return super(Reports, self).url(obj, name, data)

    def update(self):
        super(Reports, self).update()
        self.back = self.url(self.context.__parent__)


class GlobalReports(layout.View):
    """ View redirecting to the global reports container
    """
    grok.context(IHorae)
    grok.require('zope.View')
    grok.name('global-reports')
    navigation.sitemenuitem(IMainNavigation, _(u'Reports'), order=40)

    def render(self):
        return self.redirect(self.url(interfaces.IReports(self.context)))


class ContextualReports(layout.View):
    """ View redirecting to the contextual reports container
    """
    grok.context(interfaces.IReportsContext)
    grok.require('zope.View')
    grok.name('reports')
    navigation.menuitem(IViewsMenu, _(u'Reports'))

    def render(self):
        return self.redirect(self.url(self.context, '++reports++'))


class ReportsActionsProvider(grok.MultiAdapter):
    """ Action provider for reports add actions to delete
        and edit a report
    """
    grok.adapts(interfaces.IReport, Reports)
    grok.implements(IObjectTableActionsProvider)
    grok.name('horae.reports.objecttableactions.report')

    def __init__(self, context, view):
        self.context = context
        self.view = view

    def actions(self, request):
        actions = []
        if checkPermission('horae.Edit', self.context):
            actions.append({'url': self.view.url(self.context, 'edit'),
                            'label': translate(_t(u'Edit'), context=request),
                            'cssClass': ''})
        if checkPermission('horae.Delete', self.context):
            actions.append({'url': self.view.url(self.context, 'delete'),
                            'label': translate(_l(u'Delete'), context=request),
                            'cssClass': 'button-destructive delete'})
        return actions


class ReportsBreadcrumbs(reports.ReportsBreadcrumbs):
    """ Makes the contextual reports container visible in the breadcrumbs
    """
    grok.adapts(ContextualReports, IBrowserRequest)

    @property
    def url(self):
        return self.context.url()


class Report(search.BaseAdvancedSearch):
    """ View of a report
    """
    grok.context(interfaces.IReport)
    grok.require('zope.View')
    grok.name('index')
    grok.template('report')

    caption = u''

    def __call__(self, plain=None, selector=None):
        if not self.context.public and not checkPermission('horae.View', self.context):
            raise Unauthorized()
        return super(Report, self).__call__(plain, selector)

    def base_url(self):
        return self.url(self.context)

    def update(self):
        self.rendered = self.table()

    def query_data(self):
        return self.context.properties()

    def update_form(self):
        pass


class CreateReport(layout.AddForm):
    """ Add form for a report
    """
    grok.context(interfaces.IReports)
    grok.name('create')
    grok.require('zope.View')
    form_fields = grok.AutoFields(interfaces.IReport).omit('id')

    @property
    def label(self):
        return _(u'Create report from current search')

    def object_type(self):
        return _(u'Report')

    def create(self, **data):
        return interfaces.IReport(self.request)

    def add(self, obj):
        interfaces.IReports(self.context).add_object(obj)


class EditReport(layout.EditForm):
    """ Edit form of a report
    """
    grok.context(interfaces.IReport)
    grok.name('edit')
    grok.require('horae.Edit')
    navigation.menuitem(IActionsMenu, _t(u'Edit'))
    form_fields = grok.AutoFields(interfaces.IReport).omit('id')

    def object_type(self):
        return _(u'Report')


class DeleteReport(layout.DeleteForm):
    """ Delete form of a report
    """
    grok.context(interfaces.IReport)
    grok.require('horae.Delete')
    grok.name('delete')
    navigation.menuitem(IActionsMenu, _la(u'Delete'))

    def object_type(self):
        return _(u'Report')

    def item_title(self):
        return self.context.name

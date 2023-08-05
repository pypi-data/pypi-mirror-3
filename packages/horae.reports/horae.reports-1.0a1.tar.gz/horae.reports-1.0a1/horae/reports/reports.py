import grok

from zope import schema
from zope import interface
from zope import component
from zope.site.hooks import getSite
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security import checkPermission
from zope.securitypolicy.interfaces import IPrincipalPermissionManager

from horae.core import container, utils
from horae.lifecycle import lifecycle
from horae.auth.interfaces import IShareable
from horae.layout import layout
from horae.ticketing import ticketing

from horae.reports import _
from horae.reports import interfaces

interface.classImplements(ticketing.Client, interfaces.IReportsContext)
interface.classImplements(ticketing.Project, interfaces.IReportsContext)
interface.classImplements(ticketing.Milestone, interfaces.IReportsContext)


class Reports(container.Container):
    """ A container for reports
    """
    grok.implements(interfaces.IReports)

    def id_key(self):
        return 'report'

    def objects(self, permission='horae.View', contextual=False):
        """ Iterator over reports filtered by the given permission and optionally only contextual reports
        """
        for report in super(Reports, self).objects():
            if (report.public or checkPermission(permission, report)) and (not contextual or interfaces.IContextualReport.providedBy(report)):
                yield report


class ReportsBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.adapts(interfaces.IReports, IBrowserRequest)

    permission = 'zope.View'
    name = _(u'Reports')


@grok.adapter(interface.Interface)
@grok.implementer(interfaces.IReports)
def reports_of_site(context):
    site = getSite()
    if not 'reports' in site:
        site['reports'] = Reports()
    return site['reports']


class Report(grok.Model, lifecycle.LifecycleAwareMixin):
    """ A report
    """
    grok.implements(interfaces.IReport, IShareable)

    id = schema.fieldproperty.FieldProperty(interfaces.IReport['id'])
    name = schema.fieldproperty.FieldProperty(interfaces.IReport['name'])
    description = schema.fieldproperty.FieldProperty(interfaces.IReport['description'])
    public = schema.fieldproperty.FieldProperty(interfaces.IReport['public'])

    def __init__(self, properties):
        super(Report, self).__init__()
        if properties.get('current', None):
            interface.alsoProvides(self, interfaces.IContextualReport)
        self._properties = properties

    def properties(self):
        """ Returns a dict to be used for searching
        """
        return self._properties


@grok.subscribe(interfaces.IReport, grok.IObjectAddedEvent)
def assign_owner_permissions(report, event):
    """ Grants horae.View, horae.Edit, horae.Delete and horae.Sharing
        permissions to the current user on report creation
    """
    try:
        principal = utils.getRequest(None).principal.id
        manager = IPrincipalPermissionManager(report)
        manager.grantPermissionToPrincipal('horae.View', principal)
        manager.grantPermissionToPrincipal('horae.Edit', principal)
        manager.grantPermissionToPrincipal('horae.Delete', principal)
        manager.grantPermissionToPrincipal('horae.Sharing', principal)
    except:
        pass


class ReportBreadcrumbs(layout.BaseBreadcrumbs):
    """ Adapter making an object visible in the breadcrumbs
    """
    grok.adapts(interfaces.IReport, IBrowserRequest)

    permission = 'zope.View'

    @property
    def name(self):
        return self.context.name


@grok.adapter(IBrowserRequest)
@grok.implementer(interfaces.IReport)
def report_from_search(request):
    """ Creates a report from the current search
    """
    search = component.getMultiAdapter((getSite(), request), name=u'advancedsearch')
    return Report(dict([(name, value) for name, value in search.query_data().items()]))

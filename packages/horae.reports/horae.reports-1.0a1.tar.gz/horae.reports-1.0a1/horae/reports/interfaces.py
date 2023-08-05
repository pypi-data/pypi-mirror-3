from zope import interface
from zope import schema

from megrok.form import fields

from horae.core import interfaces
from horae.properties import _ as _p

from horae.reports import _


class IReportsContext(interface.Interface):
    """ Marker interface for objects displaying reports
    """


class IReports(interfaces.IContainer):
    """ A container for reports
    """

    def objects(permission='horae.View', contextual=False):
        """ Iterator over reports filtered by the given permission and optionally only contextual reports
        """


class IReport(interfaces.IIntId):
    """ A report
    """

    name = schema.TextLine(
        title=_p(u'Name'),
        required=True
    )

    description = fields.HTML(
        title=_p(u'Description'),
        required=False
    )

    public = schema.Bool(
        title=_(u'Public'),
        required=False,
        default=True
    )

    def properties():
        """ Returns a dict of name, value pairs to be used for searching
        """


class IContextualReport(IReport):
    """ A report searching in context
    """

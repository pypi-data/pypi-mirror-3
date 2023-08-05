import grok

from zope import schema
from zope import interface
from zope.interface import alsoProvides
from zope.publisher.interfaces import IRequest

from horae.core.interfaces import IHorae
from horae.core import container
from horae.core import utils
from horae.layout import layout

from horae.dashboard import interfaces


class Dashboards(container.Container):
    """ A container for dashboards
    """
    grok.implements(interfaces.IDashboards)


@grok.adapter(IHorae)
@grok.implementer(interfaces.IGroupDashboards)
def groupdashboards_of_site(site):
    """ Adapter providing the container for group dashboards
    """
    if not 'groupdashboards' in site:
        site['groupdashboards'] = Dashboards()
        alsoProvides(site['groupdashboards'], interfaces.IGroupDashboards)
    return site['groupdashboards']


@grok.adapter(IHorae)
@grok.implementer(interfaces.IUserDashboards)
def userdashboards_of_site(site):
    """ Adapter providing the container for user dashboards

        :adapts:
            :py:class:`horae.core.interfaces.IHorae`

        :implements:
            :py:class:`horae.dashboard.interfaces.IUserDashboards`
    """
    if not 'userdashboards' in site:
        site['userdashboards'] = Dashboards()
        alsoProvides(site['userdashboards'], interfaces.IUserDashboards)
    return site['userdashboards']


class Dashboard(container.Container):
    """ A dashboard
    """
    grok.implements(interfaces.IDashboard)

    def id_key(self):
        return 'widget'


@grok.adapter(interface.Interface, IRequest)
@grok.implementer(interfaces.IDashboard)
def user_dashboard(context, request):
    """ Adapter providing the dashboard of the current user

        :adapts:
            :py:class:`zope.interface.Interface`,
            :py:class:`zope.publisher.interfaces.IRequest`

        :implements:
            :py:class:`horae.dashboard.interfaces.IDashboard`
    """
    if request.principal is None:
        return None
    site = utils.findParentByInterface(context, IHorae)
    dashboards = interfaces.IUserDashboards(site)
    if not request.principal.id in dashboards:
        dashboard = Dashboard()
        dashboard.id = request.principal.id
        dashboards.add_object(dashboard)
    return dashboards.get(request.principal.id)


class Widget(grok.Model):
    """ A widget
    """
    grok.implements(interfaces.IWidget)

    factory = None
    title = None
    resizable = True

    width = schema.fieldproperty.FieldProperty(interfaces.IWidget['width'])
    height = schema.fieldproperty.FieldProperty(interfaces.IWidget['height'])
    sidebar = schema.fieldproperty.FieldProperty(interfaces.IWidget['sidebar'])


class Form(layout.Form):
    """ Base class for widgets displaying a form
    """
    grok.baseclass()

    def __init__(self, *args, **kwargs):
        super(Form, self).__init__(*args, **kwargs)
        self.setPrefix(self.context.factory + '_' + str(self.context.id))

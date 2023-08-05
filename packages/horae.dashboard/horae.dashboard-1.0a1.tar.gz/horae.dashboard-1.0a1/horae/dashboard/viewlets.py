import grok

from zope import component
from zope import interface

from horae.core.interfaces import IHorae
from horae.core.utils import findParentByInterface
from horae.auth import utils
from horae.layout import layout
from horae.layout import viewlets
from horae.ticketing.viewlets import Name

from horae.dashboard import _
from horae.dashboard import interfaces

grok.templatedir('viewlet_templates')
grok.context(interface.Interface)


class Sidebar(layout.Viewlet):
    """ Renders the users dashboard widgets defined to be displayed
        in the sidebar
    """
    grok.viewletmanager(viewlets.SidebarManager)
    grok.order(20)

    def update(self):
        self.dashboard = component.getMultiAdapter((self.context, self.request), interfaces.IDashboard)
        self.widgets = []
        for widget in self.dashboard.objects():
            if not widget.sidebar:
                continue
            self.widgets.append({'factory': widget.factory,
                                 'view': component.getMultiAdapter((widget, self.request), name='index')})
        super(Sidebar, self).update()


class DashboardName(Name):
    """ Renders the dashboards name
    """
    grok.viewletmanager(viewlets.ContentBeforeManager)
    grok.context(interfaces.IDashboard)
    grok.order(0)
    grok.name('name')

    def update(self):
        self.name = _(u'Personal dashboard')
        self.description = None
        self.id = None


class GroupName(Name):
    """ Renders the group dashboards name
    """
    grok.viewletmanager(viewlets.ContentBeforeManager)
    grok.context(interfaces.IGroupDashboard)
    grok.order(0)
    grok.name('name')

    def update(self):
        self.name = _(u'Group dashboard')
        self.description = utils.getGroup(self.context.id).name
        self.id = None


class Dashboards(layout.Viewlet):
    """ Renders the different available dashboards
    """
    grok.viewletmanager(viewlets.ContentBeforeManager)
    grok.context(interfaces.IDashboard)
    grok.order(10)

    def update(self):
        site = findParentByInterface(self.context, IHorae)
        self.dashboards = []
        self.dashboards.append({'name': _(u'Personal dashboard'),
                                'url': self.view.url(site, '++dashboard++')})
        user = utils.getUser(self.request.principal.id)
        if user is not None:
            group_url = self.view.url(site, '++groupdashboard++')
            for group in user.groups:
                if group is None:
                    continue
                self.dashboards.append({'name': group.name,
                                        'url': group_url + '/' + str(group.id)})

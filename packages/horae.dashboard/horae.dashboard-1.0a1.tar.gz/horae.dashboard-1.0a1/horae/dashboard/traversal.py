import grok

from zope import component
from zope import interface
from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces import IRequest
from zope.location import LocationProxy

from horae.core.utils import getRequest
from horae.core.interfaces import IHorae
from horae.auth import utils

from horae.dashboard import interfaces
from horae.dashboard import dashboard


class GroupDashboardLocationProxy(LocationProxy):

    def traverse(self, name):
        group = utils.getGroup(name)
        if group is None:
            return None
        request = getRequest(None)
        if request is None:
            return None
        user = utils.getUser(request.principal.id)
        if user is None:
            return None
        if not group in user.groups:
            return None
        if not name in self:
            obj = dashboard.Dashboard()
            obj.id = str(group.id)
            interface.alsoProvides(obj, interfaces.IGroupDashboard)
            self.add_object(obj)
        else:
            obj = self.get_object(name)
        return LocationProxy(obj, self, obj.id)


class DashbordNamespaceTraverser(grok.MultiAdapter):
    """ Dashboard namespace traverser
    """
    grok.name('dashboard')
    grok.adapts(IHorae, IRequest)
    grok.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return LocationProxy(component.getMultiAdapter((self.context, self.request), interfaces.IDashboard), self.context, '++dashboard++')


class GroupDashboardNamespaceTraverser(grok.MultiAdapter):
    """ Dashboard namespace traverser
    """
    grok.name('groupdashboard')
    grok.adapts(IHorae, IRequest)
    grok.implements(ITraversable)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def traverse(self, name, furtherPath):
        return GroupDashboardLocationProxy(interfaces.IGroupDashboards(self.context), self.context, '++groupdashboard++')

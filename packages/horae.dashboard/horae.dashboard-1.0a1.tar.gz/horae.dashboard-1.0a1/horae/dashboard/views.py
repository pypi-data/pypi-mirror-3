import grok

from zope import component
from zope.formlib.widget import renderElement
from zope.site.hooks import getSite
from zope.publisher.interfaces.browser import IBrowserRequest

from megrok import navigation

from horae.core.interfaces import IHorae
from horae.auth.interfaces import IStartPage
from horae.layout import layout
from horae.layout.interfaces import IMainNavigation, IDisplayView

from horae.dashboard import _
from horae.dashboard import interfaces

grok.templatedir('templates')


class Dashboard(layout.View):
    """ View displaying the dashboard and it's widgets
    """
    grok.context(interfaces.IDashboard)
    grok.require('zope.View')
    grok.name('index')
    grok.implements(IDisplayView)

    def __call__(self, plain=False, selector=None, order=None, size=None, width=None, height=None):
        if order is not None:
            return self.update_order(order)
        if size is not None:
            return self.update_size(size, width, height)
        return super(Dashboard, self).__call__(plain, selector)

    def update(self):
        self.rows = self.get_rows()
        self.types = [{'title': factory.name,
                       'value': name} for name, factory in component.getUtilitiesFor(interfaces.IWidgetFactory)]
        self.add = False if not self.types else self.url(self.context) + '/add-dashboard-widget'

    def get_rows(self):
        rows = []
        pos = 0
        row = []
        for widget in self.context.objects():
            if widget.width > 16 - pos:
                rows.append(row)
                row = []
                pos = 0
            row.append({'width': widget.width,
                        'style': 'height: %spx' % widget.height if widget.resizable else '',
                        'id': widget.id,
                        'url': self.url(widget),
                        'resizable': 'resizable' if widget.resizable else '',
                        'view': component.getMultiAdapter((widget, self.request), name='index'),
                        'factory': widget.factory,
                        'edit': self.url(self.context) + '/edit-dashboard-widget?id=' + widget.__name__,
                        'delete': self.url(self.context) + '/delete-dashboard-widget?id=' + widget.__name__})
            pos += widget.width
        if row:
            rows.append(row)
        return rows

    def update_order(self, order):
        self.context.updateOrder([id for id in order.split(',') if id in self.context])
        return u'1'

    def update_size(self, id, width, height):
        widget = self.context.get_object(id)
        if widget is None:
            return u'0'
        widget.width = int(width)
        widget.height = int(height)
        return u'1'


class UserDashboard(grok.View):
    """ View redirecting to the user's dashboard
    """
    grok.context(IHorae)
    grok.require('zope.View')

    navigation.sitemenuitem(IMainNavigation, _(u'Dashboard'), order=10)

    def render(self):
        self.redirect(self.url(self.context) + '/++dashboard++')
        return u''


class DashboardStartPage(grok.Adapter):
    """ Start page provider redirecting the user to his dashboard after
        logging in
    """
    grok.context(IBrowserRequest)
    grok.implements(IStartPage)

    def __call__(self):
        return grok.url(self.context, getSite(), '++dashboard++')


class WidgetBaseForm(object):
    """ Base widget form providing the object type, next and cancel URL
    """
    grok.context(interfaces.IDashboard)
    grok.require('zope.View')

    def object_type(self):
        return self.factory.name

    def next_url(self, obj=None):
        return self.url(self.dashboard)

    def cancel_url(self):
        return self.url(self.dashboard)


class WidgetBaseEditForm(WidgetBaseForm):
    """ Base widget edit form used for widget edit and delete forms
    """

    def __call__(self, id, plain=False, selector=None):
        self.dashboard = self.context
        self.context = self.dashboard.get(id)
        if self.context is None:
            return self.redirect(self.url(self.dashboard))
        self.factory = component.getUtility(interfaces.IWidgetFactory, self.context.factory)
        self.form_fields = grok.AutoFields(self.factory.schema).omit('id', 'width', 'height')
        self.additional = renderElement('input',
                                        type='hidden',
                                        name='id',
                                        value=self.context.id)
        return super(WidgetBaseEditForm, self).__call__(plain, selector)


class WidgetAddForm(WidgetBaseForm, layout.AddForm):
    """ Widget add form looking up the schema of the
        :py:class:`horae.dashboard.interfaces.IWidgetFactory`
        to provide the required fields
    """
    grok.name('add-dashboard-widget')

    def __call__(self, name, plain=False, selector=None):
        self.dashboard = self.context
        self.name = name
        self.factory = component.getUtility(interfaces.IWidgetFactory, name)
        self.form_fields = grok.AutoFields(self.factory.schema).omit('id', 'width', 'height')
        self.additional = renderElement('input',
                                        type='hidden',
                                        name='name',
                                        value=self.name)
        return super(WidgetAddForm, self).__call__(plain, selector)

    def create(self, **data):
        obj = self.factory()
        obj.factory = self.name
        return obj

    def add(self, obj):
        self.context.add_object(obj)


class WidgetEditForm(WidgetBaseEditForm, layout.EditForm):
    """ Widget edit form
    """
    grok.name('edit-dashboard-widget')


class WidgetDeleteForm(WidgetBaseEditForm, layout.DeleteForm):
    """ Widget delete form
    """
    grok.name('delete-dashboard-widget')

    def item_title(self):
        return self.context.title

    def delete(self):
        self.dashboard.del_object(self.context.id)

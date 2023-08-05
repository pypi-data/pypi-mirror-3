import grok

from zope import schema
from zope import component
from zope.i18n import translate

from horae.layout import layout
from horae.lifecycle.interfaces import ILatest
from horae.ticketing.interfaces import IClient, IProject, IMilestone, ITicket
from horae.search import _ as _s
from horae.search.search import SearchMixin

from horae.dashboard import interfaces
from horae.dashboard import dashboard
from horae.dashboard import _


class ILatestWidget(interfaces.IWidget):
    """ Provides a widget showing the latest objects
    """

    amount = schema.Int(
        title=_(u'Number of objects to display'),
        default=10,
        min=1
    )

    interfaces = schema.Set(
        title=_(u'Objects to display'),
        required=False,
        value_type=schema.Choice(
            vocabulary=schema.vocabulary.SimpleVocabulary((
                schema.vocabulary.SimpleTerm(IClient, IClient.__identifier__, _s(u'Clients')),
                schema.vocabulary.SimpleTerm(IProject, IProject.__identifier__, _s(u'Projects')),
                schema.vocabulary.SimpleTerm(IMilestone, IMilestone.__identifier__, _s(u'Milestones')),
                schema.vocabulary.SimpleTerm(ITicket, ITicket.__identifier__, _s(u'Tickets'))
            ))
        )
    )


class LatestWidgetFactory(grok.GlobalUtility):
    """ Latest widget factory
    """
    grok.name('latest')
    grok.implements(interfaces.IWidgetFactory)

    name = _(u'Latest')
    schema = ILatestWidget

    def __call__(self):
        """ Creates and returns a IWidget instance
        """
        return LatestWidget()


class LatestWidget(dashboard.Widget):
    """ A widget showing the latest objects
    """
    grok.implements(ILatestWidget)

    title = _(u'Latest')
    amount = schema.fieldproperty.FieldProperty(ILatestWidget['amount'])
    interfaces = schema.fieldproperty.FieldProperty(ILatestWidget['interfaces'])


class LatestWidgetIndex(SearchMixin, layout.View):
    """ View of a latest widget
    """
    grok.context(ILatestWidget)
    grok.require('horae.View')
    grok.name('index')

    def caption(self):
        caption = translate(_(u'Latest'), context=self.request)
        if len(self.context.interfaces):
            types = []
            for interface in self.context.interfaces:
                types.append(translate(ILatestWidget['interfaces'].value_type.vocabulary.getTerm(interface).title, context=self.request))
            caption += '<small>' + ', '.join(types) + '</small>'
        return caption

    def createTable(self):
        table = component.getMultiAdapter((self.context, self.request), name='table')
        table.page_size = self.page_size
        table.columns = [('id', _s(u'ID')), ('name', _s(u'Name'))]
        if not len(self.context.interfaces) == 1:
            table.columns.append(('type', _s(u'Type')))
        table.caption = self.caption()
        table.row_factory = self.row_factory
        return table

    def results(self):
        table = self.createTable()
        latest = ILatest(self.request)
        results = []
        for obj in latest.objects(*self.context.interfaces):
            results.append(obj)
            if len(results) >= self.context.amount:
                break
        return results, table

    def render(self):
        return self.table()

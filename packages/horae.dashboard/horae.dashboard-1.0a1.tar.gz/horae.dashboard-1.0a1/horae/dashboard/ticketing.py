import grok

from datetime import datetime, timedelta

from zope import component
from zope import schema
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.security import checkPermission
from zope.traversing.interfaces import ITraversable
from zope.site.hooks import getSite
from zope.event import notify

from hurry import query

from horae.core import utils
from horae.auth.utils import getUser
from horae.properties.interfaces import IComplete, IOffer, IPropertied
from horae.autocomplete import fields
from horae.autocomplete.interfaces import IValueProvider, IAutocompleteChoice
from horae.autocomplete.providers import AbstractValueProvider
from horae.lifecycle.interfaces import ILatest
from horae.ticketing.interfaces import ITicket
from horae.ticketing.events import TicketChangedEvent
from horae.ticketing import user
from horae.ticketing import _ as _t
from horae.timeaware.interfaces import ITimeRange, ITimeEntryFactory

from horae.dashboard import _
from horae.dashboard import dashboard
from horae.dashboard import interfaces

MAX_RESULTS = 25


class ITimeTrackingWidget(interfaces.IWidget):
    """ Provides a widget to track time on tickets
    """


def term_factory(ticket):
    return schema.vocabulary.SimpleTerm(ticket, ticket.id, '#%s %s' % (ticket.id, ticket.name))


def search_tickets(context, term=None, request=None, factory=term_factory, max=None):
    if term:
        try:
            ticket = component.getMultiAdapter((getSite(), utils.getRequest()), ITraversable, 'ticket').traverse(term, None)
            if not IComplete(ticket, lambda: False)() and not IOffer(ticket, lambda: False)() and checkPermission('horae.ChangeTicket', ticket):
                return [factory(ticket), ]
        except:
            pass
        term = '*' + '* *'.join(term.split(' ')) + '*'
    values = []
    seen = []
    try:
        if request is None:
            request = utils.getRequest()
        principal = request.principal
        for ticket in ILatest(principal).objects(ITicket):
            if not IComplete(ticket, lambda: False)() and not IOffer(ticket, lambda: False)() and term in ticket.name or str(ticket.id).startswith(term) and checkPermission('horae.ChangeTicket', ticket):
                values.append(factory(ticket))
                seen.append(ticket.id)
            if max is not None and len(values) >= max:
                return values
        queries = [query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
                   query.Eq(('catalog', 'complete'), 0),
                   query.Eq(('catalog', 'offer'), 0),
                   query.Eq(('properties', 'responsible'), principal.id)]
        if term:
            queries.append(query.Text(('catalog', 'text'), term))
        if seen:
            queries.extend([query.NotEq(('catalog', 'id'), id) for id in seen])
        results = component.getUtility(query.interfaces.IQuery).searchResults(query.And(*queries), sort_field=('catalog', 'modification_date'), reverse=True)
        for ticket in results:
            if checkPermission('horae.ChangeTicket', ticket):
                values.append(factory(ticket))
                seen.append(ticket.id)
            if max is not None and len(values) >= max:
                return values
    except:
        pass
    queries = [query.set.AnyOf(('catalog', 'implements'), [ITicket.__identifier__, ]),
               query.Eq(('catalog', 'complete'), 0),
               query.Eq(('catalog', 'offer'), 0)]
    if term:
        queries.append(query.Text(('catalog', 'text'), term))
    if seen:
        queries.extend([query.NotEq(('catalog', 'id'), id) for id in seen])
    results = component.getUtility(query.interfaces.IQuery).searchResults(query.And(*queries), sort_field=('catalog', 'modification_date'), reverse=True)
    for ticket in results:
        if checkPermission('horae.ChangeTicket', ticket):
            values.append(factory(ticket))
        if max is not None and len(values) >= max:
            return values
    return values


class TicketValueProvider(grok.MultiAdapter, AbstractValueProvider):
    """ Value provider for the ticket autocomplete field of the time tracking
        widget
    """
    grok.adapts(ITimeTrackingWidget, IAutocompleteChoice, IBrowserRequest)
    grok.provides(IValueProvider)
    grok.name('ticket')

    def __init__(self, context, field, request):
        super(TicketValueProvider, self).__init__(field, request)
        self.context = context

    def factory(self, ticket):
        return (ticket.id, '#%s %s' % (ticket.id, ticket.name))

    def __call__(self, term):
        return search_tickets(self.context, term, self.request, self.factory, MAX_RESULTS)


class TicketsVocabulary(object):
    """ Lazy vocabulary for the ticket autocomplete field of the time tracking
        widget
    """
    grok.implements(schema.interfaces.IVocabularyTokenized)

    def __init__(self, context):
        self.context = context

    def __contains__(self, value):
        if not ITicket.providedBy(value):
            return False
        return not IComplete(value, lambda: False)() and not IOffer(value, lambda: False)() and checkPermission('horae.ChangeTicket', value)

    def getTerm(self, value):
        if not value in self:
            raise LookupError(value)
        return term_factory(value)

    def __iter__(self):
        try:
            request = utils.getRequest()
            principal = request.principal
            for ticket in ILatest(principal).objects(ITicket):
                if ticket in self:
                    yield term_factory(ticket)
        except:
            pass

    def __len__(self):
        return 1

    def getTermByToken(self, token):
        try:
            ticket = component.getMultiAdapter((getSite(), utils.getRequest()), ITraversable, 'ticket').traverse(token, None)
            assert ticket in self
            return term_factory(ticket)
        except:
            raise LookupError(token)


def tickets_vocabulary_factory(context):
    return TicketsVocabulary(context)
schema.vocabulary.getVocabularyRegistry().register('horae.dashboard.ticketing.tickets', tickets_vocabulary_factory)


class TimeTrackingWidgetFactory(grok.GlobalUtility):
    """ Time tracking widget factory
    """
    grok.name('timetracking')
    grok.implements(interfaces.IWidgetFactory)

    name = _(u'Time tracking')
    schema = ITimeTrackingWidget

    def __call__(self):
        """ Creates and returns a IWidget instance
        """
        return TimeTrackingWidget()


class TimeTrackingWidget(dashboard.Widget):
    """ A widget providing a simple form to track time on tickets
    """
    grok.implements(ITimeTrackingWidget)

    title = _(u'Time tracking')
    resizable = False


class ITimeTrackingWidgetForm(ITimeRange):
    """ Schema of the time tracking form
    """

    ticket = fields.AutocompleteChoice(
        title=_t(u'Ticket'),
        required=True,
        vocabulary='horae.dashboard.ticketing.tickets'
    )

    date_hours = schema.Float(
        title=_t(u'Hours'),
        required=True,
        default=1.0
    )


class TimeTrackingWidgetIndex(dashboard.Form):
    """ The view of the time tracking widget
    """
    grok.context(ITimeTrackingWidget)
    grok.require('horae.View')
    grok.name('index')

    label = _(u'Time tracking')

    def update(self):
        self.form_fields = grok.AutoFields(ITimeTrackingWidgetForm).omit('date_start', 'date_end') + grok.AutoFields(ITimeTrackingWidgetForm).omit('ticket', 'date_hours')
        super(TimeTrackingWidgetIndex, self).update()

    def setUpWidgets(self, ignore_request=False):
        super(TimeTrackingWidgetIndex, self).setUpWidgets(ignore_request)
        if not self.widgets['ticket'].hasInput() or ignore_request:
            for ticket in ILatest(self.request).objects(ITicket):
                if not IComplete(ticket, lambda: False)() and not IOffer(ticket, lambda: False)():
                    self.widgets['ticket'].setRenderedValue(ticket)
                    break
        self.widgets['ticket'].form_url = self.url(self.context) + '/index'
        if not self.widgets['date_start'].hasInput() or ignore_request:
            self.widgets['date_start'].setRenderedValue(datetime.now() - timedelta(hours=1))
        if not self.widgets['date_end'].hasInput() or ignore_request:
            self.widgets['date_end'].setRenderedValue(datetime.now())

    @grok.action(_(u'Save'), name='save')
    def handle_save(self, **data):
        self.status = _(u'Time successfully stored')
        self.statusCssClass = 'success'
        ticket = data['ticket']
        previous = {}
        for change in IPropertied(ticket).changelog():
            previous.update(dict(change.properties()))
        ticket.new_change()
        self.call_extenders('apply', obj=ticket, **data)
        factory = ITimeEntryFactory(ticket)
        factory.date_start = data['date_start']
        factory.date_end = data['date_end']
        factory.create()
        for key in self.request.form.keys():
            if key.startswith(self.prefix):
                del self.request.form[key]
        notify(grok.ObjectModifiedEvent(ticket))
        notify(TicketChangedEvent(ticket, IPropertied(ticket).current(), previous))


class IUserTicketsWidget(interfaces.IWidget):
    """ Provides a list of tickets the current user is responsible for
    """

    amount = schema.Int(
        title=_(u'Number of tickets to display'),
        default=10,
        min=1
    )


class UserTicketsWidgetFactory(grok.GlobalUtility):
    """ User tickets widget factory
    """
    grok.name('usertickets')
    grok.implements(interfaces.IWidgetFactory)

    name = _(u'My tickets')
    schema = IUserTicketsWidget

    def __call__(self):
        """ Creates and returns a IWidget instance
        """
        widget = UserTicketsWidget()
        widget.width = 8
        return widget


class UserTicketsWidget(dashboard.Widget):
    """ A widget showing the tickets a user is responsible for
    """
    grok.implements(IUserTicketsWidget)

    title = _(u'My tickets')
    amount = schema.fieldproperty.FieldProperty(IUserTicketsWidget['amount'])


class UserTicketsWidgetIndex(user.Index):
    """ The view of the user tickets widget
    """
    grok.context(IUserTicketsWidget)
    grok.require('horae.View')
    grok.name('index')

    def __init__(self, context, request):
        self.widget = context
        super(UserTicketsWidgetIndex, self).__init__(getUser(request.principal.id), request)

    def searchArguments(self, table=None):
        args = super(UserTicketsWidgetIndex, self).searchArguments(table)
        args['limit'] = self.widget.amount
        return args

    def createTable(self):
        table = super(UserTicketsWidgetIndex, self).createTable()
        if table is not None:
            table.filterable = {}
            table.sortable = None
            columns = ('id', 'name', 'workflow', 'execution',)
            if self.widget.width >= 8:
                columns += ('client', 'project',)
            if self.widget.width >= 12:
                columns += ('milestone', 'modified',)
            table.columns = [(name, title) for name, title in table.columns if name in columns]
        return table

    def filterable(self):
        return {}

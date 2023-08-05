import grok
import simplejson

try:
    from datetime import datetime, date, timedelta
    from zope import interface
    from zope import component
    from zope import schema
    from zope.schema import vocabulary
    from zope.traversing.interfaces import ITraversable
    from zope.site.hooks import getSite
    from zope.i18n import translate

    from horae.core.utils import formatDateTimeRange
    from horae.layout.interfaces import IViewExtender
    from horae.resources import interfaces
    from horae.resources import _ as _r
    from horae.timeaware import timeaware
    from horae.timeaware.interfaces import ITimeRange

    from horae.dashboard import _
    from horae.dashboard import dashboard
    from horae.dashboard import ticketing
    from horae.dashboard.interfaces import IWidget, IWidgetFactory

    class ExpenseTimeTrackingExtender(grok.Adapter):
        """ Extends the time tracking widget with a field to select the
            desired resource and cost unit
        """
        grok.context(ticketing.TimeTrackingWidgetIndex)
        grok.implements(IViewExtender)
        grok.name('horae.dashboard.resources.timetracking')

        def pre_update(self):
            registry = vocabulary.getVocabularyRegistry()
            if len(registry.get(self.context.context, 'horae.resources.vocabulary.resourcecostunit')):
                self.context.form_fields = self.context.form_fields + grok.AutoFields(interfaces.IWorkExpenseForm)
                self.context.form_fields['workexpense'].field.order = 110

        def pre_setUpWidgets(self, ignore_request=False):
            pass

        def post_update(self):
            if self.context.form_fields.get('workexpense') is not None:
                self.context.form_fields['workexpense'].field = self.context.form_fields['workexpense'].field.bind(self.context.context)
                resource = self.context.widgets['workexpense'].getInputValue() if self.context.widgets['workexpense'].hasInput() else None
                for term in self.context.form_fields['workexpense'].field.vocabulary:
                    if resource is None:
                        resource = term.value
                        self.context.widgets['workexpense'].setRenderedValue(term.value)
                    if resource.resource == term.value.resource and \
                       resource.resource.default_costunit == term.value.costunit:
                        self.context.widgets['workexpense'].setRenderedValue(term.value)
                    if term.value.resource.user is not None and self.context.request.principal.id == term.value.resource.user and \
                       term.value.costunit == term.value.resource.default_costunit:
                        self.context.widgets['workexpense'].setRenderedValue(term.value)
                        break

        def apply(self, obj, **data):
            form = interfaces.IWorkExpenseForm(obj)
            form.workexpense = data['workexpense']

        def validate(self, action, data):
            if not 'ticket' in data:
                return ()
            workexpense = data['workexpense']
            for planned_resource in interfaces.IPlannedResources(data['ticket']).objects():
                if planned_resource.resource.id == workexpense.resource.id and planned_resource.costunit.id == workexpense.costunit.id:
                    return ()
            return [interface.Invalid(_(u'Resource or cost unit not available for the given ticket')), ]

    class AvailableResources(grok.View):
        """ Helper view to get the available resources of a given
            ticket as JSON
        """
        grok.context(ticketing.ITimeTrackingWidget)
        grok.name('available-resources')

        def __call__(self, id):
            ticket = component.getMultiAdapter((getSite(), self.request), ITraversable, 'ticket').traverse(id, None)
            registry = vocabulary.getVocabularyRegistry()
            vocab = registry.get(ticket, 'horae.resources.vocabulary.resourcecostunit')
            return simplejson.dumps({'resources': [term.token for term in vocab],
                                     'id': id})

        def render(self):
            pass

    class IWorkTimeTrackingWidget(IWidget):
        """ Provides a form to track work time of a specified human resource
        """

    class WorkTimeTrackingWidgetFactory(grok.GlobalUtility):
        """ Work time tracking widget factory
        """
        grok.name('worktimetracking')
        grok.implements(IWidgetFactory)

        name = _(u'Work time tracking')
        schema = IWorkTimeTrackingWidget

        def __call__(self):
            """ Creates and returns a IWidget instance
            """
            return WorkTimeTrackingWidget()

    class WorkTimeTrackingWidget(dashboard.Widget):
        """ Provides a form to track work time of a specified human resource
        """
        grok.implements(IWorkTimeTrackingWidget)

        title = _(u'Work time tracking')
        resizable = False

    class IWorkTimeTrackingWidgetForm(ITimeRange):
        """ Simple form to track work time of a specified human resource
        """

        resource = schema.Choice(
            title=_r(u'Human resource'),
            vocabulary='horae.resources.vocabulary.currentusershumanresources'
        )

    class WorkTimeTrackingWidgetIndex(dashboard.Form):
        """ Simple form to track work time of a specified human resource
        """
        grok.context(IWorkTimeTrackingWidget)
        grok.name('index')

        @property
        def label(self):
            if self.resource is not None:
                return '<a href="%s">%s</a>' % (self.url(interfaces.IEffectiveWorkTime(self.resource)), translate(_(u'Work time tracking'), context=self.request))
            return _(u'Work time tracking')

        def append(self):
            if self.resource is None:
                return u''
            effectiveworktime = interfaces.IEffectiveWorkTime(self.resource)
            entries = []
            today = date.today()
            now = datetime(today.year, today.month, today.day)
            for entry in effectiveworktime.entries((now - timedelta(days=3), now + timedelta(days=1))):
                entries.insert(0, '<li>%s</li>' % formatDateTimeRange(entry.date_start, entry.date_end, self.request))
            if len(entries):
                return '<div class="pastentries"><h3>%s</h3><ul class="noMarker">%s</ul></div>' % (translate(_(u'Past 3 days'), context=self.request), ''.join(entries))
            return u''

        def update(self):
            self.form_fields = grok.AutoFields(IWorkTimeTrackingWidgetForm)
            self.resource = None
            registry = vocabulary.getVocabularyRegistry()
            vocab = registry.get(self.context, 'horae.resources.vocabulary.currentusershumanresources')
            if len(vocab) == 1:
                self.form_fields = self.form_fields.omit('resource')
                for term in vocab:
                    self.resource = term.value
            super(WorkTimeTrackingWidgetIndex, self).update()

        def setUpWidgets(self, ignore_request=False):
            super(WorkTimeTrackingWidgetIndex, self).setUpWidgets(ignore_request)
            if not self.widgets['date_start'].hasInput() or ignore_request:
                self.widgets['date_start'].setRenderedValue(datetime.now() - timedelta(hours=1))
            if not self.widgets['date_end'].hasInput() or ignore_request:
                self.widgets['date_end'].setRenderedValue(datetime.now())
            if self.resource is not None:
                effectiveworktime = interfaces.IEffectiveWorkTime(self.resource)
                today = date.today()
                now = datetime(today.year, today.month, today.day)
                worktime = interfaces.IPlannedWorkTime(self.resource).subtract(interfaces.IAbsence(self.resource), (now, now + timedelta(days=1)))
                for entry in worktime.objects():
                    if not len(effectiveworktime.entries((entry.date_start, entry.date_end))):
                        if not self.widgets['date_start'].hasInput() or ignore_request:
                            self.widgets['date_start'].setRenderedValue(entry.date_start)
                        if not self.widgets['date_end'].hasInput() or ignore_request:
                            self.widgets['date_end'].setRenderedValue(entry.date_end)
                        break

        @grok.action(_(u'Save'))
        def handle_save(self, **data):
            if 'resource' in data:
                self.resource = data['resource']
            effectiveworktime = interfaces.IEffectiveWorkTime(self.resource)
            entry = timeaware.PersistentTimeEntry()
            entry.date_start = data['date_start']
            entry.date_end = data['date_end']
            effectiveworktime.add_object(entry)
            self.status = _(u'Time successfully stored')
            self.statusCssClass = 'success'
            if 'resource' in data:
                self.resource = None

except ImportError: # horae.resources not available
    pass

import grok

try:
    from persistent.wref import WeakRef

    from zope import schema
    from zope.i18n import translate

    from horae.reports import _ as _r
    from horae.reports import views

    from horae.dashboard import _
    from horae.dashboard import dashboard
    from horae.dashboard.interfaces import IWidget, IWidgetFactory

    class IReportWidget(IWidget):
        """ A widget showing the results of a defined report
        """

        report = schema.Choice(
            title=_r(u'Report'),
            vocabulary='horae.reports.vocabulary.reports'
        )

        amount = schema.Int(
            title=_(u'Number of results to display'),
            default=10,
            min=1
        )

    class ReportWidgetFactory(grok.GlobalUtility):
        """ Report widget factory
        """
        grok.name('report')
        grok.implements(IWidgetFactory)

        name = _(u'Report')
        schema = IReportWidget

        def __call__(self):
            """ Creates and returns a IWidget instance
            """
            widget = ReportWidget()
            widget.width = 8
            return widget

    class ReportWidget(dashboard.Widget):
        """ A widget showing the results of a defined report
        """
        grok.implements(IReportWidget)

        title = _(u'Report')
        amount = schema.fieldproperty.FieldProperty(IReportWidget['amount'])
        resizable = True

        def get_report(self):
            try:
                return self._report()
            except:
                return None

        def set_report(self, report):
            self._report = WeakRef(report)
        report = property(get_report, set_report)

    class ReportWidgetIndex(views.Report):
        """ A widget showing the results of a defined report
        """
        grok.context(IReportWidget)
        grok.name('index')

        def __call__(self, plain=False, selector=None):
            try:
                report = self.context.report
                self.page_size = self.context.amount
                self.limit = self.context.amount
                self.widget, self.context = self.context, report
                return '<h1 class="firstHeading"><a href="%s">%s</a></h1>' % (self.url(self.context), self.context.name) + self.table()
            except:
                return translate(_(u'The selected report is no longer available'), context=self.request)

        def createTable(self):
            table = super(ReportWidgetIndex, self).createTable()
            if table is not None:
                table.filterable = {}
                table.sortable = None
                columns = ('id', 'name', 'type',)
                if self.widget.width >= 8:
                    columns += ('modifier', 'modification_date',)
                if self.widget.width >= 12:
                    columns += ('workflow', 'execution',)
                table.columns = [(name, title) for name, title in table.columns if name in columns]
            return table

except ImportError: # horae.reports not available
    pass

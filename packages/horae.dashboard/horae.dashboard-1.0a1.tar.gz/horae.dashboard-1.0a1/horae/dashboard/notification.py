import grok

try:
    from zope import schema
    from zope.site.hooks import getSite
    from zope.i18n import translate

    from horae.notification import views
    from horae.notification import _ as _n

    from horae.dashboard import interfaces
    from horae.dashboard import dashboard
    from horae.dashboard import _

    class INotificationsWidget(interfaces.IWidget):
        """ Provides a widget showing the latest notifications
        """

        amount = schema.Int(
            title=_(u'Number of notifications to display'),
            default=10,
            min=1,
        )

    class NotificationsWidgetFactory(grok.GlobalUtility):
        """ Notifications widget factory
        """
        grok.name('notifications')
        grok.implements(interfaces.IWidgetFactory)

        name = _n(u'Notifications')
        schema = INotificationsWidget

        def __call__(self):
            """ Creates and returns a IWidget instance
            """
            return NotificationsWidget()

    class NotificationsWidget(dashboard.Widget):
        """ A widget providing a simple form to track time on tickets
        """
        grok.implements(INotificationsWidget)

        title = _n(u'Notifications')
        amount = schema.fieldproperty.FieldProperty(INotificationsWidget['amount'])

    class NotificationsWidgetIndex(views.Notifications):
        grok.context(INotificationsWidget)
        grok.require('horae.View')
        grok.name('index')

        def __call__(self, plain=False, selector=None):
            return '<h1 class="firstHeading"><a href="%s">%s</a></h1>' % (self.url(getSite(), 'view-notifications'), translate(_n(u'Notifications'), context=self.request)) + \
                    super(NotificationsWidgetIndex, self).__call__(plain=True, selector=selector)

        def set(self, value):
            pass

        def get_amount(self):
            return self.context.amount
        amount = property(get_amount, set)

        def get_simple(self):
            return True
        simple = property(get_simple, set)

        def get_header(self):
            return False
        header = property(get_header, set)

        def get_buttons(self):
            return False
        buttons = property(get_buttons, set)

except ImportError: # horae.notification not available
    pass

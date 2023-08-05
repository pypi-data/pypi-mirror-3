from zope import interface
from zope import schema

from horae.core import interfaces

from horae.dashboard import _


class IDashboards(interfaces.IContainer):
    """ A container for dashboards
    """


class IGroupDashboards(IDashboards):
    """ A container for group dashboards
    """


class IUserDashboards(IDashboards):
    """ A container for user dashboards
    """


class IDashboard(interfaces.ITextId, interfaces.IContainer):
    """ A dashboard
    """


class IGroupDashboard(IDashboard):
    """ A group dashboard
    """


class IWidgetFactory(interface.Interface):
    """ A widget factory
    """

    name = interface.Attribute('name', '''The name of the widget type''')
    schema = interface.Attribute('schema', '''The schema of the widget type''')

    def __call__():
        """ Creates and returns an :py:class:`IWidget` instance
        """


class IWidget(interfaces.IIntId):
    """ A widget
    """

    factory = interface.Attribute('factory', '''The name of :py:class:`IWidgetFactory` creating this widget''')
    title = interface.Attribute('title', '''The title of the widget''')
    resizable = interface.Attribute('resizable', '''Whether this widget is resizeable or not''')

    width = schema.Int(
        title=u'The width of the widget',
        default=4,
        min=2,
        max=16
    )
    height = schema.Int(
        title=u'The height of the widget',
        default=300,
        min=100,
        required=False
    )
    sidebar = schema.Bool(
        title=_(u'Show widget in sidebar'),
        default=False
    )

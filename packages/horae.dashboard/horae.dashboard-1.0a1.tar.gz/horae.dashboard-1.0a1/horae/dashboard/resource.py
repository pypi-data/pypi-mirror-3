import grok

from zope.interface import Interface
from fanstatic import Library, Resource

from js import jqueryui

from horae.core.utils import getRequest
from horae.autocomplete.resource import css, js
from horae.layout import interfaces
from horae.layout import resource
from horae.datetime import resource as datetime

library = Library('horae.dashboard', 'static')

style = Resource(library, 'dashboard.css')
script = Resource(library, 'dashboard.js', depends=[jqueryui.jqueryui, jqueryui.smoothness, resource.initialization])

ticketing = Resource(library, 'ticketing.js', [script, css, js, datetime.spinbox, datetime.css, datetime.js])
notification = Resource(library, 'notification.js')


@grok.adapter(Interface, name='horae.dashboard')
@grok.implementer(interfaces.IResourceProvider)
def dashboard_resource_provider(context):
    """ Provides CSS and JavaScript resources needed for the
        horae.dashboard package
    """
    request = getRequest(None)
    resources = [style, script, ticketing, notification]
    if request is not None:
        jqueryui_i18n = datetime.jqueryui_i18n(request)
        if jqueryui_i18n is not None:
            resources.insert(0, jqueryui_i18n)
    return resources

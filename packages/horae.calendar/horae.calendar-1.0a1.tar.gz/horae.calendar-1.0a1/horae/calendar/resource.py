import grok

from zope.interface import Interface
from fanstatic import Library, Resource

from js.jquery import jquery

from horae.layout import interfaces
from horae.layout import resource

library = Library('horae.calendar', 'static')

style = Resource(library, 'calendar.css')
script = Resource(library, 'calendar.js', depends=[jquery, resource.initialization, ])


@grok.adapter(Interface, name='horae.calendar')
@grok.implementer(interfaces.IResourceProvider)
def calendar_resource_provider(context):
    """ Provides CSS and JavaScript resources needed for the
        horae.calendar package
    """
    return [style, script, ]

import grok

from zope.interface import Interface
from fanstatic import Library, Resource

from js.jquery import jquery

from horae.layout import interfaces
from horae.layout import resource

library = Library('horae.notification', 'static')

style = Resource(library, 'notification.css')
script = Resource(library, 'notification.js', depends=[jquery, resource.initialization])


@grok.adapter(Interface, name='horae.notification')
@grok.implementer(interfaces.IResourceProvider)
def notification_resource_provider(context):
    """ Provides the CSS and JavaScript resources needed for the
        horae.notification package
    """
    return [style, script]

import grok

from zope.interface import Interface
from zope.site.hooks import getSite

from horae.layout import layout
from horae.layout.viewlets import TopManager

from horae.notification import interfaces
from horae.notification import _

grok.templatedir('viewlet_templates')
grok.context(Interface)

MAX_NOTIFICATIONS = 15


class Notifications(layout.Viewlet):
    """ Renders the number of unread notifications
    """
    grok.viewletmanager(TopManager)
    grok.order(20)
    grok.require('zope.View')

    def update(self):
        notifications = interfaces.INotifications(self.context)
        self.url = grok.url(self.request, getSite()) + '/@@view-notifications'
        self.unread = notifications.unread()
        if self.unread > 1:
            self.message = _(u'${number} new notifications', mapping={'number': self.unread})
        elif self.unread > 0:
            self.message = _(u'New notification')
        else:
            self.message = _(u'No new notifications')

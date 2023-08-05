import grok
import json

from zope.i18n import translate
from zope.session.interfaces import ISession

from megrok import navigation

from horae.core import utils
from horae.core.interfaces import IHorae
from horae.auth.interfaces import IUserURL
from horae.layout import layout
from horae.layout.interfaces import IGlobalManageMenu

from horae.notification import _
from horae.notification import interfaces

grok.templatedir('templates')


class NotificationConfiguration(layout.EditForm):
    """ Form to edit the notification configuration defined by
        :py:class:`horae.notification.interfaces.INotificationConfiguration`
    """
    grok.context(IHorae)
    grok.require('horae.Manage')
    grok.name('configure-notification')
    navigation.sitemenuitem(IGlobalManageMenu, _(u'Notification configuration'), order=10)

    label = _(u'Notification configuration')
    form_fields = grok.AutoFields(interfaces.INotificationConfiguration)


class Notifications(layout.View):
    """ Renders the available notifications of the current user
    """
    grok.context(IHorae)
    grok.require('zope.View')
    grok.name('view-notifications')

    amount = 25
    start = None
    session_key = 'horae.notification.notifications'

    def __call__(self, amount=None, start=None, read=None, unread=None, mark_all_read=False, show=None, ajax=False, plain=False, selector=None):
        self.simple = ajax
        self.ajax = ajax
        self.header = not ajax
        self.buttons = not ajax
        self.show = None
        self._notifications = interfaces.INotifications(self.context)
        if ajax == 'unread':
            return self.unread_count()
        if show is not None:
            return self.show_body(show, ajax)
        if read is not None:
            return self.read(read, ajax)
        if unread is not None:
            return self.unread(unread, ajax)
        if mark_all_read:
            return self.mark_all_read(ajax)
        session = ISession(self.request)
        if 'amount' in session[self.session_key]:
            self.amount = session[self.session_key]['amount']
        if start is not None:
            try:
                self.start = int(start)
            except:
                pass
        if amount is not None:
            try:
                self.amount = int(amount)
                if ajax and not ajax == 'simple':
                    self.update()
                    self.simple = False
                    return json.dumps({'has_more': self.has_more,
                                       'entries': super(Notifications, self).__call__(ajax)})
                if not ajax:
                    session[self.session_key]['amount'] = self.amount
            except:
                pass
        return super(Notifications, self).__call__(ajax or plain, selector)

    def show_body(self, id, ajax=False):
        try:
            self.show = int(id)
        except:
            self.show = None
        if ajax:
            notification = self._notifications.get_object(self.show)
            if notification is not None:
                return json.dumps({'label': translate(_(u'Hide information'), context=self.request),
                                   'body': notification.body(self.request)})
            else:
                return u''
        return self()

    def read(self, id, ajax=False, unread=False):
        notification = self._notifications.get_object(id)
        if notification is not None:
            if unread:
                self._notifications.mark_unread(notification)
            else:
                self._notifications.mark_read(notification)
            if ajax:
                return json.dumps({'label': translate(_(u'Mark as unread') if not unread else _(u'Mark as read'), context=self.request),
                                   'url': self.url() + '?' + ('unread' if not unread else 'read') + '=' + id})
        return self()

    def unread(self, id, ajax=False):
        return self.read(id, ajax, True)

    def mark_all_read(self, ajax=False):
        self._notifications.mark_all_read()
        if ajax:
            return json.dumps({'label': translate(_(u'Mark as unread'), context=self.request)})

    def unread_count(self):
        unread = self._notifications.unread()
        if unread > 1:
            message = _(u'${number} new notifications', mapping={'number': unread})
        elif unread > 0:
            message = _(u'New notification')
        else:
            message = _(u'No new notifications')
        return json.dumps({'unread': unread,
                           'message': translate(message, context=self.request)})

    def update(self):
        self.notifications = []
        self.has_more = False
        for notification, unread in self._notifications.notifications():
            if self.start is not None and notification.id >= self.start:
                continue
            if len(self.notifications) > self.amount:
                self.has_more = True
                break
            user = notification.user()
            user_url = None
            if user is not None:
                user_url = IUserURL(user, lambda: None)()
                user = user.name
            else:
                user = notification.username
            self.notifications.append({'notification': notification,
                                       'unread': unread,
                                       'cssClass': notification.cssClass + (' unread' if unread else ''),
                                       'url': notification.url(self.request),
                                       'title': notification.title(self.request),
                                       'body': notification.body(self.request),
                                       'show': self.show == notification.id,
                                       'user': user,
                                       'user_url': user_url,
                                       'date': utils.formatDateTime(notification.date, self.request)})

import grok
from datetime import datetime

from persistent.dict import PersistentDict
from persistent.list import PersistentList
from persistent.wref import WeakRef
from BTrees.IOBTree import IOBTree

from zope import interface
from zope import component
from zope import schema
from zope.site.hooks import getSite
from zope.annotation.interfaces import IAnnotations
from zope.sendmail.mailer import SMTPMailer
from zope.security import checkPermission

from horae.core import container
from horae.core import utils
from horae.auth.utils import getUser
from horae.subscription.interfaces import ISubscription

from horae.notification import _
from horae.notification import interfaces


class Notifications(container.Container):
    """ A container for notifications
    """
    grok.implements(interfaces.INotifications)

    def __init__(self):
        super(Notifications, self).__init__()
        self._read = IOBTree()

    def id_key(self):
        return 'notification'

    def add_object(self, obj):
        """ Adds a new object and returns the generated id
        """
        id = super(Notifications, self).add_object(obj)
        self.updateOrder([str(id), ] + [k for k in self.keys() if not k == str(id)])
        return id

    def notifications(self):
        """ Iterator of notification, unread tuples available for the current user
        """
        principal = utils.getPrincipal()
        for notification in self.objects():
            if not notification.available():
                continue
            if notification.context is not None and notification.permission is not None and not checkPermission(notification.permission, notification.context):
                continue
            unread = principal is not None and (not notification.id in self._read or not principal.id in self._read[notification.id])
            yield notification, unread

    def mark_read(self, notification):
        """ Mark the notification as read for the current user
        """
        principal = utils.getPrincipal()
        if principal is None:
            return
        if not notification.id in self._read:
            self._read[notification.id] = PersistentList()
        if not principal.id in self._read[notification.id]:
            self._read[notification.id].append(principal.id)

    def mark_all_read(self):
        """ Mark all notifications of the current user as read
        """
        principal = utils.getPrincipal()
        if principal is None:
            return
        for id in self.keys():
            if not int(id) in self._read:
                self._read[int(id)] = PersistentList()
            if not principal.id in self._read[int(id)]:
                self._read[int(id)].append(principal.id)

    def mark_unread(self, notification):
        """ Mark the notification as unread for the current user
        """
        principal = utils.getPrincipal()
        if principal is None:
            return
        if not notification.id in self._read:
            return
        if principal.id in self._read[notification.id]:
            self._read[notification.id].remove(principal.id)

    def unread(self):
        """ Number of unread notifications for the current user
        """
        principal = utils.getPrincipal()
        if principal is None:
            return 0
        number = 0
        for id in self.keys():
            if int(id) in self._read and principal.id in self._read[int(id)]:
                continue
            notification = self.get_object(id)
            if not notification.available():
                continue
            if notification.context is not None and notification.permission is not None and not checkPermission(notification.permission, notification.context):
                continue
            number += 1
        return number


class Notification(grok.Model):
    """ A notification
    """
    grok.implements(interfaces.INotification)
    grok.baseclass()

    id = schema.fieldproperty.FieldProperty(interfaces.INotification['id'])
    date = None
    username = None
    permission = 'horae.View'
    _context = None
    cssClass = u''

    def __init__(self, context):
        super(Notification, self).__init__()
        self._context = WeakRef(context)
        try:
            self.username = utils.getRequest().principal.id
        except:
            pass
        self.date = datetime.now()

    @property
    def context(self):
        try:
            return self._context()
        except:
            return None

    def user(self):
        """ Returns the user or None
        """
        if self.username is None:
            return None
        return getUser(self.username)

    def title(self, request):
        """ Returns the notification title
        """
        raise NotImplementedError(u'concrete classes must implement title()')

    def body(self, request):
        """ Returns the notification body
        """
        raise NotImplementedError(u'concrete classes must implement body()')

    def available(self):
        """ Whether this notification is available
        """
        return True

    def url(self, request):
        """ Returns the url to be used for the notification
        """
        return grok.url(request, self.context)


class TicketModifiedNotification(Notification):
    """ A notification about a ticket modification
    """
    grok.implements(interfaces.ITicketModifiedNotification)

    message = None

    def title(self, request):
        """ Returns the notification title
        """
        return _(u'Ticket #${no} changed', mapping={'no': self.context.id})

    def body(self, request):
        """ Returns the notification body
        """
        return self.message

    def available(self):
        """ Whether this notification is available
        """
        principal = utils.getPrincipal()
        if principal is None or self.context is None:
            return False
        if principal.id == self.username:
            return False
        for subscription in ISubscription(self.context).subscribers():
            if interfaces.IUserSubscriber.providedBy(subscription):
                if subscription.user.username == principal.id:
                    return True
            elif interfaces.IGroupSubscriber.providedBy(subscription):
                if subscription.group.id in principal.groups:
                    return True
        return False


@grok.adapter(interface.Interface)
@grok.implementer(interfaces.INotifications)
def notifications(obj):
    """ Adapter providing the container notifications
    """
    site = getSite()
    if not 'notifications' in site:
        site['notifications'] = Notifications()
    return site['notifications']

ANNOTATIONS_KEY = 'horae.notification'


@grok.adapter(interface.Interface)
@grok.implementer(interfaces.INotificationConfiguration)
def notification_configuration(context):
    """ Adapter providing the notification configuration
    """
    return component.getUtility(interfaces.INotificationConfiguration, name='horae.notification')


class NotificationConfiguration(grok.GlobalUtility, SMTPMailer):
    """ The notification configuration
    """
    grok.implements(interfaces.INotificationConfiguration)
    grok.provides(interfaces.INotificationConfiguration)
    grok.name('horae.notification')

    _v_storage = None

    def __init__(self):
        super(NotificationConfiguration, self).__init__()
        self._v_storage = None

    @property
    def storage(self):
        if self._v_storage is None:
            config = getSite()
            if config is None:
                return {}
            annotations = IAnnotations(config)
            if not ANNOTATIONS_KEY in annotations:
                annotations[ANNOTATIONS_KEY] = PersistentDict()
            self._v_storage = annotations[ANNOTATIONS_KEY]
        return self._v_storage

    def get_hostname(self):
        return self.storage.get('hostname', u'localhost')

    def set_hostname(self, value):
        self.storage['hostname'] = value
    hostname = property(get_hostname, set_hostname)

    def get_port(self):
        return self.storage.get('port', 25)

    def set_port(self, value):
        self.storage['port'] = value
    port = property(get_port, set_port)

    def get_username(self):
        return self.storage.get('username', None)

    def set_username(self, value):
        self.storage['username'] = value
    username = property(get_username, set_username)

    def get_password(self):
        return self.storage.get('password', None)

    def set_password(self, value):
        self.storage['password'] = value
    password = property(get_password, set_password)

    def get_no_tls(self):
        return self.storage.get('no_tls', None)

    def set_no_tls(self, value):
        self.storage['no_tls'] = value
    no_tls = property(get_no_tls, set_no_tls)

    def get_force_tls(self):
        return self.storage.get('force_tls', None)

    def set_force_tls(self, value):
        self.storage['force_tls'] = value
    force_tls = property(get_force_tls, set_force_tls)

    def get_email_from_name(self):
        return self.storage.get('email_from_name', None)

    def set_email_from_name(self, value):
        self.storage['email_from_name'] = value
    email_from_name = property(get_email_from_name, set_email_from_name)

    def get_email_from_address(self):
        return self.storage.get('email_from_address', None)

    def set_email_from_address(self, value):
        self.storage['email_from_address'] = value
    email_from_address = property(get_email_from_address, set_email_from_address)

    def get_pandoc_path(self):
        return self.storage.get('pandoc_path', None)

    def set_pandoc_path(self, value):
        self.storage['pandoc_path'] = value
    pandoc_path = property(get_pandoc_path, set_pandoc_path)

    def get_email_admin(self):
        return self.storage.get('email_admin', None)

    def set_email_admin(self, value):
        self.storage['email_admin'] = value
    email_admin = property(get_email_admin, set_email_admin)

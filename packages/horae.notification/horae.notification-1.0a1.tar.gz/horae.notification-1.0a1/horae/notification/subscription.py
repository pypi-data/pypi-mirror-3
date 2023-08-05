import grok
import email
from BeautifulSoup import BeautifulSoup
from pandoc import core as pandoc

from logging import getLogger

from zope import component
from zope.i18n import translate
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.authentication.interfaces import IUnauthenticatedPrincipal
from zope.security.interfaces import IMemberGetterGroup
from zope.sendmail.interfaces import IMailDelivery

from horae.core.utils import getRequest
from horae.auth import utils
from horae.auth.interfaces import IUser, IGroup, IUserURL
from horae.ticketing.interfaces import ITicket, ITicketChangedEvent
from horae.subscription.interfaces import ISubscriber, ISubscription, IMessage

from horae.notification import _
from horae.notification import interfaces
from horae.notification.notification import TicketModifiedNotification

logger = getLogger('horae.subscription')


@grok.subscribe(ITicket, grok.IObjectModifiedEvent)
def subscribe_modifier_to_ticket(ticket, event):
    """ Subscribes the modifier of a ticket after a ticket has been modified
    """
    if grok.IContainerModifiedEvent.providedBy(event):
        return
    try:
        request = getRequest()
    except:
        return
    if request is None:
        return
    modifier = utils.getUser(request.principal.id)
    if modifier is None:
        return
    subscriber = ISubscriber(modifier)
    if subscriber is None:
        return
    subscription = ISubscription(ticket)
    subscription.subscribe(subscriber)
    subscriber.context = ticket


@grok.subscribe(ITicket, grok.IObjectModifiedEvent)
def subscribe_responsible_to_ticket(ticket, event):
    """ Subscribes the responsible of a ticket after a ticket has been modified
    """
    if grok.IContainerModifiedEvent.providedBy(event):
        return
    subscription = ISubscription(ticket)
    responsible = utils.getUser(ticket.get_property('responsible', None))
    if responsible is None:
        return
    subscriber = ISubscriber(responsible)
    if subscriber is None:
        return
    subscription = ISubscription(ticket)
    subscription.subscribe(subscriber)
    subscriber.context = ticket


@grok.subscribe(ITicket, ITicketChangedEvent)
def notify_subscribers(ticket, event):
    """ Notifies all registered subscribers after a ticket has been modified
    """
    try:
        message = component.getMultiAdapter((event, getRequest()), interface=IMessage)
    except:
        return
    subscription = ISubscription(ticket)

    notifications = interfaces.INotifications(ticket)
    notification = TicketModifiedNotification(ticket)
    notification.message = message.message(True)
    notifications.add_object(notification)

    if component.getUtility(interfaces.INotificationConfiguration, name=u'horae.notification').pandoc_path is None:
        return
    subscription.subscribe(admin_subscriber)
    subscription.notify(message)
    subscription.unsubscribe(admin_subscriber)


class BaseSubscriber(grok.Model):
    """ Base implementation of a subscriber
    """

    def notify(self, message, subject):
        """ Sends the message to the subscriber
        """
        try:
            configuration = component.getUtility(interfaces.INotificationConfiguration, name='horae.notification')
            mailer = component.getUtility(IMailDelivery, 'horae.notification.mailer')
            msg = email.MIMEText.MIMEText(message.encode('UTF-8'), 'plain', 'UTF-8')
            msg["From"] = email.utils.formataddr((configuration.email_from_name, configuration.email_from_address))
            msg["Reply-to"] = email.utils.formataddr((configuration.email_from_name, configuration.email_from_address))
            msg["To"] = ';'.join([email.utils.formataddr((self.name, address)) for address in self.emails])
            msg["Subject"] = email.Header.Header(subject, 'UTF-8')
            mailer.send(configuration.email_from_address, self.emails, msg.as_string())
        except:
            logger.error('Sending notification "%s" to "%s" failed' % (subject, ', '.join([address for address in self.emails])))


class AdminSubscriber(BaseSubscriber):
    """ Admin subscriber sending notifications to the email address
        configured in :py:class:`horae.notification.interfaces.INotificationConfiguration`
    """
    grok.implements(ISubscriber)

    id = 'horae.notification.admin'
    name = 'Horae admin'
    url = None

    @property
    def emails(self):
        configuration = component.getUtility(interfaces.INotificationConfiguration, name='horae.notification')
        if configuration.email_admin is None:
            return []
        return configuration.email_admin.split(';')

    def available(self, context):
        return len(self.emails)

admin_subscriber = AdminSubscriber()


class UserSubscriber(BaseSubscriber):
    """ A user subscriber
    """
    grok.implements(interfaces.IUserSubscriber)

    display = True
    username = None

    def __init__(self, user):
        super(UserSubscriber, self).__init__()
        self.user = user
        self.id = user.username
        self.name = user.name

    @property
    def emails(self):
        return [self.user.email, ]

    @property
    def url(self):
        return IUserURL(self.user, lambda: None)()

    def set_user(self, user):
        self.username = user.username

    def get_user(self):
        return utils.getUser(self.username)
    user = property(get_user, set_user)

    def available(self, context):
        return self.user is not None and utils.checkPermissionForPrincipal('horae.View', context, self.user.username)


class GroupSubscriber(BaseSubscriber):
    """ A group subscriber
    """
    grok.implements(interfaces.IGroupSubscriber)

    display = True
    groupid = None

    def __init__(self, group):
        super(GroupSubscriber, self).__init__()
        self.id = group.id
        self.name = group.name
        self.group = group

    @property
    def emails(self):
        members = IMemberGetterGroup(self.group).getMembers()
        return [member.email for member in members]

    @property
    def url(self):
        return None

    def set_group(self, group):
        self.groupid = group.id

    def get_group(self):
        return utils.getGroup(self.groupid)
    group = property(get_group, set_group)

    def available(self, context):
        return self.group is not None and utils.checkPermissionForPrincipal('horae.View', context, self.group.id)


@grok.adapter(IBrowserRequest)
@grok.implementer(ISubscriber)
def current_user_subscriber(request):
    """ Adapter returning an :py:class:`horae.subscription.interface.ISubscriber`
        object of the current user
    """
    loggedin = not IUnauthenticatedPrincipal.providedBy(request.principal)
    if not loggedin:
        return None
    user = utils.getUser(request.principal.id)
    if user is None:
        return None
    return ISubscriber(user)


@grok.adapter(IUser)
@grok.implementer(ISubscriber)
def user_subscriber(user):
    """ Adapter returning an :py:class:`horae.subscription.interface.ISubscriber`
        object of the adapted user
    """
    return UserSubscriber(user)


@grok.adapter(IGroup)
@grok.implementer(ISubscriber)
def group_subscriber(group):
    """ Adapter returning an :py:class:`horae.subscription.interface.ISubscriber`
        object of the adapted group
    """
    return GroupSubscriber(group)


class TicketChangeMessage(grok.MultiAdapter):
    """ Factory for messages about a ticket change
    """
    grok.implements(IMessage)
    grok.adapts(ITicketChangedEvent, IBrowserRequest)

    def __init__(self, event, request):
        self.event = event
        self.request = request

    def subject(self):
        """ Returns the subject of the notification to be sent
        """
        return translate(_(u'Ticket #${no} changed', mapping={'no': self.event.object.id}), context=self.request)

    def message(self, html=False):
        """ Returns the notification message to be sent
        """
        try:
            soup = BeautifulSoup(component.getMultiAdapter((self.event.object, self.request), name=u'index')(plain=True, form=False, change=self.event.change, previous=self.event.previous).encode('utf-8'))
            source = soup.find('div', id='content').renderContents()
            if html:
                return source.decode('utf-8')
            pandoc.PANDOC_PATH = component.getUtility(interfaces.INotificationConfiguration, name=u'horae.notification').pandoc_path
            doc = pandoc.Document()
            doc.html = source
            return doc.rst.decode('utf-8')
        except:
            logger.error('Failed to create notification message for ticket #%s using pandoc at "%s"' % (self.event.object.id, pandoc.PANDOC_PATH))
            return None

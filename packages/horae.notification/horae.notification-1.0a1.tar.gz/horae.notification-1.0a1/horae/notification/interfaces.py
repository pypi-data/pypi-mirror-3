from zope import interface, schema
from zope.sendmail.interfaces import ISMTPMailer, _ as _z
from megrok.form.fields import Email

from horae.core.interfaces import IContainer, IIntId
from horae.subscription.interfaces import ISubscriber

from horae.notification import _


class INotifications(IContainer):
    """ A container for notifications
    """

    def notifications():
        """ Iterator of notification, unread tuples available for the current user
        """

    def mark_read(notification):
        """ Mark the notification as read for the current user
        """

    def mark_all_read():
        """ Mark all notifications of the current user as read
        """

    def mark_unread(notification):
        """ Mark the notification as unread for the current user
        """

    def unread():
        """ Number of unread notifications for the current user
        """


class INotification(IIntId):
    """ A notification
    """

    date = interface.Attribute('date', 'The date this notification was issued')
    username = interface.Attribute('username', 'The username of the notification issuer')
    permission = interface.Attribute('permission', 'The permission required to view this notification')
    context = interface.Attribute('context', 'The context of this notification')
    cssClass = interface.Attribute('cssClass', 'The cssClass to be added')

    def user():
        """ Returns the user or None
        """

    def title(request):
        """ Returns the notification title
        """

    def body(request):
        """ Returns the notification body
        """

    def available():
        """ Whether this notification is available
        """

    def url(request):
        """ Returns the url to be used for the notification
        """


class ITicketModifiedNotification(INotification):
    """ A notification about a ticket modification
    """

    message = interface.Attribute('message', 'The message')


class INotificationConfiguration(ISMTPMailer):
    """ Configuration used for sending notifications
    """

    username = schema.TextLine(
        title=_z(u"Username"),
        description=_z(u"Username used for optional SMTP authentication."),
        required=False
    )

    password = schema.Password(
        title=_z(u"Password"),
        description=_z(u"Password used for optional SMTP authentication."),
        required=False
    )

    email_from_name = schema.TextLine(
        title=_(u"Email 'From' name"),
        default=None,
        required=True
    )

    email_from_address = Email(
        title=_(u"Email 'From' address"),
        default=None,
        required=True
    )

    pandoc_path = schema.TextLine(
        title=_(u"Path to pandoc executeable"),
        default=u'/usr/bin/pandoc',
        required=True
    )

    email_admin = Email(
        title=_(u'Email admin'),
        description=_(u'All notifications are additionally sent to this email'),
        required=False
    )


class IUserSubscriber(ISubscriber):
    """ A user subscriber
    """

    user = schema.Choice(
        title=_(u'The associated user'),
        required=True,
        vocabulary='horae.auth.vocabulary.users'
    )


class IGroupSubscriber(ISubscriber):
    """ A group subscriber
    """

    group = schema.Choice(
        title=_(u'The associated group'),
        required=True,
        vocabulary='horae.auth.vocabulary.groups'
    )

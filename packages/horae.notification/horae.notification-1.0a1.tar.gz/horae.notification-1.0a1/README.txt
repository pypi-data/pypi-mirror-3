Introduction
============

``horae.notification`` provides persistent and email notifications
for the Horae resource planning system.

Persistent notifications
========================

Persistent notifications are displayed by a viewlet and a corresponding
view. They are issued by adding new notifications (implementing
``horae.notification.interfaces.INotification`` to the notifications
adapter registered for the interface ``horae.notification.interfaces.INotifications``.
Examples may be found in ``horae.notification.subscription`` and
``horae.planning.notification``.

Email notifications
===================

Email notifications are handled by using the `horae.subscription
<http://pypi.python.org/pypi/horae.subscription>`_ package and  are sent
out to all subscribers of a ticket after it has changed.

Dependencies
============

Horae
-----

* `horae.auth <http://pypi.python.org/pypi/horae.auth>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.subscription <http://pypi.python.org/pypi/horae.subscription>`_
* `horae.ticketing <http://pypi.python.org/pypi/horae.ticketing>`_

Third party
-----------

* `pyandoc <http://pypi.python.org/pypi/pyandoc>`_
* `zope.sendmail <http://pypi.python.org/pypi/zope.sendmail>`_

System
------

``horae.notification`` requires `Pandoc <http://johnmacfarlane.net/pandoc>`_
a universal document converter to convert from HTML to reStructeredText
to send the email notifications. Installation instructions for Pandoc may be
found online at http://johnmacfarlane.net/pandoc/installing.html.

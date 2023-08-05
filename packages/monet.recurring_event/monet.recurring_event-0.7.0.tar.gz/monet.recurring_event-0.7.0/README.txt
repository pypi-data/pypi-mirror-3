Do not use
==========

An old and **deprecated** dependency for `monet.calendar.event`__ and the `Monet Calendar`__ suite.

__ http://pypi.python.org/pypi/monet.calendar.event
__ http://plone.org/products/monet.calendar.star

For sure you don't need this package!

.. Note::
   Starting from monet.calendar.event 0.4.0 you *don't* need this package anymore.
   
   Add this package to your buildout only if you used an older version of ``monet.calendar.event``;
   unluckily we can't remove easily this dependency in old sites.

Error fixed
-----------

Install this package only if, reinstalling a Monet Calendar component, you get an error like this::

    Traceback (innermost last):
      Module ZPublisher.Publish, line 125, in publish
      Module Zope2.App.startup, line 238, in commit
      Module transaction._manager, line 96, in commit
      Module transaction._transaction, line 395, in commit
      Module transaction._transaction, line 495, in _commitResources
      Module ZODB.Connection, line 510, in commit
      Module ZODB.Connection, line 555, in _commit
      Module ZODB.Connection, line 582, in _store_objects
      Module ZODB.serialize, line 407, in serialize
      Module ZODB.serialize, line 416, in _dump
    PicklingError: Can't pickle <class 'monet.recurring_event.interfaces.IMonetRecurringEventLayer'>: import of module monet.recurring_event.interfaces failed


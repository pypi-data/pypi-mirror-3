Introduction
============

The ``horae.calendar`` package provides a generic calendar view having a
month, week and day perspective for the Horae resource planning system.

Usage
=====

The calendar is available on every context as a view named ``calendar``.
The entries to be displayed by the calendar are taken from all the adapters
implementing ``horae.calendar.interfaces.ICalendarEntries`` and adapting
the context the view is currently viewed on. An example implementation
can be found in the `horae.planning <http://pypi.python.org/pypi/horae.planning>`_
package.

Dependencies
============

Horae
-----

* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `fanstatic <http://pypi.python.org/pypi/fanstatic>`_
* `zope.fanstatic <http://pypi.python.org/pypi/zope.fanstatic>`_

Introduction
============

``horae.resources`` provides resource management functionality for the
Horae resource planning system which includes:

* Global cost units
* Global resources
  
  * Human resources
  * One time resources
  * Hourly resources
  
* Defining the planned work time for human resources
* Defining absences for human resources
* Tracking of effective work time for human resources
* Planning human resources and the corresponding cost unit for tickets
* Association of time booked on a ticket with a planned resource
  (human resource and cost unit)
* Enter one time and hourly expenses on tickets
* Canceling previously entered expenses on tickets

Cost units
==========

Cost units are simple definitions of types of work that may be done and
consist of a name and an hourly rate.

Resources
=========

For every resource one may define what users or groups are allowed to
enter expenses of this resource. Following the three types of resources
are shortly explained.

Human resources
---------------

Human resources consist of a name, a defined set of cost units and are
linked with a user of the system. Additionally every human resource
holds its planned work time, absences and effective work time.

One time resources
------------------

One time resources are categories for one time expenses booked on tickets.
They only consist of a name. In an IT-company **Software**, **Hardware**
and **Licence** may be useful one time resources.

Hourly resources
----------------

Hourly resources are the possibly least used resources. They consist of a
name and an hourly rate. They may later be entered on a ticket in combination
with a time range as an hourly expense. A possible use case for hourly resources
may arise for example in a manufacturing company where a used machine has an
hourly cost which one would like to have entered on a ticket.

Dependencies
============

Horae
-----

* `horae.auth <http://pypi.python.org/pypi/horae.auth>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.groupselect <http://pypi.python.org/pypi/horae.groupselect>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.properties <http://pypi.python.org/pypi/horae.properties>`_
* `horae.ticketing <http://pypi.python.org/pypi/horae.ticketing>`_
* `horae.timeaware <http://pypi.python.org/pypi/horae.timeaware>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `z3c.relationfield <http://pypi.python.org/pypi/z3c.relationfield>`_
* `hurry.query <http://pypi.python.org/pypi/hurry.query>`_

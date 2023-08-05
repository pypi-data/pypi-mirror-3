Introduction
============

The ``horae.ticketing`` package implements the different models and their
hierarchy for the Horae resource planning system which there are:

* Client
* Project
* Milestone
* Ticket

Where clients hold projects and projects hold milestones and tickets. Tickets
may optionally be grouped into milestones. All the aforementioned models are using
the property architecture provided by the `horae.properties
<http://pypi.python.org/pypi/horae.properties>`_ package and thus implement
``horae.properties.interfaces.IPropertied``. The following default properties
are registered for the different containers:

Global properties
-----------------

* Name (``horae.properties.properties.TextLineProperty``)
* Description (``horae.properties.properties.RichTextProperty``)
* Tags (``horae.properties.properties.KeywordProperty``)

Project properties
------------------

* Start/due date (``horae.properties.properties.DateTimeRangeProperty``)

Milestone properties
--------------------

* Start/due date (``horae.properties.properties.DateTimeRangeProperty``)

Ticket properties
-----------------

* Estimated hours (``horae.properties.properties.FloatProperty``)
* Start/due date (``horae.properties.properties.DateTimeRangeProperty``)
* Responsible (``horae.properties.properties.UserRoleProperty``)
* Comment title (``horae.properties.properties.TextLineProperty``)
* Comment (``horae.properties.properties.RichTextProperty``)
* Milestone (``horae.properties.properties.MilestoneProperty``)
* Hidden fields (``horae.properties.properties.FieldsProperty``)
* Dependencies (``horae.ticketing.properties.TicketReferenceProperty``)

Dependencies
============

Horae
-----

* `horae.auth <http://pypi.python.org/pypi/horae.auth>`_
* `horae.cache <http://pypi.python.org/pypi/horae.cache>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.lifecycle <http://pypi.python.org/pypi/horae.lifecycle>`_
* `horae.properties <http://pypi.python.org/pypi/horae.properties>`_
* `horae.search <http://pypi.python.org/pypi/horae.search>`_
* `horae.timeaware <http://pypi.python.org/pypi/horae.timeaware>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `z3c.relationfield <http://pypi.python.org/pypi/z3c.relationfield>`_
* `hurry.query <http://pypi.python.org/pypi/hurry.query>`_

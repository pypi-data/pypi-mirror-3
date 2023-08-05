Introduction
============

``horae.properties`` provides the dynamic property infrastructure used by
the client, project, milestone and ticket content objects of the
`horae.ticketing <http://pypi.python.org/pypi/horae.ticketing>`_.

Usage
=====

The package builds up on three main classes:

``Properties``
  Container for persistent properties
``Property``
  A property providing one or more fields
``Propertied``
  An object based on the fields provided by the properties which are
  defined by the corresponding property containers

Objects using the property architecture have to subclass the
``horae.properties.propertied.PropertiedMixin`` mix in class and their
add, edit and display forms have to subclass the corresponding base classes
``PropertiedAddForm``, ``PropertiedEditForm`` and ``PropertiedDisplayForm``
defined in ``horae.properties.views``. The properties for a propertied
object are collected from all named adapters implementing
``horae.properties.interfaces.IProperties`` and adapting the object.
Sample implementations may be found in the `horae.ticketing
<http://pypi.python.org/pypi/horae.ticketing>`_ package.

There are five property containers implemented by ``horae.properties`` which
there are:

**Global properties**
  Properties available for all propertied objects
**Client properties**
  Properties available for clients
**Project properties**
  Properties available for projects
**Milestone properties**
  Properties available for milestones
**Ticket properties**
  Properties available for tickets

Properties may be created or customized persistently using the GUI
provided by ``horae.properties``. Another way to define properties
is by defining them as default properties which is done by registering
a named global utility implementing ``horae.properties.interfaces.IDefaultProperty``.
Examples of such default properties may be found in the `horae.ticketing
<http://pypi.python.org/pypi/horae.ticketing>`_ package.

Property types
==============

The package provides the following ``Property`` implementations defined in
``horae.properties.properties``:

``BoolProperty``
  A boolean property
``TextLineProperty``
  A textline property
``TextProperty``
  A text property
``RichTextProperty``
  A rich text property
``ChoiceProperty``
  A choice property
``MultipleChoiceProperty``
  A multiple choice property
``WeightedChoiceProperty``
  A choice property having weighted options
``FloatProperty``
  A float property
``PriceProperty``
  A price property
``UserProperty``
  A user property
``UserRoleProperty``
  A user role property
``GroupProperty``
  A group property
``GroupRoleProperty``
  A group role property
``DateTimeProperty``
  A date time property
``DateTimeRangeProperty``
  A date time range property

History
=======

A ``Propertied`` object stores changes in a list of ``PropertyChange`` objects
to preserve a changelog of the lifecycle. A view of the whole history
may be provided by sub-classing the ``horae.properties.views.History`` base
class.

Dependencies
============

Horae
-----

* `horae.auth <http://pypi.python.org/pypi/horae.auth>`_
* `horae.autocomplete <http://pypi.python.org/pypi/horae.autocomplete>`_
* `horae.cache <http://pypi.python.org/pypi/horae.cache>`_
* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.lifecycle <http://pypi.python.org/pypi/horae.lifecycle>`_
* `horae.timeaware <http://pypi.python.org/pypi/horae.timeaware>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `z3c.relationfield <http://pypi.python.org/pypi/z3c.relationfield>`_

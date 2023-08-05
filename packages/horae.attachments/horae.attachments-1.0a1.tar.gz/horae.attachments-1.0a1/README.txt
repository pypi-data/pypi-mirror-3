Introduction
============

The ``horae.attachments`` package provides support for adding attachments
to tickets of the Horae resource planning system. This is done by using
the view extension mechanism provided by `horae.layout
<http://pypi.python.org/pypi/horae.layout>`_ to extend the ticket change
view provided by `horae.ticketing <http://pypi.python.org/pypi/horae.ticketing>`_
by a field to add multiple files. Additionally the display view and history
of a ticket is extended in the same way to have the added attachments
rendered as links.

Dependencies
============

Horae
-----

* `horae.core <http://pypi.python.org/pypi/horae.core>`_
* `horae.layout <http://pypi.python.org/pypi/horae.layout>`_
* `horae.properties <http://pypi.python.org/pypi/horae.properties>`_
* `horae.ticketing <http://pypi.python.org/pypi/horae.ticketing>`_

Third party
-----------

* `grok <http://pypi.python.org/pypi/grok>`_
* `z3c.relationfield <http://pypi.python.org/pypi/z3c.relationfield>`_

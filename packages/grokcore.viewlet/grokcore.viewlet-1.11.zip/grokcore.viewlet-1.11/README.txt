This package provides support to write and register Zope Viewlets
directly in Python (without ZCML). It's designed to be used with
`grokcore.view`_ which let you write and register Zope Views.

.. contents::

Setting up ``grokcore.viewlet``
===============================

This package is set up like the `grokcore.component`_
package. Please refer to its documentation for more details. The
additional ZCML lines you will need are::

  <include package="grokcore.viewlet" file="meta.zcml" />
  <include package="grokcore.viewlet" />

Put the first line somewhere near the top of your root ZCML file.

Examples
========

First we need a view to call our viewlet manager::

   from grokcore import viewlet

   class Index(viewlet.View):
       pass

   index = viewlet.Page Template("""
   <body>
   <head>Test</head>
   <body>
   <div tail:content="structure provider:content">
   </div>
   </body>
   """)

After that we could define only a manager which display something::

   class Content(viewlet.ViewletManager):
       viewlet.View(Index)

       def render(self):
           return u'<h1>Hello World</h1>'


Or a completely different example::

   class AdvancedContent(viewlet.ViewletManager):
       viewlet.name('content')
       viewlet.view(Index)

And some viewlets for that one::

   class StaticData(viewlet.Viewlet):
       viewlet.view(Index)
       viewlet.viewletmanager(AdvancedContent)

       def render(self):
           return u'<p> Data from %s</p>' self.context.id

Or::

   class SecretData(viewlet.Viewlet):
       viewlet.view(Index)
       viewlet.viewletmanager(AdvancedContent)
       viewlet.require('agent.secret')

   secretdata = viewlet.PageTemplate("""
   <p>Nothing to see here.</p>
   """)

The way templates are binded to components works exactly the way than
in `grokcore.view`_, for more information refer to its
documentation.

API Overview
============

Base classes
------------

``ViewletManager``
  Define a new viewlet manager. You can either provide a render
  method, a template, which can or not use registered viewlets.

  If you define a template, ``view`` is added as a reference to the
  current view for which the manager is rendering in the template's
  namespace. It is available as well as an attribute on the manager
  object.

``Viewlet``
  Define a new viewlet. You can either provide a template or a render
  method on it. Like in views, you can define an update method to
  process needed data.

  Like for manager, ``view`` is added to the template namespace if
  used. ``viewletmanager`` is defined as well as a reference to the
  manager in the template's namespace and as an attribute on the
  viewlet object.

Directives
----------

You can use directives from `grokcore.view`_ to register your
viewlet or viewlet manager: ``name``, ``context``, ``layer`` and
``require`` (for security on a viewlet).

To that is added:

``view``
   Select for which view is registered a viewlet or a viewlet manager.

``viewletmanager``
   Select for which viewlet manager is registered a viewlet.

``order``
   Define a rendering order for viewlets in a viewlet manager. This
   should be a number, the smaller order render first, bigger last.


Additionally, the ``grokcore.viewlet`` package exposes the
`grokcore.component`_, `grokcore.security`_ and `grokcore.view`_ APIs.

.. _grokcore.component: http://pypi.python.org/pypi/grokcore.component
.. _grokcore.viewlet: http://pypi.python.org/pypi/grokcore.viewlet
.. _grokcore.security: http://pypi.python.org/pypi/grokcore.security
.. _grokcore.view: http://pypi.python.org/pypi/grokcore.view

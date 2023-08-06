
This package provides support to write local site and utilities for
Zope directly in Python (without ZCML).

.. contents::


Setting up ``grokcore.site``
============================

This package is essentially set up like the `grokcore.component`_
package, please refer to its documentation for details.  The only
additional ZCML line you will need is::

  <include package="grokcore.site" />

Put this somewhere near the top of your root ZCML file but below the
line where you include ``grokcore.component``'s configuration.


Examples
========

Global utilities are already managed by `grokcore.component`_.

Here a simple example of a local utility::

  from zope.interface import implements, Interface
  import grokcore.site

  class IKangaroo(Interface):

      def jump():
         """Make all kangaroos jump somewhere.
         """

  class KangarooUtility(grokcore.site.LocalUtility):
      implements(IKangaroo)

      def jump(self):
          pass


Now, we can register our utility to a local site. That will create
automatically, and register that utility when we create that site::


   class Jungle(grokcore.site.Site):

       grokcore.site.local_utility(KangarooUtility, IKangaroo)


If you don't add the last line, you will still have your site, but
nothing to make jump your kangaroo. Then, you will be able to add
manually by hand after (if you want).


API Overview
============

Base classes
------------

``Site``
   Base class for your site.

``LocalUtility``
   Base class for a ZODB-persitent local utility.


Directives
----------

``local_utility(factory, provides=None, name=u'', setup=None, public=False, name_in_container=None``)
   Directive used on a site to register a local utility at the
   creation time:

   ``factory``
      Would be the component to register (required parameter),

   ``provides``
      Would be the interface used to query the local utility (required
      parameter),

   ``name``
      Would be the name used to query the local utility,

   ``setup``
      Would be a function taking parameter. If defined it will be
      called after the utility is created with it as first and unique
      parameter.

   ``public``
      If true, the utility will be created in the site container
      itself, not in the site manager, and public will be able to
      access it directly.

   ``name_in_container``
      Would be used as id for the utility in container itwill be
      created. If not defined it will ask NameChooser to pick a name
      for it.

In addition, the ``grokcore.site`` package exposes the
`grokcore.component`_ API.

.. _grokcore.component: http://pypi.python.org/pypi/grokcore.component

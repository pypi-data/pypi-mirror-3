This package provides basic elements for defining Zope permissions and
security checkers without ZCML.

.. contents::

Setting up ``grokcore.security``
================================

This package is essentially set up like the `grokcore.component`_
package, please refer to its documentation for details.  The
additional ZCML lines you will need are::

  <include package="grokcore.security" file="meta.zcml" />
  <include package="grokcore.security" />

Put this somewhere near the top of your root ZCML file but below the
line where you include ``grokcore.component``'s configuration.


Defining permissions
====================

In `grokcore.component`_, various components are defined (and
automatically registered) by subclassing from certain baseclasses.
The same applies to defining permissions with ``grokcore.security`` as
well::

  import grokcore.security

  class EditContent(grokcore.security.Permission):
      grokcore.security.name('mypkg.EditContent')

This defines a permission with the ID ``mypkg.EditContent``.  You must
always specify this ID explicitly.  In addition, you can also give the
permission a human-readable title and description.  This is useful
when your application provides lists of permissions somewhere and you
don't want to bother users with deciphering the dotted IDs::

  import grokcore.security

  class EditContent(grokcore.security.Permission):
      grokcore.security.name('mypkg.EditContent')
      grokcore.security.title('Edit content')
      grokcore.security.description('Anyone who has this permission may '
                                    'modify content in the application.')


Defining checkers for components
================================

``grokcore.security`` provides some means for defining checkers for
components:

* ``grokcore.security.require(permission)`` which can be used either
  as a class-level directive to set a permission for a whole
  component, or as a decorator to set a permission for a function or
  method.

* ``protect_getattr`` and ``protect_setattr``, available from
  ``grokcore.security.util``, which take a class, an attribute name
  and a permission as arguments and define Zope security checkers for
  getting or setting a particular attribute on instance of said class.

With these, you can build grokkers for components that need security
declarations.  For instance, the `grokcore.view`_ package uses them to
define a grokker that makes security declarations for views::

  class ViewSecurityGrokker(martian.ClassGrokker):
      martian.component(grokcore.view.View)
      martian.directive(grokcore.security.require, name='permission')

      def execute(self, factory, config, permission, **kw):
          for method_name in zope.publisher.interfaces.browser.IBrowserPage:
              config.action(
                  discriminator=('protectName', factory, method_name),
                  callable=grokcore.security.util.protect_getattr,
                  args=(factory, method_name, permission),
                  )
          return True

With such a grokker, it is possible to protect views like so::

  class Edit(grokcore.view.View):
      grokcore.security.require(EditContent)

Note how we can simply pass a permission class to the ``require``
directive.  Alternatively, you can pass the permission ID::

  class Edit(grokcore.view.View):
      grokcore.security.require('mypkg.EditContent')

If you wanted to be able to define permissions for individual class
methods rather than the whole class, you would simply base your
grokker on ``martian.MethodGrokker`` rather than ``ClassGrokker``.
The actual mechanics of defining a checker are the same.

Please note that ``grokcore.security`` does not yet provide directives
that allow you to specify permissions for simple attribute access
(read and write).


API overview
============

``Permission``
    Base class for defining permissions.  Use the ``name`` directive
    to define the mandatory permission ID.  Optionally use the
    ``title`` and ``description`` directives to give the permission
    human-readable information.

``Public``
    Special permission that can be referred to whenever a component
    should not be protected by a permission at all (public access).

``require(permission_class_or_id)``
    declares that the use of a particular component (when used as a
    class-level directive) or a method (when used as a method
    decorator) requires a certain permission.  The argument can either
    be a permission class (subclass of ``Permission``) or a permission
    ID.

In addition, the ``grokcore.security`` package exposes the
`grokcore.component`_ API.


.. _grokcore.component: http://pypi.python.org/pypi/grokcore.component
.. _grokcore.view: http://pypi.python.org/pypi/grokcore.view

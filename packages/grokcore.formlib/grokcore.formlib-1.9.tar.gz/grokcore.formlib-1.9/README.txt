This package provides support for writing forms using the Zope Formlib
library and registering them directly in Python (without ZCML).

.. contents::

Setting up ``grokcore.formlib``
===============================

This package is essentially set up like the `grokcore.component`_
package, please refer to its documentation for details.  The
additional ZCML lines you will need are::

  <include package="grokcore.formlib" file="meta.zcml" />
  <include package="grokcore.formlib" />

Put the first line somewhere near the top of your root ZCML file.

Examples
========

We need an example interface::

  from zope import interface, schema

  class IMammoth(interface.Interface):

     name = schema.TextLine(title=u"Name")
     age = schema.Int(title=u"Age", min=0)

Edit forms
----------

You can provide an edit form for ``IMammoth`` like this::


  from grokcore import formlib

  class Edit(formlib.EditForm):

     formlib.context(IMammoth)


If your content object is defined in the same Python file and
implements ``grokcore.formlib.IContext``, then it will be the default
context for your form.


Display forms
-------------

Display forms are as easy as edit forms::

  class Index(formlib.DisplayForm):

     formlib.context(IMammoth)


Generic forms
-------------


You can build more generic forms, providing your own actions for a form::


   class ISearch(interface.Interface):

       search = schema.TextLine(title=u"Text")


After this, you define your form. It's applied to a mammoth, but uses
the ``ISearch`` interface to generate fields::

   class Search(formlib.Form):

       formlib.context(IMammoth)

       form_fields = formlib.Fields(ISearch)

       def update(self):
           # Default search results are None
           self.search_result = None

       @formlib.action(u"Search")
       def search(self, text):
           self.search_result = 'something found with text'



Create a custom template ``search.pt`` to render your form (in a
directory ``modulename_templates``).


Add forms
---------

Add forms work like generic forms, you have to provide your action
``Add``.

Customization
-------------

Since a Grok form is a Grok view, all configuration directives and
attributes available on a Grok view are available as well on a Grok
form.

This means that you can customize your form by associating a template
with it. The template is responsible for displaying widgets and
actions. The API to access them is the same as on a Zope Formlib form.

You can't customize a form by providing a ``render()`` method on it,
but you can still use the ``update()`` method if you want.

Please refer to the documentation of `grokcore.view`_ for more
details.

API Overview
============

Base classes
------------

``EditForm``
  Extends ``Form`` to create an edit form for your content.

``DisplayForm``
  Creates simple display forms.

``Form``
  Is a base class to create generic forms.

``AddForm``
  Extends ``Form`` to create add forms. You have to provide the *add*
  action which is going to create the new object.



Decorators
----------

``action``
  Is a decorator to create an action on the form. Your action only has
  to accept values from the form as parameters.

Helpers
-------

``AutoFields``
  Create form fields from the given context. If the context is an
  interface, Zope fields defined in that interface are going to be
  used to build form fields.
  If the context is a regular object, Zope fields of all implemented
  interfaces of that object are going to used to build form fields.

``Fields``
  Create and reorder fields on the form.


Additionally, the ``grokcore.formlib`` package exposes the
`grokcore.component`_, `grokcore.security`_ and `grokcore.view`_ APIs.

.. _grokcore.component: http://pypi.python.org/pypi/grokcore.component
.. _grokcore.formlib: http://pypi.python.org/pypi/grokcore.formlib
.. _grokcore.security: http://pypi.python.org/pypi/grokcore.security
.. _grokcore.view: http://pypi.python.org/pypi/grokcore.view



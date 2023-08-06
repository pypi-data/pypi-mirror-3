.. _usage:

=======
 Usage
=======

Markup-Types
============

django-markupmirror comes with five default markup types (or converters). You
Can create and register your own converters and unregister the default ones if
you prefer.

.. _usage-markup-types-default:

Default Markup Types
--------------------

The markup-types available by default are:

``plaintext``
    .. automodule:: markupmirror.markup.plaintext
    .. autoclass:: PlainTextMarkup

``html``
    .. automodule:: markupmirror.markup.html
    .. autoclass:: HtmlMarkup

``markdown``
    .. automodule:: markupmirror.markup.markdown_
    .. autoclass:: MarkdownMarkup

``restructuredtext``
    .. automodule:: markupmirror.markup.restructuredtext
    .. autoclass:: ReStructuredTextMarkup

``textile``
    .. automodule:: markupmirror.markup.textile_
    .. autoclass:: TextileMarkup

The Markup Pool
---------------

The markup pool is the main access point to markup converters. They are
registered with the pool, and retrieved from it.

.. automodule:: markupmirror.markup.base

.. py:data:: markupmirror.markup.base.markup_pool

   Instance of ``MarkupPool`` for public use.

.. autoclass:: MarkupPool
   :members:

Create your own Markup Type
---------------------------

You can easily create your own markup converters for any purpose. The converter
only needs to inherit from ``BaseMarkup`` and implement the ``convert`` method.

.. autoclass:: markupmirror.markup.base.BaseMarkup
   :members: convert, before_convert, after_convert, __call__, get_name
   :special-members:

Register and unregister Markup Types
------------------------------------

The :ref:`default markup types <usage-markup-types-default>` provided by
django-markupmirror are registered during initialization. If you want to remove
any of these, you can use the ``MarkupPool.unregister_markup`` method::

    from markupmirror.markup.base import markup_pool

    markup_pool.unregister_markup('plaintext')  # is equal to
    del markup_pool['textile']

To register new markup converters, pass the markup class to the
``MarkupPool.register_markup`` method::

    from markupmirror.markup.base import markup_pool, BaseMarkup

    class ExampleMarkup(BaseMarkup):

        def convert(self, markup):
            return markup.replace("markup", "example")

    markup_pool.register_markup(ExampleMarkup)

This would make the ``ExampleMarkup`` converter available through the key
``example``, derived from its class name::

    example_markup = markup_pool['example']

Using the ``MarkupMirrorField``
===============================

After you have configured markupmirror in your settings and added your custom
markup converters, the only thing left to do is to use the
``MarkupMirrorField`` in your models.

A field with fixed markup type would have to provide a ``markup_type``::

    from django.db import models
    from markupmirror.fields import MarkupMirrorFields

    class MyModel(models.Model):
        content = MarkupMirrorField(markup_type='markdown')

To provide a selectbox for the users to select the content's markup type
manually, use ``default_markup_type`` instead::

    class MyModel(models.Model):
        content = MarkupMirrorField(default_markup_type='plaintext')

If you provide neither ``markup_type`` nor ``default_markup_type``, the
``MARKUPMIRROR_DEFAULT_MARKUP_TYPE`` setting will be used as default.

For reference, see the ``MarkupMirrorField`` and ``Markup`` classes:

.. automodule:: markupmirror.fields

.. autoclass:: MarkupMirrorField

.. autoclass:: Markup
   :members: raw, markup_type, rendered, __unicode__
   :special-members:

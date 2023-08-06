.. _installation:

==============
 Installation
==============

* To **install** django-markupmirror, use `pip`_ (or `easy_install`_ or simply
  ``python setup.py install`` from source) and add ``'markupmirror'`` to the
  ``INSTALLED_APPS`` in your `Django`_ project.

  .. code-block:: bash

    $ pip install django-markupmirror

  ::

    INSTALLED_APPS = (
        ...
        'markupmirror',
        ...
    )

* In your ``settings.py`` specify at least ``MARKUPMIRROR_DEFAULT_MARKUP_TYPE``
  which is ``'plaintext'`` by default.

* For the markup HTML-preview, you'll need to add markupmirror's URLs in your
  URLconf. In your ``urls.py`` add::

    import markupmirror.urls

    urlpatterns = patterns('',
        (r'^markupmirror/', include(markupmirror.urls.preview)),
    )

.. _pip: http://www.pip-installer.org/
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall

Requirements
------------

django-markupmirror depends on:

* `Django`_ 1.4+ (for now tested with 1.4 only), obviously.

* `FeinCMS`_ 1.5+ (for now tested with 1.5.3 only), if you want to use the page
  content-type.

* `Markdown 2.1+`_, if you want to use the ``MarkdownMarkup`` converter.

* `Docutils 0.8+`_, if you want to use the ``ReStructuredTextMarkup``
  converter.

* `Textile 2.1+`_, if you want to use the ``TextileMarkup`` converter.

The three latter will be available automatically if the respective dependencies
are met.

.. _Django: http://pypi.python.org/pypi/Django
.. _FeinCMS: http://pypi.python.org/pypi/FeinCMS
.. _Markdown 2.1+: http://pypi.python.org/pypi/Markdown
.. _Docutils 0.8+: http://pypi.python.org/pypi/docutils
.. _Textile 2.1+: http://pypi.python.org/pypi/textile

Settings & Configuration
------------------------

Use the configuration variables below in your ``settings.py`` to customize the
behaviour of django-markupmirror:

.. automodule:: markupmirror.settings

.. py:data:: MARKUPMIRROR_DEFAULT_MARKUP_TYPE

   Defines any of the :ref:`default markup-types <usage-markup-types-default>`
   as default for fields where no ``markup_type`` or ``default_markup_type``
   has been set explicitly.

   Defaults to ``plaintext``.

.. py:data:: MARKUPMIRROR_MARKDOWN_EXTENSIONS

   Defines the extensions to load for `Markdown`_. Markdown's package
   documentation contains `a list of available extensions`_.

   Defaults to ``['extra', 'headerid(level=2)']``.

.. py:data:: MARKUPMIRROR_MARKDOWN_OUTPUT_FORMAT

   Defines the output format for Markdown. One of ``HTML4``, ``XHTML`` and
   ``HTML5``.

   Defaults to ``HTML5``.

.. py:data:: MARKUPMIRROR_TEXTILE_SETTINGS

   Dictionary of arguments passed directly to the Textile converter defined in
   ``textile.functions.textile``.

   The converter's default function signature is:
   ``head_offset=0, html_type='xhtml', auto_link=False, encoding=None,
   output=None``.

   Defaults to::

    MARKUPMIRROR_TEXTILE_SETTINGS = {
        'encoding': 'utf-8',
        'output': 'utf-8'
    }

.. py:data:: MARKUPMIRROR_CODEMIRROR_SETTINGS

   Basic settings passed to all CodeMirror editor instances for initialization.
   Check the `CodeMirror documentation on configuration settings`_ for details.

   Defaults to::

    MARKUPMIRROR_CODEMIRROR_SETTINGS = {
        'width': '50%',
        'height': '300px',
        'indentUnit': 4,
        'lineNumbers': True,
        'lineWrapping': True,
        'path': settings.STATIC_URL + 'markupmirror/',
    }


.. _Markdown: http://daringfireball.net/projects/markdown/
.. _Markdown's package documentation: http://packages.python.org/Markdown/
.. _a list of available extensions:
    http://packages.python.org/Markdown/extensions/
.. _CodeMirror documentation on configuration settings:
    http://codemirror.net/doc/manual.html#config

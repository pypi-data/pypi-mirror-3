Quickstart
==========

* To **install** django-markupmirror, use `pip`_ and add ``'markupmirror'`` to
  the ``INSTALLED_APPS`` in your `Django`_ project.

* In your ``settings.py`` specify at least ``MARKUPMIRROR_DEFAULT_MARKUP_TYPE``
  which is ``'plaintext'`` by default.

* For the markup HTML-preview, you'll need to add markupmirror's URLs in your
  URLconf. In your ``urls.py`` add::

    import markupmirror.urls

    urlpatterns = patterns('',
        (r'^markupmirror/', include(markupmirror.urls.preview)),
    )

* Add one or more ``markupmirror.fields.MarkupMirrorField`` s to your models
  and define ``markup_type`` or ``default_markup_type``::

    class ModelWithMarkup(models.Model):
        content = MarkupMirrorField(
            verbose_name="content", markup_type='markdown')

* If you want the `FeinCMS`_ content-type model ``MarkupMirrorContent``, you'll
  also need to add ``'markupmirror.feincms'`` to your ``INSTALLED_APPS``.

  Also, you need to register the content-type model with FeinCMS' Page module::

    from feincms.module.page.models import Page
    from markupmirror.feincms.models import MarkupMirrorContent

    Page.create_content_type(MarkupMirrorContent)

By default, django-markupmirror comes with markup converters for plain text
(converts links and linebreaks) and HTML (does nothing). Converters for
`Markdown`_, `reStructuredText`_ and `Textile`_ are also available, but require
3rd-party libraries to be installed. However, you can register your own markup
converters.

.. _pip: http://www.pip-installer.org/
.. _easy_install: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _Django: http://www.djangoproject.com/
.. _FeinCMS: http://www.feinheit.ch/media/labs/feincms/
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Textile: http://www.textism.com/tools/textile/

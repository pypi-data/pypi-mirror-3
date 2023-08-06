.. _feincms:

=====================
 FeinCMS Integration
=====================

django-markupmirror provides easy integration with `Feinheit's FeinCMS`_ in
form of a `custom content-type`_.

The only thing you need to do to use it, is to register the
``MarkupMirrorContent`` content-type model with your ``Page`` configuration::

    from feincms.module.page.models import Page
    from markupmirror.feincms.models import MarkupMirrorContent

    Page.create_content_type(MarkupMirrorContent)

After that you should synchronize your database structure. Find out `how to
use South to migrate your FeinCMS tables`_ in FeinCMS' documentation.

.. _Feinheit's FeinCMS: http://feinheit.ch/media/labs/feincms/
.. _custom content-type:
    http://feinheit.ch/media/labs/feincms/contenttypes.html
.. _how to use South to migrate your FeinCMS tables:
    http://feinheit.ch/media/labs/feincms/migrations.html

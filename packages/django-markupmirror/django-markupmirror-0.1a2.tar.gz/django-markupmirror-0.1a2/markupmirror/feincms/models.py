from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from markupmirror import settings
from markupmirror.fields import MarkupMirrorField


class MarkupMirrorContent(models.Model):
    """FeinCMS Page contenttype that stores markup in a MarkupMirrorField.

    """
    # TODO: find a way to include a button like richtext content
    # __name__ = 'richtextcontent'

    feincms_item_editor_context_processors = (
        lambda x: settings.MARKUPMIRROR_FEINCMS_INIT_CONTEXT,
    )
    feincms_item_editor_includes = {
        'head': [settings.MARKUPMIRROR_FEINCMS_INIT_TEMPLATE],
    }

    content = MarkupMirrorField(
        verbose_name=_(u"Markup content"),
        markup_type=settings.MARKUPMIRROR_DEFAULT_MARKUP_TYPE,
        blank=True)

    class Meta:
        abstract = True
        app_label = 'wienfluss'
        verbose_name = _(u"Markup content")
        verbose_name_plural = _(u"Markup content")

    def render(self, **kwargs):
        request = kwargs.get('request')
        return render_to_string('content/markupmirror/default.html', {
            'content': self,
            'request': request
        })


__all__ = ('MarkupMirrorContent',)

from django.utils.html import linebreaks
from django.utils.html import urlize
from django.utils.translation import ugettext_lazy as _

from markupmirror.markup.base import BaseMarkup
from markupmirror.markup.base import register_markup


class PlainTextMarkup(BaseMarkup):
    """Markup transformer for plain-text content.

    This uses Django's ``urlize`` and ``linebreaks`` utitlies to convert URLs
    in the text to clickable links and linebreaks to ``<p>`` and ``<br />``
    elements respectively.

    """
    codemirror_mode = 'text/plain'
    title = _(u"Plain text")

    def convert(self, markup):
        return urlize(linebreaks(markup))


register_markup(PlainTextMarkup)


__all__ = ('PlainTextMarkup',)

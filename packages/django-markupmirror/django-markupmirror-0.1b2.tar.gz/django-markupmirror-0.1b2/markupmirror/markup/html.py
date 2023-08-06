from django.utils.translation import ugettext_lazy as _

from markupmirror.markup.base import BaseMarkup
from markupmirror.markup.base import register_markup


class HtmlMarkup(BaseMarkup):
    """Markup pseudo-transformer for HTML content.

    This does not transform anything and thus is potentially harmful.
    Use with care.

    """
    codemirror_mode = 'text/html'
    title = _(u"HTML")


register_markup(HtmlMarkup)


__all__ = ('HtmlMarkup',)

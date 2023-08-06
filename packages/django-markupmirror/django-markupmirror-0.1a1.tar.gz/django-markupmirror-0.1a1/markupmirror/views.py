from django.http import HttpResponse
from django.views.generic.base import View

from markupmirror.markup.base import markup_pool


class MarkupPreview(View):
    """Renders markup content to HTML for preview purposes."""

    http_method_names = ['post']

    def post(self, request, markup_type, *args, **kwargs):
        markup = markup_pool.get_markup(markup_type)
        text = self.request.POST.get('text', u"")
        return HttpResponse(markup(text), content_type='text/html')


__all__ = ('MarkupMirrorPreview',)

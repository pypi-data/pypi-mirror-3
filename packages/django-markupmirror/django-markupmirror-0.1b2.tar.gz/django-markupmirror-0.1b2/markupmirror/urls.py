from django.conf.urls import patterns
from django.conf.urls import url
from django.views.generic.base import TemplateView

from markupmirror.views import MarkupPreview


urlpatterns = patterns('',
    url(r'^preview/$', MarkupPreview.as_view(), name='preview'),
    url(r'^base/$',
        TemplateView.as_view(
            template_name='markupmirror/preview.html'),
        name='base'),
)


# Default namespace registration for include('markupmirror.urls.preview')
# (urlpatterns, app_name, namespace)
preview = (urlpatterns, 'markupmirror', 'markupmirror')


__all__ = ('preview',)

from django.conf.urls.defaults import include
from django.conf.urls.defaults import patterns

import markupmirror.urls


urlpatterns = patterns('',
    (r'^markupmirror/', include(markupmirror.urls.preview)),
)

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget
from django.core.urlresolvers import reverse
from django.utils import simplejson as json

from markupmirror import settings
from markupmirror.markup.base import markup_pool


class MarkupMirrorTextarea(forms.Textarea):

    css_classes = ('markupmirror-editor',)

    def __init__(self, attrs=None):
        """Adds the ``markupmirror-editor`` class to the textarea to make sure
        it can be identified through JS.

        """
        css_class = attrs.get('class', '') if attrs else ''
        for cls in self.css_classes:
            if cls not in css_class:
                css_class += ' ' + cls
                css_class = css_class.strip()

        default_attrs = {
            'class': css_class,
        }

        if attrs:
            default_attrs.update(attrs)
        super(MarkupMirrorTextarea, self).__init__(attrs=default_attrs)

    def render(self, name, value, attrs=None):
        default_attrs = {}

        # start with CodeMirror base settings
        mm_settings = settings.MARKUPMIRROR_CODEMIRROR_SETTINGS.copy()
        markup_type = settings.MARKUPMIRROR_DEFAULT_MARKUP_TYPE

        # if value is filled, use the markup type defined with the content
        if value is not None and not isinstance(value, unicode):
            # get markup converter by type.
            # ``value`` is ``markupmirror.fields.Markup``.
            markup_type = value.markup_type
            # get real value
            value = value.raw

        # mode for CodeMirror and preview and base URLs plus markup_type
        # parameter for loading markup previews
        mm_settings.update({
            'mode': markup_pool[markup_type].codemirror_mode,
            'markup_type': markup_type,
            'preview_url': reverse('markupmirror:preview'),
            'base_url': reverse('markupmirror:base'),
        })

        # provide mm_settings as data attribute in widget
        default_attrs = {
            'data-mm-settings': json.dumps(mm_settings, sort_keys=True),
        }
        if attrs:
            default_attrs.update(attrs)

        return super(MarkupMirrorTextarea, self).render(name, value,
                                                        default_attrs)

    class Media:
        css = {
            'all': settings.MARKUPMIRROR_CSS
        }
        js = settings.MARKUPMIRROR_JS


class AdminMarkupMirrorTextareaWidget(
    MarkupMirrorTextarea, AdminTextareaWidget):

    css_classes = ('vLargeTextField', 'markupmirror-editor')


__all__ = ('MarkupMirrorTextarea', 'AdminMarkupMirrorTextareaWidget')

from django import forms
from django.contrib.admin.widgets import AdminTextareaWidget

from markupmirror import settings
from markupmirror.markup.base import markup_pool


class MarkupMirrorTextarea(forms.Textarea):

    css_classes = ('item-markupmirror',)

    def __init__(self, attrs=None):
        """Adds the ``item-markupmirror`` class to the textarea to make sure
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
        if value is not None and not isinstance(value, unicode):
            # get markup converter by type.
            # ``value`` is ``markupmirror.fields.Markup``.
            markup_type = value.markup_type
            markup = markup_pool.get_markup(markup_type)

            default_attrs = {
                'data-mode': markup.codemirror_mode,
                'data-markuptype': markup_type,
            }

            # get real value
            value = value.raw
        else:
            default = settings.MARKUPMIRROR_DEFAULT_MARKUP_TYPE
            default_attrs = {
                'data-mode': markup_pool[default].codemirror_mode,
                'data-markuptype': default,
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

    css_classes = ('vLargeTextField', 'item-markupmirror')


__all__ = ('MarkupMirrorTextarea', 'AdminMarkupMirrorTextareaWidget')

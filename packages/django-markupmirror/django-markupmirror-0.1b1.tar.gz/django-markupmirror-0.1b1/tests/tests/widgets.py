import textwrap

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import simplejson as json

from markupmirror import settings as mm_settings
from markupmirror.markup.base import markup_pool
from markupmirror.widgets import AdminMarkupMirrorTextareaWidget

from tests import settings
from tests.models import Post, PostForm


class MarkupMirrorWidgetTests(TestCase):
    """Tests the ``markupmirror.widget.MarkupMirrorTextarea`` and
    ``..AdminMarkupMirrorTextareaWidget`` implementations.

    """

    maxDiff = None

    def setUp(self):
        """Creates three ``Post`` objects with different field settings."""

        # Post with Markdown field
        self.mp = Post(title="example Markdown post",
                       body="**markdown**", body_markup_type='markdown')
        self.mp.save()

        # default data attribute values for textareas:
        self.mm_settings = mm_settings.MARKUPMIRROR_CODEMIRROR_SETTINGS.copy()
        default = mm_settings.MARKUPMIRROR_DEFAULT_MARKUP_TYPE
        self.mm_settings.update({
            'preview_url': reverse('markupmirror:preview'),
            'base_url': reverse('markupmirror:base'),
            'mode': markup_pool[default].codemirror_mode,
            'markup_type': default,
        })

    def test_widget_media(self):
        """Tests that the CSS and JS files required by the
        ``MarkupMirrorTextarea`` and the corresponding admin widget are used
        by forms correctly.

        """
        pass

    def test_widget_default_attributes(self):
        """Tests the rendered HTML of the ``MarkupMirrorTextarea`` to make
        sure the default attributes are ok.

        """
        form = PostForm(instance=self.mp)
        comment = form.fields['comment']
        self.assertHTMLEqual(
            comment.widget.render('comment', self.mp.comment),
            textwrap.dedent(u"""\
                <textarea rows="10" cols="40" name="comment"
                          class="markupmirror-editor"
                          data-mm-settings='{0}'></textarea>""").format(
                    json.dumps(self.mm_settings, sort_keys=True))
            )

    def test_widget_additional_attributes(self):
        """Tests that additional attributes passed to the widget's ``render``
        method are not lost.

        """
        form = PostForm(instance=self.mp)
        comment = form.fields['comment']
        self.assertHTMLEqual(
            comment.widget.render('comment', self.mp.comment, attrs={
                'data-something': "else",
                }),
            textwrap.dedent(u"""\
                <textarea rows="10" cols="40" name="comment"
                          class="markupmirror-editor"
                          data-mm-settings='{0}'
                          data-something="else"></textarea>""").format(
                    json.dumps(self.mm_settings, sort_keys=True))
            )

    def test_widget_default_mode_and_markuptype(self):
        """Widgets initialized without data (create model forms) should
        have a default markup_type and mode.

        """
        form = PostForm(instance=self.mp)
        comment = form.fields['comment']

        default = settings.MARKUPMIRROR_DEFAULT_MARKUP_TYPE
        attrs = self.mm_settings.copy()
        attrs.update({
            'mode': markup_pool[default].codemirror_mode,
            'markup_type': default,
        })
        self.assertHTMLEqual(
            comment.widget.render('comment', u""),
            textwrap.dedent(u"""\
                <textarea rows="10" cols="40" name="comment"
                          class="markupmirror-editor"
                          data-mm-settings='{0}'></textarea>""").format(
                json.dumps(attrs, sort_keys=True))
            )

    def test_admin_widget_render(self):
        """Tests that the ``AdminMarkupMirrorTextareaWidget`` renders
        properly.

        """
        admin_widget = AdminMarkupMirrorTextareaWidget()
        attrs = self.mm_settings.copy()
        attrs.update({
            'mode': 'text/x-markdown',
            'markup_type': 'markdown',
        })
        self.assertHTMLEqual(
            admin_widget.render('comment', self.mp.comment),
            textwrap.dedent(u"""\
                <textarea rows="10" cols="40" name="comment"
                          class="vLargeTextField markupmirror-editor"
                          data-mm-settings='{0}' />""").format(
                json.dumps(attrs, sort_keys=True))
            )

__all__ = ('MarkupMirrorWidgetTests',)

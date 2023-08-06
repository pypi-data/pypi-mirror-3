import textwrap

from django.test import TestCase

from markupmirror.markup.base import markup_pool
from markupmirror.widgets import AdminMarkupMirrorTextareaWidget

from tests import settings
from tests.models import Post, PostForm


class MarkupMirrorWidgetTests(TestCase):
    """Tests the ``markupmirror.widget.MarkupMirrorTextarea`` and
    ``..AdminMarkupMirrorTextareaWidget`` implementations.

    """
    def setUp(self):
        """Creates three ``Post`` objects with different field settings."""

        # Post with Markdown field
        self.mp = Post(title="example Markdown post",
                       body="**markdown**", body_markup_type='markdown')
        self.mp.save()

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
                          class="item-markupmirror"
                          data-markuptype="markdown"
                          data-mode="text/x-markdown"></textarea>"""))

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
                          class="item-markupmirror"
                          data-markuptype="markdown"
                          data-mode="text/x-markdown"
                          data-something="else"></textarea>"""))

    def test_widget_default_mode_and_markuptype(self):
        """Widgets initialized without data (create model forms) should
        have a default markup_type and mode.

        """
        form = PostForm(instance=self.mp)
        comment = form.fields['comment']

        default = settings.MARKUPMIRROR_DEFAULT_MARKUP_TYPE
        self.assertHTMLEqual(
            comment.widget.render('comment', u""),
            textwrap.dedent(u"""\
                <textarea rows="10" cols="40" name="comment"
                          class="item-markupmirror"
                          data-markuptype="{default_markup_type}"
                          data-mode="{default_mode}"></textarea>""".format(
                default_markup_type=default,
                default_mode=markup_pool[default].codemirror_mode)))

    def test_admin_widget_render(self):
        """Tests that the ``AdminMarkupMirrorTextareaWidget`` renders
        properly.

        """
        admin_widget = AdminMarkupMirrorTextareaWidget()
        self.assertHTMLEqual(
            admin_widget.render('comment', self.mp.comment),
            textwrap.dedent(u"""\
                <textarea rows="10" cols="40" name="comment"
                          class="vLargeTextField item-markupmirror"
                          data-markuptype="markdown"
                          data-mode="text/x-markdown"></textarea>"""))

__all__ = ('MarkupMirrorWidgetTests',)

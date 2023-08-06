import textwrap

from django import forms
from django.core import serializers
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import simplejson as json

from markupmirror.fields import Markup
from markupmirror.fields import MarkupMirrorField
from markupmirror.markup.base import markup_pool

from tests.models import Concrete, Post, PostForm


class MarkupMirrorFieldTests(TestCase):
    """Tests the ``markupmirror.fields.MarkupMirrorField`` implementation."""

    def setUp(self):
        """Creates three ``Post`` objects with different field settings."""

        # Post with Markdown field
        self.mp = Post(title="example Markdown post",
                       body="**markdown**", body_markup_type='markdown')
        self.mp.save()

        # Post with reStructuredText field
        self.rp = Post(title="example reStructuredText post",
                       body="*reST*", body_markup_type='restructuredtext')
        self.rp.save()

        # Post being attacked
        self.xss_str = "<script>alert('xss');</script>"
        self.xss_post = Post(title="example XSS post",
                             body=self.xss_str, body_markup_type='markdown',
                             comment=self.xss_str)
        self.xss_post.save()

    def test_verbose_name(self):
        """Tests that the standard field property ``verbose_name`` works."""
        self.assertEqual(self.mp._meta.get_field('body').verbose_name,
                         "post body")

    def test_markup_type_exclusive(self):
        """``MarkupMirrorField`` fields in models may only define one of
        ``markup_type`` or ``default_markup_type`` parameters.

        """
        self.assertRaises(ImproperlyConfigured,
                          MarkupMirrorField,
                          verbose_name='broken',
                          markup_type='markdown',
                          default_markup_type='markdown')

    def test_markup_body(self):
        """Tests the three accessors ``raw``, ``rendered`` and ``markup_type``
        of the ``Markup`` content wrapper class.

        """
        self.assertEquals(self.mp.body.raw, "**markdown**")
        self.assertEquals(self.mp.body.rendered,
                          "<p><strong>markdown</strong></p>")
        self.assertEquals(self.mp.body.markup_type, "markdown")

    def test_markup_unicode(self):
        """Converting ``Markup`` to unicode uses the ``Markup.rendered``
        accessor internally.

        """
        self.assertEqual(
            unicode(self.rp.body.rendered), textwrap.dedent(u"""\
            <div class="document">
            <p><em>reST</em></p>
            </div>
            """))

    def test_from_database(self):
        """Test that data loads back from the database correctly and 'post'
        has the right type.

        """
        post1 = Post.objects.get(pk=self.mp.pk)
        self.assertIsInstance(post1.body, Markup)
        self.assertEqual(unicode(post1.body),
                         u"<p><strong>markdown</strong></p>")

    def test_pre_save(self):
        """Test that saving markup values for markup_types which are not
        registered fails.

        """
        post1 = Post.objects.get(pk=self.mp.pk)
        self.assertEqual(post1.body.markup_type, 'markdown')

        # unregister markdown
        del markup_pool['markdown']
        self.assertFalse('markdown' in markup_pool)

        # trying to save the Post now should fail
        self.assertRaises(ValueError, post1.save)

        # restore markup pool
        from markupmirror.markup import markdown_
        markup_pool.register_markup(markdown_.MarkdownMarkup)
        self.assertTrue('markdown' in markup_pool)

    def test_prepare_for_database(self):
        """Tests that ``Markup`` can be used to compare with
        ``MarkupMirrorField`` values at query time.

        """
        post1 = Post.objects.get(pk=self.mp.pk)
        body = post1.body
        self.assertIsInstance(body, Markup)
        self.assertEqual(post1, Post.objects.get(body=body))

    def test_accessor_classmethod(self):
        """``MarkupMirrorField`` attributes on model classes can only be
        accessed via an instance.

        """
        def access_body():
            return Post.body

        self.assertRaises(AttributeError, access_body)

    def test_accessor_none(self):
        """If the field is ``None`` that's what should be returned."""
        self.assertIsInstance(self.mp.body, Markup)
        self.mp.body = None
        self.assertEqual(self.mp.body, None)

    def test_body_assignment(self):
        """Setting the field's value works through the descriptor's setter
        (``MarkupMirrorFieldDescriptor.__set__``) and accepts both strings
        and ``Markup`` instances.

        """
        self.rp.body = "**reST**"
        self.rp.save()
        self.assertEquals(unicode(self.rp.body),
            unicode(self.rp.body.rendered), textwrap.dedent(u"""\
            <div class="document">
            <p><strong>reST</strong></p>
            </div>
            """))

        rest_markup = Markup(self.rp, 'body',
                             'body_rendered', 'body_markup_type')
        rest_markup.raw = "*reST*"
        self.rp.body = rest_markup
        self.assertEquals(unicode(self.rp.body),
            unicode(self.rp.body.rendered), textwrap.dedent(u"""\
            <div class="document">
            <p><em>reST</em></p>
            </div>
            """))

    def test_raw_assignment(self):
        """Setting the ``Markup.raw`` property modifies the field's value."""

        self.rp.body.raw = '*more reST*'
        self.rp.save()
        self.assertEquals(unicode(self.rp.body),
            unicode(self.rp.body.rendered), textwrap.dedent(u"""\
            <div class="document">
            <p><em>more reST</em></p>
            </div>
            """))

    def test_rendered_assignment(self):
        """The ``Markup.rendered`` property dos not have a setter."""

        def set_rendered(text):
            self.rp.body.rendered = text

        self.assertRaises(AttributeError, set_rendered, "fail!")

    def test_body_type_assignment(self):
        """The markup type can be changed using the ``Markup.markup_type``
        property.

        """
        self.rp.body.markup_type = 'markdown'
        self.rp.save()
        self.assertEquals(self.rp.body.markup_type, 'markdown')
        self.assertEquals(unicode(self.rp.body),
                          "<p><em>reST</em></p>")

    def test_serialize_to_json(self):
        """Serializing a ``Post`` with a ``MarkupMirrorField`` works."""
        stream = serializers.serialize('json', Post.objects.all())
        json_data = json.loads(stream)
        self.assertEqual(json_data, [
            {
                u'fields': {
                    u'body': u'**markdown**',
                    u'body_markup_type': u'markdown',
                    u'body_rendered': u'<p><strong>markdown</strong></p>',
                    u'comment': '',
                    u'comment_markup_type': u'markdown',
                    u'comment_rendered': '',
                    u'markdown_field': '',
                    u'markdown_field_markup_type': u'markdown',
                    u'markdown_field_rendered': '',
                    u'title': u'example Markdown post',
                },
                u'model': u'tests.post',
                u'pk': 1,
            },
            {
                u'fields': {
                    u'body': u'*reST*',
                    u'body_markup_type': u'restructuredtext',
                    u'body_rendered':
                        u'<div class="document">'
                        u'\n<p><em>reST</em></p>\n</div>\n',
                    u'comment': '',
                    u'comment_markup_type': u'markdown',
                    u'comment_rendered': '',
                    u'markdown_field': '',
                    u'markdown_field_markup_type': u'markdown',
                    u'markdown_field_rendered': '',
                    u'title': u'example reStructuredText post',
                },
                u'model': u'tests.post',
                u'pk': 2,
            },
            {
                u'fields': {
                    u'body': u"<script>alert('xss');</script>",
                    u'body_markup_type': u'markdown',
                    u'body_rendered': u"<script>alert('xss');</script>",
                    u'comment': u"<script>alert('xss');</script>",
                    u'comment_markup_type': u'markdown',
                    u'comment_rendered':
                        u'<p>&lt;script&gt;'
                        u'alert(&#39;xss&#39;);&lt;/script&gt;</p>',
                    u'markdown_field': '',
                    u'markdown_field_markup_type': u'markdown',
                    u'markdown_field_rendered': '',
                    u'title': u'example XSS post',
                },
                u'model': u'tests.post',
                u'pk': 3,
            },
        ])

    def test_deserialize_json(self):
        """Tests that objects with ``MarkupMirrorFields`` can be deserialized
        correctly.

        """
        stream = serializers.serialize('json', Post.objects.all())
        obj = list(serializers.deserialize('json', stream))[0]
        self.assertEquals(obj.object, self.mp)

    def test_escape_html(self):
        """Rendered content should be escaped to prevent XSS attacks."""
        self.assertEquals(self.xss_post.comment.raw, self.xss_str)
        self.assertEquals(
            unicode(self.xss_post.comment.rendered),
            u'<p>&lt;script&gt;alert(&#39;xss&#39;);&lt;/script&gt;</p>')

    def test_escape_html_false(self):
        """The ``MarkupMirrorField.escape_html`` prevents this escaping."""
        self.assertEquals(self.xss_post.body.raw, self.xss_str)
        self.assertEquals(unicode(self.xss_post.body.rendered), self.xss_str)

    def test_inheritance(self):
        """Abstract base models inherit the ``MarkupMirrorField`` to the
        concrete subclasses.

        """
        concrete_fields = [f.name for f in Concrete._meta.fields]
        self.assertEquals(
            concrete_fields,
            ['id', 'content', 'content_markup_type', 'content_rendered'])

    def test_markup_type_validation(self):
        """Invalid markup types are rejected."""
        self.assertRaises(ImproperlyConfigured, MarkupMirrorField,
            'verbose name', 'markup_field', 'bad_markup_type')

    def test_default_markup_types(self):
        """Per default the markup types plaintext, html are available.
        Depending on available third-party products, markdown,
        restructuredtext and textile are also in the markup pool.

        """
        markups = markup_pool.markups
        for markup_type, markup in markups.items():
            rendered = markup(u"test")
            self.assertTrue(hasattr(rendered, '__str__'))

    def test_formfield(self):
        """Form fields for ``MarkupMirrorFields`` always have three additional
        attributes:

        * ``class=item-markupmirror``.
        * ``data-mode``: ``codemirror_mode`` of the assigned markup converter.
        * ``data-markuptype``: the field's ``default_markup_type`` or the
          assigned value's ``Markup.markup_type``.

        """
        form = PostForm()
        comment = form.fields['comment']
        self.assertEqual(
            sorted(comment.widget.attrs.keys()),
            ['class', 'cols', 'data-markuptype', 'data-mode', 'rows'])
        self.assertTrue('item-markupmirror' in comment.widget.attrs['class'])
        self.assertEqual(
            comment.widget.attrs['data-markuptype'],
            self.mp.comment.markup_type)
        self.assertEqual(
            comment.widget.attrs['data-mode'],
            markup_pool[self.mp.comment.markup_type].codemirror_mode)


__all__ = ('MarkupMirrorFieldTests',)

import textwrap

from django.test import TestCase

from markupmirror.markup.markdown_ import MarkdownMarkup


MARKUP = u"""\
A First Level Header
====================

A Second Level Header
---------------------

Now is the time for all good men to come to
the aid of their country. This is just a
regular paragraph.

The quick brown fox jumped over the lazy
dog's back.

### Header 3

> This is a blockquote.
>
> This is the second paragraph in the blockquote.
>
> ## This is an H2 in a blockquote
"""


class MarkdownMarkupTests(TestCase):
    """Tests the ``markupmirror.markup.markdown_.MarkdownMarkup`` class that
    converts Markdown content to HTML.

    """
    def test_convert(self):
        """The ``MarkdownMarkup`` converter uses python-markdown to convert
        markdown to HTML.

        """
        markdown_markup = MarkdownMarkup()
        # === becomes h2 because of headerid(level=2) extension
        self.assertHTMLEqual(
            markdown_markup(MARKUP),
            textwrap.dedent(u"""\
                <h2 id="a-first-level-header">A First Level Header</h2>
                <h3 id="a-second-level-header">A Second Level Header</h3>
                <p>Now is the time for all good men to come to
                    the aid of their country. This is just a
                    regular paragraph.</p>
                <p>The quick brown fox jumped over the lazy dog's back.</p>
                <h4 id="header-3">Header 3</h4>
                <blockquote>
                    <p>This is a blockquote.</p>
                    <p>This is the second paragraph in the blockquote.</p>
                    <h3 id="this-is-an-h2-in-a-blockquote">
                        This is an H2 in a blockquote</h3>
                </blockquote>
                """))

    # TODO: don't know how to fake an ImportError.
    #       Excluded in tests.settings.COVERAGE_CODE_EXCLUDES.
    #
    # def test_no_markdown(self):
    #     """If markdown is not installed, the converter will just not be
    #     available.

    #     """
    #     # first, remove already registered markdown converter
    #     markup_pool.unregister_markup('markdown')
    #     self.assertRaises(KeyError, markup_pool.get_markup, 'markdown')

    #     # trying to import markdown fails
    #     with self.assertRaises(ImportError):
    #         from markdown import Markdown

    #     # now try to re-register by importing markdown_ module
    #     # this tries to import markdown and fails silently
    #     from markupmirror.markup import markdown_

    #     # markdown should not be found
    #     self.assertRaises(KeyError, markup_pool.get_markup, 'markdown')

    #     # re-register markdown to restore default state
    #     register_markup(MarkdownMarkup)


__all__ = ('MarkdownMarkupTests',)

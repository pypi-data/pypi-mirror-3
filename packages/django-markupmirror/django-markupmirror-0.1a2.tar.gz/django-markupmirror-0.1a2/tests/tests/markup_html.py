from django.test import TestCase

from markupmirror.markup.html import HtmlMarkup


MARKUP = u"""\
<h1>A First Level Header</h1>

<h2>A Second Level Header</h2>

<p>Now is the time for all good men to come to the aid of their country.<br />
This is just a regular paragraph.</p>

<p>The quick brown fox jumped over the lazy dog's back.</p>

<h3>Header 3</h3>

<blockquote>
    <p>This is a blockquote.</p>
    <p>This is the second paragraph in the blockquote.</p>
</blockquote>
"""


class HTMLMarkupTests(TestCase):
    """Tests the ``markupmirror.markup.html.HtmlMarkup`` class that
    passes through plain HTML content.

    """
    def test_convert(self):
        """The ``HtmlMarkup`` converter does not do anything."""
        html_markup = HtmlMarkup()
        self.assertHTMLEqual(html_markup(MARKUP), MARKUP)


__all__ = ('HTMLMarkupTests',)

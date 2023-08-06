import textwrap

from django.test import TestCase

from markupmirror.markup.textile_ import TextileMarkup


MARKUP = u"""\
h1. A First Level Header

h2. A Second Level Header

Now is the time for all good men to come to the aid of their country.
This is just a regular paragraph.

The quick brown fox jumped over the lazy dog's back.

h3. Header 3

bq. This is a blockquote.
This is the second paragraph in the blockquote.
"""


class TextileMarkupTests(TestCase):
    """Tests the ``markupmirror.markup.textile_.TextileMarkup`` class that
    converts Textile content to HTML.

    """
    def test_convert(self):
        """The ``TextileMarkup`` converter uses textile to convert Textile
        markup to HTML.

        """
        textile_markup = TextileMarkup()
        self.assertHTMLEqual(
            textile_markup(MARKUP),
            textwrap.dedent(u"""\
                <h1>A First Level Header</h1>

                <h2>A Second Level Header</h2>

                <p>Now is the time for all good men to come to the aid of
                    their country.<br />
                    This is just a regular paragraph.</p>

                <p>The quick brown fox jumped over the lazy dog&#8217;s back.
                    </p>

                <h3>Header 3</h3>

                <blockquote>
                    <p>This is a blockquote.<br />
                    This is the second paragraph in the blockquote.</p>
                </blockquote>
                """))


__all__ = ('TextileMarkupTests',)

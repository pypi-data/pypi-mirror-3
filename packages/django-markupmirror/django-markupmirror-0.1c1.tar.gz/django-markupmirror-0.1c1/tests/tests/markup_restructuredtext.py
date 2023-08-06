import textwrap

from django.test import TestCase

from markupmirror.markup.restructuredtext import ReStructuredTextMarkup


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

Header 3
^^^^^^^^

    This is a blockquote.

    This is the second paragraph in the blockquote.
"""


class ReStructuredTextMarkupTests(TestCase):
    """Tests the
    ``markupmirror.markup.restructuredtext.ReStructuredTextMarkup`` class that
    converts reStructuredText content to HTML.

    """
    def test_convert(self):
        """The ``ReStructuredTextMarkup`` converter uses docutils to convert
        reStructuredText markup to HTML.

        """
        restructuredtext_markup = ReStructuredTextMarkup()
        self.assertHTMLEqual(
            restructuredtext_markup(MARKUP),
            textwrap.dedent(u"""\
                <div class="document" id="a-first-level-header">
                    <h1 class="title">A First Level Header</h1>
                    <h2 class="subtitle" id="a-second-level-header">
                        A Second Level Header</h2>
                    <p>Now is the time for all good men to come to
                        the aid of their country. This is just a
                        regular paragraph.</p>
                    <p>The quick brown fox jumped over the lazy dog's back.</p>
                    <div class="section" id="header-3">
                        <h1>Header 3</h1>
                        <blockquote>
                            <p>This is a blockquote.</p>
                            <p>This is the second paragraph in the blockquote.
                                </p>
                        </blockquote>
                    </div>
                </div>
                """))


__all__ = ('ReStructuredTextMarkupTests',)

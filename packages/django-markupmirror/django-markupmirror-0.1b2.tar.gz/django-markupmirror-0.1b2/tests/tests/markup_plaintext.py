import textwrap

from django.test import TestCase

from markupmirror.markup.plaintext import PlainTextMarkup


MARKUP = u"""\
This is some plaintext markup.
It includes http://www.domain.com/ links and

also some linebreaks.
"""


class PlainTextMarkupTests(TestCase):
    """Tests the ``markupmirror.markup.plaintext.PlainTextMarkup`` class that
    does simple conversion of linebreaks and URLs.

    """

    def test_convert(self):
        """The ``PlaintextMarkup`` converter uses ``urlize`` and ``linebreaks``
        to convert URLs to anchors and linebreaks to paragraphs.

        """
        plaintext_markup = PlainTextMarkup()
        self.assertHTMLEqual(
            plaintext_markup(MARKUP),
            textwrap.dedent(u"""\
                <p>This is some plaintext markup.<br />
                It includes <a href="http://www.domain.com/">
                    http://www.domain.com/</a> links and</p>
                <p>also some linebreaks.<br /></p>
                """))


__all__ = ('PlainTextMarkupTests',)

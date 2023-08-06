from django.http import HttpResponse
from django.http import HttpResponseNotAllowed
from django.test import TestCase
from django.core.urlresolvers import reverse


class MarkupPreviewViewTests(TestCase):
    """Tests the ``markupmirror.views.MarkupPreview`` view implementation."""

    def test_url(self):
        """Tests that the markupmirror namespace is being registered and
        the preview URL can be resolved correctly.

        """
        self.assertEqual(reverse('markupmirror:preview'),
                         '/markupmirror/preview/')

    def test_post_only(self):
        """The preview view may only be used via POST to make sure text won't
        be truncated or the like.

        """
        url = reverse('markupmirror:preview')
        self.assertIsInstance(self.client.get(url), HttpResponseNotAllowed)
        self.assertIsInstance(self.client.post(url, {
                'text': "**markup**",
                'markup_type': 'plaintext'
            }), HttpResponse)


__all__ = ('MarkupPreviewViewTests',)

from django.test import TestCase

import markupmirror


class VersionTests(TestCase):
    """Tests the version information tools in ``markupmirror.__init__``."""

    def setUp(self):
        self.original_version = markupmirror.VERSION_INFO
        markupmirror.VERSION_INFO = {
            'major': 1,
            'minor': 3,
            'micro': 0,
            'sub': 'final',
            'serial': 1
        }

    def tearDown(self):
        markupmirror.VERSION_INFO = self.original_version

    def test_definitions(self):
        """Tests that the module-level definitions in ``markupmirror.__ini__``
        work. (This is mainly for coverage)

        """
        import sys
        del sys.modules['markupmirror']
        import markupmirror
        self.assertTrue(hasattr(markupmirror, 'VERSION_INFO'))
        self.assertTrue(hasattr(markupmirror, 'get_version'))
        self.assertTrue(hasattr(markupmirror, '__version__'))

    def test_get_version(self):
        """Tests if ``markupmirror.get_version`` returns the correct dotted
        version string depending on the settings in ``VERSION_INFO``.

        """
        self.assertEqual(markupmirror.get_version(), '1.3')
        # add a micro version
        markupmirror.VERSION_INFO['micro'] = 7
        self.assertEqual(markupmirror.get_version(), '1.3.7')
        # alpha, beta, candidate or final versions with serial numbers
        markupmirror.VERSION_INFO['sub'] = 'alpha'
        markupmirror.VERSION_INFO['serial'] = 2
        self.assertEqual(markupmirror.get_version(), '1.3.7a2')
        markupmirror.VERSION_INFO['sub'] = 'beta'
        markupmirror.VERSION_INFO['serial'] = 1
        self.assertEqual(markupmirror.get_version(), '1.3.7b1')
        markupmirror.VERSION_INFO['sub'] = 'candidate'
        markupmirror.VERSION_INFO['serial'] = 3
        self.assertEqual(markupmirror.get_version(), '1.3.7c3')
        markupmirror.VERSION_INFO['sub'] = 'final'
        markupmirror.VERSION_INFO['serial'] = 1
        self.assertEqual(markupmirror.get_version(), '1.3.7')

    def test_get_short_version(self):
        """``get_version(short=True)`` should only ever return major and minor
        version.

        """
        self.assertEqual(markupmirror.get_version(short=True), '1.3')

    def test_invalid_sub_or_serial(self):
        """``VERSION_INFO['sub']`` must be one of alpha, beta, candidate or
        final; ``VERSION_INFO['serial']`` must be an integer >= 1.

        """
        # invalid sub
        markupmirror.VERSION_INFO['sub'] = 'betta'
        markupmirror.VERSION_INFO['serial'] = 1
        self.assertRaises(AssertionError, markupmirror.get_version)
        # invalid serial
        markupmirror.VERSION_INFO['sub'] = 'beta'
        markupmirror.VERSION_INFO['serial'] = '1'
        self.assertRaises(AssertionError, markupmirror.get_version)

    def test_invalid_major_minor_micro(self):
        """``VERSION_INFO['major|minor|micro']`` must be integers."""
        # invalid major
        markupmirror.VERSION_INFO['major'] = 'one'
        self.assertRaises(AssertionError, markupmirror.get_version)
        # invalid minor
        markupmirror.VERSION_INFO['minor'] = 'three'
        self.assertRaises(AssertionError, markupmirror.get_version)
        # invalid micro
        markupmirror.VERSION_INFO['micro'] = 'seven'
        self.assertRaises(AssertionError, markupmirror.get_version)


__all__ = ('VersionTests',)

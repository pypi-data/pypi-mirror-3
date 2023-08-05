import unittest

from pysemver import SemVer


class SemVerTestCase(unittest.TestCase):

    def setUp(self):
        self.valid_versions = ['1.4.2',
                               '1.4.2-alpha',
                               '1.4.2-alpha.1',
                               '1.4.2-alpha.12',
                               '1.4.2-alpha.12+build',
                               '1.4.2-alpha.12+build.3',
                               '1.4.2-alpha.12+build.37',
                               '1.4.2-alpha.12+build.37.ea85f673',
                               '1.4.2+build.37.ea85f673',
                               '1.4.2+build']

        self.invalid_versions = ['1.4',
                                 '1.4.',
                                 '1.4 .2',
                                 '1.4.2.',
                                 '1.4.2-',
                                 '1.4.2-alpha.',
                                 '1.4.2 -alpha',
                                 '1.4.2+build.37.ea85f673-alpha.12']

    def test_valid_versions(self):
        [self.assertTrue(SemVer.is_valid(x), msg=x) for x in self.valid_versions]

    def test_invalid_version(self):
        [self.assertFalse(SemVer.is_valid(x), msg=x) for x in self.invalid_versions]

    def test_init(self):
        v = SemVer()
        self.assertEqual(v.major, 0)
        self.assertEqual(v.minor, 0)
        self.assertEqual(v.patch, 0)
        self.assertIsNone(v.prerelease)
        self.assertIsNone(v.build)

    def test_init_from_string_success(self):
        v = SemVer('1.4.2-alpha.1+build.24')
        self.assertIsNotNone(v)
        self.assertEqual(v.major, 1)
        self.assertEqual(v.minor, 4)
        self.assertEqual(v.patch, 2)
        self.assertEqual(v.prerelease, 'alpha.1')
        self.assertEqual(v.build, 'build.24')

    def test_init_from_string_fail(self):
        with self.assertRaises(ValueError):
            SemVer('1.4.2+')


if __name__ == '__main__':
    unittest.main(verbosity=2)

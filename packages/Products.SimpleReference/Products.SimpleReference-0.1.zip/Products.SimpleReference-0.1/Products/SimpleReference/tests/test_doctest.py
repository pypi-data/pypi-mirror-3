from Products.SimpleReference.tests import base
from Testing import ZopeTestCase as ztc
import doctest
import unittest


def test_suite():

    filenames = [
        'content/file.txt',
        'content/image.txt',
    ]
    tests = []

    for filename in filenames:
        tests.append(ztc.ZopeDocFileSuite(
            filename, package='Products.SimpleReference',
            test_class=base.FunctionalTestCase,
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE |
                doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))

    return unittest.TestSuite(tests)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

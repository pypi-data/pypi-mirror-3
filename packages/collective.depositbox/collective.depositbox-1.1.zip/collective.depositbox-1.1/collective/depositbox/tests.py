import doctest
import unittest

from zope.testing import doctestunit
from zope.component import testing

"""
from Testing import ZopeTestCase as ztc

from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import collective.depositbox


class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            ztc.installPackage(collective.depositbox)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass
"""


def test_suite():
    return unittest.TestSuite([

        # Unit tests
        doctestunit.DocFileSuite(
            'README.txt', package='collective.depositbox',
            setUp=testing.setUp, tearDown=testing.tearDown,
            optionflags=doctest.ELLIPSIS),

        #doctestunit.DocTestSuite(
        #    module='collective.depositbox.mymodule',
        #    setUp=testing.setUp, tearDown=testing.tearDown),


        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='collective.depositbox',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='collective.depositbox',
        #    test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

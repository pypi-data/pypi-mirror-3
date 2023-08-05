import unittest
from Testing import ZopeTestCase as ztc
from collective.editskinswitcher.tests import base


def test_suite():
    return unittest.TestSuite([

        # Integration tests that use PloneTestCase and use the
        # functional test browser.
        ztc.ZopeDocFileSuite(
            'tests/force_login.txt',
            package='collective.editskinswitcher',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/ssl_switch.txt',
            package='collective.editskinswitcher',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/need_authentication.txt',
            package='collective.editskinswitcher',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/ploneadmin_header.txt',
            package='collective.editskinswitcher',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/preview.txt',
            package='collective.editskinswitcher',
            test_class=base.BaseFunctionalTestCase),

        ztc.ZopeDocFileSuite(
            'tests/specific_switch.txt',
            package='collective.editskinswitcher',
            test_class=base.BaseFunctionalTestCase),

        ])

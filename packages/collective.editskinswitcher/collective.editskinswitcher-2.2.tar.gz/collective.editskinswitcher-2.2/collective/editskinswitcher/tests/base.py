import logging
from Testing import ZopeTestCase as ztc
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml
from Products.Five import fiveconfigure
from ZPublisher import HTTPRequest

import collective.editskinswitcher
from collective.editskinswitcher.tests.utils import new_default_skin

logger = logging.getLogger('collective.editskinswitcher')


def get_header(self, name, default=None):
    """Return the named HTTP header, or an optional default
    argument or None if the header is not found. Note that
    both original and CGI-ified header names are recognized,
    e.g. 'Content-Type', 'CONTENT_TYPE' and 'HTTP_CONTENT_TYPE'
    should all return the Content-Type header, if available.

    CHANGED from original:

    For testing, we first try the default behaviour.  When that fails
    we try to get the name from the request variables.  The reason is
    that it is rather hard to mock an extra header like X_FORCE_LOGIN.
    """
    original = self.old_get_header(name, default=default)
    if original is default:
        val = self.get(name, default=default)
        if val is not None:
            return val
    return original


HTTPRequest.HTTPRequest.old_get_header = HTTPRequest.HTTPRequest.get_header
HTTPRequest.HTTPRequest.get_header = get_header
logger.info('Patched ZPublisher.HTTPRequest.HTTPRequest.get_header for tests.')


@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    zcml.load_config('configure.zcml',
                     collective.editskinswitcher)
    fiveconfigure.debug_mode = False
    ztc.installPackage('collective.editskinswitcher')


class BaseTestCase(ptc.PloneTestCase):
    """Base class for test cases.
    """

    def setUp(self):
        super(BaseTestCase, self).setUp()
        # Create new skin based on Plone Default and make this the
        # default skin.
        new_default_skin(self.portal)


class BaseFunctionalTestCase(ptc.FunctionalTestCase):
    """Base class for test cases.
    """

    def setUp(self):
        super(BaseFunctionalTestCase, self).setUp()
        # Create new skin based on Plone Default and make this the
        # default skin.
        new_default_skin(self.portal)


setup_product()
ptc.setupPloneSite(products=['collective.editskinswitcher'])

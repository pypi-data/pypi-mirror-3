# -*- coding: utf-8 -*-

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc

from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.setup import default_password
from Products.PloneTestCase.layer import onsetup


@onsetup
def setup_package():

    fiveconfigure.debug_mode = True
    import collective.portletpage
    zcml.load_config('configure.zcml', collective.portletpage)
    fiveconfigure.debug_mode = False

    ztc.installPackage('collective.portletpage')

setup_package()
ptc.setupPloneSite(products=['collective.portletpage'])


class TestCase(ptc.PloneTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """


class FunctionalTestCase(ptc.FunctionalTestCase):
    """We use this base class for all the tests in this package. If necessary,
    we can put common utility or setup code in here.
    """

    def afterSetUp(self):
        self.portal.portal_membership.addMember('uber',
                                                default_password,
                                                ('Member', 'Manager'), [])


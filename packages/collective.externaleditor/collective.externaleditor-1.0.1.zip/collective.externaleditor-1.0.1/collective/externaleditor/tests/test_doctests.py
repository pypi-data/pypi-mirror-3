import doctest
from unittest import TestSuite

from Products.PloneTestCase.PloneTestCase import setupPloneSite
from Testing.ZopeTestCase import FunctionalDocFileSuite

from plone.app.controlpanel.tests.cptc import ControlPanelTestCase

setupPloneSite()

OPTIONFLAGS = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suite = TestSuite()

    suite.addTest(FunctionalDocFileSuite('controlpanel.txt',
        optionflags=OPTIONFLAGS,
        package="collective.externaleditor.tests",
        test_class=ControlPanelTestCase))

    return suite

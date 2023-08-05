import logging

from zope import event

from Products.Archetypes.event import ObjectInitializedEvent
from Products.Archetypes.utils import shasattr

from slc.seminarportal.tests.base import SeminarPortalTestCase

log = logging.getLogger('test_seminar.py')

class TestSeminar(SeminarPortalTestCase):

    def afterSetUp(self):
        """ Create a Seminar object, and call the relevant event to enable the
            auto-creation of the sub-objects ('speakers', 'speech venues').
        """
        self.loginAsPortalOwner()
        portal = self.portal
        portal.invokeFactory('SPSeminar', 'plone-conference', title="Seminar")
        seminar = getattr(portal, 'plone-conference')
        seminar._renameAfterCreation(check_auto_id=True)
        event.notify(ObjectInitializedEvent(seminar))
        self.seminar = seminar


    def test_subfolders_created(self):
        """ Test for the succesful automatic creation of subfolders.
        """
        portal = self.portal
        seminar = getattr(portal, 'plone-conference')

        # Check that subflolders are created.
        self.failUnlessEqual(shasattr(seminar, 'speakers'), True)
        self.failUnlessEqual(shasattr(seminar, 'speech-venues'), True)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestSeminar))
    return suite


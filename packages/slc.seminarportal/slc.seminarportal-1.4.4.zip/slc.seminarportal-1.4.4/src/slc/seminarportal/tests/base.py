import logging
import random

from DateTime import DateTime
from Testing import ZopeTestCase as ztc

from plone.browserlayer import utils as browserlayerutils

from Products.CMFCore.utils import getToolByName
from Products.Five import fiveconfigure
from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from slc.seminarportal.config import names
from slc.seminarportal.config import titles
from slc.seminarportal.config import desc
from slc.seminarportal.config import short_desc

from slc.seminarportal.utils import create_speech
from slc.seminarportal.interfaces import IThemeLayer

log = logging.getLogger('tests/base.py')

ztc.installProduct('Relations')
ztc.installProduct('LinguaPlone')

PRODUCTS = [
        'Relations', 
        'LinguaPlone', 
        'slc.seminarportal'
        ]
ptc.setupPloneSite(products=PRODUCTS)

class SeminarPortalTestCase(ptc.PloneTestCase):
    """Base class used for test cases
    """
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            import slc.seminarportal
            zcml.load_config('configure.zcml', slc.seminarportal)
            fiveconfigure.debug_mode = False
            ztc.installPackage('slc.seminarportal');

            browserlayerutils.register_layer(
                                    IThemeLayer,
                                    name="slc.seminarportal.browserlayer" 
                                    )

    def create_speakers(self, seminar):
        """ Create test speakers
        """
        speakers_folder = getattr(seminar, 'speakers')
        for surname, firstname in names:
            speaker_id = seminar.generateUniqueId('SPSpeaker')
            speakers_folder.invokeFactory('SPSpeaker', 
                                speaker_id,)
            s = getattr(speakers_folder, speaker_id)
            s._renameAfterCreation(check_auto_id=True)
            s.setLastName(surname)
            s.setFirstName(firstname)


    def create_speech_venues(self, seminar):
        """ """
        wftool = getToolByName(seminar, 'portal_workflow')
        speech_venues_folder = getattr(seminar, 'speech-venues')
        for i in ['A', 'B']:
            log.info('Creating venue: %s' % i)
            speech_folder_id = 'speech_venue_%s' % i.lower()
            speech_venues_folder.invokeFactory(
                                        'SPSpeechVenue', 
                                        speech_folder_id, 
                                        title='Speech Venue %s' % i, 
                                        description=short_desc
                                        )

            speech_folder = getattr(speech_venues_folder, speech_folder_id)
            wftool.doActionFor(speech_folder, 'publish')


    def create_speeches(self, seminar):
        """ """
        speech_venues = getattr(seminar, 'speech-venues').objectValues()
        speakers = getattr(seminar, 'speakers').objectValues()
        seminar_day = DateTime() + 10
        for venue in speech_venues:
            for days in [0,1,2]:
                for title in titles:
                    speech_title = 'Speech: %s' % title
                    start_hour = random.randint(6, 20)
                    end_hour = start_hour + random.randint(0,3)
                    start_date = DateTime('%s %s:%s ' % ((seminar_day+days).Date(), start_hour, random.randint(0,30)))
                    end_date = DateTime('%s %s:%s' % ((seminar_day+days).Date(), end_hour, random.randint(30,59)))
                    speech = create_speech(venue, speech_title, desc, start_date, end_date)
                    speech_speakers = []
                    for i in range(0,2):
                        rand_index = random.randint(0, len(speakers)-1)
                        speaker = speakers[rand_index]
                        speech_speakers.append(speaker)
                    speech.setSpeakers(speech_speakers)
                    speech.reindexObject()



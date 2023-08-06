from django.conf import settings
from django.test import TestCase
from ccpages import settings as c_settings
from ccpages.tests.mock import MockRequest
from ccpages.views import index


class SettingsTest(TestCase):

    def test_default_status(self):
        """default status"""
        original = getattr(settings, 'CCPAGES_DEFAULT_STATUS', None)
        # defaults to 1
        self.assertEqual(1, c_settings.CCPAGES_DEFAULT_STATUS)
        # make it 0 
        settings.CCPAGES_DEFAULT_STATUS = 0
        reload(c_settings)
        self.assertEqual(0, c_settings.CCPAGES_DEFAULT_STATUS)
        # revert it
        setattr(settings, 'CCPAGES_DEFAULT_STATUS', original)

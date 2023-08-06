from decimal import Decimal
from django.test import TestCase
from ccpages.forms import PagePasswordForm
from ccpages.models import Page


class ListenerTestCases(TestCase):

    def test_hash_if_password(self):
        """A hash is generated on save if page has password"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'ha'
        page1.status = Page.VISIBLE
        page1.save()
        # get the page
        p = Page.objects.get(pk=page1.pk)
        # we have a hash
        self.assertEqual(
                p.hash,
                'f9fc27b9374ad1e3bf34fdbcec3a4fd632427fed')
    
    def test_hash_if_no_password(self):
        """A hash is not generated on save if page has no password"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # get the page
        p = Page.objects.get(pk=page1.pk)
        # we have no hash
        self.assertFalse(p.hash)

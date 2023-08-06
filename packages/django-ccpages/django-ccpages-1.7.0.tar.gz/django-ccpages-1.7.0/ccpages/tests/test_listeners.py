import os
from unittest import skipUnless
from decimal import Decimal
from django.test import TestCase
from django.conf import settings
from django.core.files import File
from ccpages.forms import PagePasswordForm
from ccpages.models import Page, PageAttachment

class ListenerTestCases(TestCase):

    @skipUnless(os.path.exists('%s/ccpages/test.pdf' % settings.STATIC_ROOT),
            'test.pdf file does not exist')
    def test_title(self):
        """A title is set on a file from filename is none is supplied"""
        # open file
        test_pdf = open('%s/ccpages/test.pdf' % settings.STATIC_ROOT)
        # make page and attachment
        p1 = Page()
        p1.title = '1'
        p1.slug = '1'
        p1.content = '# Hello World'
        p1.order = Decimal('1')
        p1.password = 'ha'
        p1.status = Page.VISIBLE
        p1.save()
        at1 = PageAttachment()
        at1.page = p1
        at1.src = File(test_pdf, 'ccpages/test.pdf')
        at1.save()
        # the title is 'test.pdf'
        self.assertEqual(at1.title, 'test.pdf')
        test_pdf.close()
        os.unlink(at1.src.path)
        # make another one, but this time with a title
        test_pdf = open('%s/ccpages/test.pdf' % settings.STATIC_ROOT)
        at2 = PageAttachment()
        at2.page = p1
        at2.src = File(test_pdf, 'ccpages/test.pdf')
        at2.title = 'Arther'
        at2.save()
        # title is now arther
        self.assertEqual(at2.title, 'Arther')
        # delete the files
        test_pdf.close()
        os.unlink(at2.src.path)

    def test_content_rendered(self):
        """When a page is saved the content is passed through
        markdown and saved as content_rendered"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '# Hello World'
        page1.order = Decimal('1')
        page1.password = 'ha'
        page1.status = Page.VISIBLE
        page1.save()
        # we now have rendered content
        self.assertHTMLEqual(
                page1.content_rendered,
                '<h1 id="hello-world">\nHello World\n</h1>')

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

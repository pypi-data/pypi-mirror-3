import os
from decimal import Decimal
from unittest import skipUnless
from django.core.urlresolvers import reverse
from django.http import Http404
from django.test import TestCase
from ccpages.tests.mock import MockRequest
from ccpages.views import index, view, password
from ccpages.models import Page
from ccpages import settings as c_settings


layout_dir_exists = os.path.exists(c_settings.CUSTOM_LAYOUTS)



class ViewTestCases(TestCase):

    def setUp(self):
        # create a reqest factory
        self.rf = MockRequest()

    @skipUnless(layout_dir_exists, 'custom layout dir required')
    def test_custom_layout(self):
        """if a custom template is used in a template then
        that will be used to render the page"""
        # write out the test template
        layout_path = '%s/unittest.html' % c_settings.CUSTOM_LAYOUTS
        layout = open(layout_path, 'w')
        layout.write('hello world')
        layout.close()
        # now make the page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.layout = layout_path
        page1.save()
        # get the response and it is 'hello world'
        request = self.rf.get(reverse('ccpages:view', args=[1]))
        response = view(request, page1.slug)
        self.assertEqual('hello world', response.content)
        # remove the layout and it is not equal
        page1.layout = None
        page1.save()
        response = view(request, page1.slug)
        self.assertNotEqual('hello world', response.content)
        # delete the custom template
        os.unlink(layout_path)

    def test_password_404(self):
        """Any attempt to access a page that doesn't exist returns
        a 404 status code"""
        response = self.client.get(
                reverse('ccpages:password', args=['asd']))
        self.assertEqual(404, response.status_code)

    def test_password_200(self):
        """The password page responds with a 200 ok"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'wrng'
        page1.status = Page.VISIBLE
        page1.save()
        # make post request and we get a 200
        request = self.rf.get(
                reverse('ccpages:password', args=[page1.slug]))
        response = password(request, page1.slug)
        self.assertEqual(200, response.status_code)

    def test_password_post_incorrect_password(self):
        """When the incorrect password for a page is sent via post
        the users session is updated to include a hash that allows
        access"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'wrng'
        page1.status = Page.VISIBLE
        page1.save()
        # make post request and we get a 200
        request = self.rf.post(
                reverse('ccpages:password', args=[page1.slug]),
                {'password': 'billy-bo-django'})
        response = password(request, page1.slug)
        self.assertEqual(200, response.status_code)

    def test_password_post_correct_password(self):
        """When the correct password for a page is sent via post
        the users session is updated to include a hash that allows
        access"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'billy-bo-django'
        page1.status = Page.VISIBLE
        page1.save()
        # make request and we get a 302
        request = self.rf.post(
                reverse('ccpages:password', args=[page1.slug]),
                {'password': 'billy-bo-django'})
        response = password(request, page1.slug)
        self.assertEqual(302, response.status_code)
        # and now the session has the key and a hash in it
        self.assertEqual(
                request.session['ccpage_1_hash'],
                'c0b0f36ffdfe68518916a0ea9d8a89cd2b4bc586')

    def test_password_redirects_back_if_page_has_no_password(self):
        """if a page has no password and the user attempts to access
        the password page, they are redirected back"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make request and we get a 302
        request = self.rf.get(reverse('ccpages:password', args=[1]))
        response = password(request, page1.slug)
        self.assertEqual(302, response.status_code)
        self.assertEqual(
                response['Location'],
                reverse('ccpages:view', args=[page1.slug]))

    def test_index_no_pages_404(self):
        """if there are no pages then the index returns a 404"""
        request = self.rf.get(reverse('ccpages:index'))
        self.assertRaises(Http404, index, request)

    def test_index_200(self):
        """If there is a default then we get a nice 200"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make request and we get a 200
        request = self.rf.get(reverse('ccpages:index'))
        response = index(request)
        self.assertEqual(302, response.status_code)

    def test_view_404(self):
        """Any attempt to access a page that doesn't exist returns
        a 404 status code"""
        response = self.client.get(reverse('ccpages:view', args=['asd']))
        self.assertEqual(404, response.status_code)

    def test_view_with_correct_hash(self):
        """if a user visits a page with the correct hash in their
        session the view returns a 200 response"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'billy-bo-django'
        page1.status = Page.VISIBLE
        page1.save()
        # make request and we get a 200
        request = self.rf.get(reverse('ccpages:view', args=[page1.slug]))
        hash = 'c0b0f36ffdfe68518916a0ea9d8a89cd2b4bc586'
        request.session['ccpage_1_hash'] = hash
        response = view(request, page1.slug)
        self.assertEqual(200, response.status_code)

    def test_view_200(self):
        """A visible page with no password returns a 200"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make request and we get a 200
        request = self.rf.get(reverse('ccpages:view', args=[1]))
        response = view(request, page1.slug)
        self.assertEqual(200, response.status_code)

    def test_view_password_redirects(self):
        """If there is a page with a password and the user isn't
        authed to view it then it redirects to the view view, but
        with a different url"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.password = 'la-ritournelle'
        page1.save()
        # make request and we get a 302
        request = self.rf.get(reverse('ccpages:view', args=[1]))
        response = view(request, page1.slug)
        self.assertEqual(302, response.status_code)
        self.assertEqual(
                response['Location'],
                reverse('ccpages:password', args=[page1.slug]))

from decimal import Decimal
from django.test import TestCase
from ccpages.forms import PagePasswordForm
from ccpages.models import Page


class PageFormTestCases(TestCase):

    def test_silent_fail_if_no_page_supplied(self):
        """If no page is supplied to the form then the KeyError
        is silent"""
        form = PagePasswordForm()

    def test_supply_incorrect_password_and_form_is_invalid(self):
        """If we supply the incorrect password to the form then the
        form will not validate"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'ha'
        page1.status = Page.VISIBLE
        page1.save()
        # make the data
        data = {'password': 'wrong'}
        # make the form
        form = PagePasswordForm(data, page=page1)
        # form is not valid
        self.assertFalse(form.is_valid())

    def test_supply_correct_password_and_form_has_a_hash(self):
        """If we supply the correct password to the form then the
        form will save the hash value"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'ha'
        page1.status = Page.VISIBLE
        page1.save()
        # make the data
        data = {'password': 'ha'}
        # make the form
        form = PagePasswordForm(data, page=page1)
        form.is_valid()
        # form has a hash
        self.assertTrue(form.hash)

    def test_supply_correct_password_and_form_is_valid(self):
        """If we supply the correct password to the form then the
        form will validate"""
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.password = 'ha'
        page1.status = Page.VISIBLE
        page1.save()
        # make the data
        data = {'password': 'ha'}
        # make the form
        form = PagePasswordForm(data, page=page1)
        # form is valid
        self.assertTrue(form.is_valid())


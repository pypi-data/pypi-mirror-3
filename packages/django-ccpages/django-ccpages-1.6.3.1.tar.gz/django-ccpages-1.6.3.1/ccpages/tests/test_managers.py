from decimal import Decimal
from django.test import TestCase
from ccpages.models import Page


class ManagerTestCases(TestCase):


    def test_navbreadcrumbs(self):
        """The navbreadcrums method returns all visible decendants of
        a page all the way to the root"""
        # make 1 page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make 2 page
        page2 = Page()
        page2.title = '2'
        page2.slug = '2'
        page2.content = '2'
        page2.order = Decimal('2')
        page2.status = Page.VISIBLE
        page2.parent = page1
        page2.save()
        # make 3 page
        page3 = Page()
        page3.title = '3'
        page3.slug = '3'
        page3.content = '3'
        page3.order = Decimal('3')
        page3.status = Page.HIDDEN
        page3.parent = page1
        page3.save()
        # make 4 page
        page4 = Page()
        page4.title = '4'
        page4.slug = '4'
        page4.content = '4'
        page4.order = Decimal('4')
        page4.status = Page.VISIBLE
        page4.parent = page1
        page4.save()
        # make 5 page
        page5 = Page()
        page5.title = '5'
        page5.slug = '5'
        page5.content = '5'
        page5.order = Decimal('5')
        page5.status = Page.VISIBLE
        page5.save()
        # get the breadcrumb for page1
        p1_bc = Page.objects.nav_breadcrumbs(page1)
        # none because its a root
        self.assertEqual(0, p1_bc.count())
        # get page4
        p4_bc = Page.objects.nav_breadcrumbs(page4)
        self.assertEqual(1, p4_bc.count())
        # now make them all decendants of each other
        page3.parent = page2
        page3.save()
        page4.parent = page3
        page4.save()
        page5.parent = page4
        page5.save()
        # get page5
        p5_bc = Page.objects.nav_breadcrumbs(page5)
        # now only three in length because page 3 is hidden
        self.assertEqual(3, p5_bc.count())

    def test_navglobal(self):
        """the navglobal method returns all visible children of the
        root of a parent in the correct order"""
        # make 1 page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make 2 page
        page2 = Page()
        page2.title = '2'
        page2.slug = '2'
        page2.content = '2'
        page2.order = Decimal('2')
        page2.status = Page.VISIBLE
        page2.save()
        # make 3 page
        page3 = Page()
        page3.title = '3'
        page3.slug = '3'
        page3.content = '3'
        page3.order = Decimal('3')
        page3.status = Page.HIDDEN
        page3.save()
        # there will be two return by the manager methor
        nav = Page.objects.nav_global()
        self.assertEqual(2, nav.count())
        # make page 3 visible and now we have three
        page3.status = Page.VISIBLE
        page3.save()
        nav = Page.objects.nav_global()
        self.assertEqual(3, nav.count())


    def test_nav_local(self):
        """the nav_local method returns all visible children of the
        root of a parent in the correct order"""
        # make 1 page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make 2 page
        page2 = Page()
        page2.title = '2'
        page2.slug = '2'
        page2.content = '2'
        page2.order = Decimal('2')
        page2.status = Page.VISIBLE
        page2.parent = page1
        page2.save()
        # make 3 page
        page3 = Page()
        page3.title = '3'
        page3.slug = '3'
        page3.content = '3'
        page3.order = Decimal('3')
        page3.status = Page.HIDDEN
        page3.parent = page1
        page3.save()
        # make 4 page
        page4 = Page()
        page4.title = '4'
        page4.slug = '4'
        page4.content = '4'
        page4.order = Decimal('4')
        page4.status = Page.VISIBLE
        page4.parent = page1
        page4.save()
        # make 5 page
        page5 = Page()
        page5.title = '5'
        page5.slug = '5'
        page5.content = '5'
        page5.order = Decimal('5')
        page5.status = Page.VISIBLE
        page5.save()
        # the local nav for page 5 is empty
        p5_nav = Page.objects.nav_local(page5)
        self.assertEqual(0, p5_nav.count())
        # the local nav for p4 has 2 pages because one p3 is hidden
        p4_nav = Page.objects.nav_local(page4)
        self.assertEqual(2, p4_nav.count())
        # give page2 a lower order and now p4 is first
        page2.order = Decimal('100')
        page2.save()
        p2_nav = Page.objects.nav_local(page2)
        self.assertEqual(p2_nav[0].pk, page4.pk)
        self.assertEqual(p2_nav[1].pk, page2.pk)
        # make p4 orders waaay lower
        page4.order = Decimal('3000')
        page4.save()
        p4_nav = Page.objects.nav_local(page4)
        self.assertEqual(p4_nav[0].pk, page2.pk)
        self.assertEqual(p4_nav[1].pk, page4.pk)
    def test_visible(self):
        """The visible method returns only visible items"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.HIDDEN
        page1.save()
        # make another page
        page2 = Page()
        page2.title = '2'
        page2.slug = '2'
        page2.content = '2'
        page2.status = Page.VISIBLE
        page2.save()
        # the default page is the first one
        self.assertEqual(1, Page.custom.visible().count())
        # make the first one visible and we have a new default
        page1.status = Page.VISIBLE
        page1.save()
        self.assertEqual(2, Page.custom.visible().count())

    def test_default(self):
        """The default method of the custom manager returns the 
        instance with the highest order"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.VISIBLE
        page1.save()
        # make another page
        page2 = Page()
        page2.title = '2'
        page2.slug = '2'
        page2.content = '2'
        page2.status = Page.VISIBLE
        page2.save()
        # the default page is the first one
        default = Page.custom.default()
        self.assertEqual(default.pk, page1.pk)

    def test_default_page_must_be_visible(self):
        """The default page must be visible"""
        # make a page
        page1 = Page()
        page1.title = '1'
        page1.slug = '1'
        page1.content = '1'
        page1.order = Decimal('1')
        page1.status = Page.HIDDEN
        page1.save()
        # make another page
        page2 = Page()
        page2.title = '2'
        page2.slug = '2'
        page2.content = '2'
        page2.status = Page.VISIBLE
        page2.save()
        # the default page is the first one
        default = Page.custom.default()
        self.assertEqual(default.pk, page2.pk)
        # make the first one visible and we have a new default
        page1.status = Page.VISIBLE
        page1.save()
        default = Page.custom.default()
        self.assertEqual(default.pk, page1.pk)


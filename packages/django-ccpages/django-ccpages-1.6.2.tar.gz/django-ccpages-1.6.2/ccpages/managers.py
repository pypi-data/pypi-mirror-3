from django.db import models


class PagesManager(models.Manager):


    def default(self):
        """returns the lowest ordered page as the default"""
        try:
            return super(PagesManager, self)\
                    .get_query_set()\
                    .filter(status=self.model.VISIBLE)\
                    .order_by('order')[0]
        except IndexError:
            raise self.model.DoesNotExist

    def visible(self):
        """returns the visible pages"""
        return super(PagesManager, self)\
                .get_query_set()\
                .filter(status=self.model.VISIBLE)

    def nav_breadcrumbs(self, page):
        """returns the hierarchy of pages from a page to the root"""
        return page\
                .get_ancestors()\
                .filter(status=self.model.VISIBLE)

    def nav_global(self):
        """returns the visible root pages for use in the global 
        navigation"""
        return super(PagesManager, self)\
                .get_query_set()\
                .filter(
                        status=self.model.VISIBLE,
                        parent=None)

    def nav_local(self, page):
        """returns the children of the root node of the supplied
        page for use in local navigation"""
        return page\
                .get_root()\
                .get_children()\
                .filter(status=self.model.VISIBLE)\
                .order_by('order')


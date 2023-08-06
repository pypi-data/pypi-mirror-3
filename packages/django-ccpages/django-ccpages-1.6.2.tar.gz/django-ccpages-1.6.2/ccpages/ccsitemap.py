import ccsitemaps
from ccpages.models import Page


class PageSiteMap(ccsitemaps.SiteMap):
    model = Page

    @staticmethod
    def last_mod():
        try:
            last_mod = Page.objects\
                .visible()\
                .order_by('-modified')[0]
            return last_mod.modified
        except IndexError:
            return None

    @staticmethod
    def get_objects():
        return Page.objects.visible()


ccsitemaps.register(PageSiteMap)

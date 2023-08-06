from haystack import indexes
from haystack import site
from ccpages.models import Page

class PageIndex(indexes.SearchIndex):
    text = indexes.CharField(
            document=True,
            use_template=True)
    title = indexes.CharField(
            model_attr='title')
    description = indexes.CharField(
            model_attr='description')
    created = indexes.DateTimeField(
            model_attr='created')

    def index_queryset(self):
        return Page.objects.filter(
                password='',
                status=Page.VISIBLE)

site.register(Page, PageIndex)

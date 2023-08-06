from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from ccthumbs.fields import ImageWithThumbsField
from ccpages import settings as c_settings
from ccpages import listeners
from ccpages.managers import PagesManager


class Page(MPTTModel):
    """ The page model is a simple model designed to be used
    as the basis for a rudimentary cms"""
    VISIBLE = 1
    HIDDEN = 0
    STATUS_CHOICES = (
            (HIDDEN, 'Hidden'),
            (VISIBLE, 'Visible')
    )
    title = models.CharField(
            max_length=255)
    password = models.CharField(
            max_length=255,
            blank=True,
            null=True)
    hash = models.CharField(
            max_length=40,
            blank=True,
            null=True)
    slug = models.SlugField(
            unique=True)
    content = models.TextField()
    content_rendered = models.TextField(
            blank=True,
            null=True)
    parent = TreeForeignKey('self',
            blank=True,
            null=True,
            related_name='children')
    order = models.DecimalField(
            default=10.00,
            max_digits=8,
            decimal_places=2)
    status = models.PositiveSmallIntegerField(
            default=c_settings.CCPAGES_DEFAULT_STATUS,
            choices=STATUS_CHOICES)
    layout = models.CharField(
            choices=c_settings.CCPAGES_LAYOUTS,
            default='ccpages/view.html',
            max_length=255)
    created = models.DateTimeField(
            blank=True,
            null=True,
            auto_now_add=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)

    custom = PagesManager()

    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('ccpages:view', (),{
            'slug': self.slug})


    @property
    def description(self):
        return self.content_rendered[:100]

class PageImage(models.Model):
    page = models.ForeignKey(Page)
    url = models.CharField(
            blank=True,
            null=True,
            max_length=255)
    src = ImageWithThumbsField(
            upload_to='ccpages/%Y/%m/%d',
            sizes=c_settings.CCPAGES_IMAGE_SIZES)
    title = models.CharField(
            max_length=255,
            null=True,
            blank=True)
    order = models.DecimalField(
            default=10.00,
            max_digits=8,
            decimal_places=2)
    created = models.DateTimeField(
            blank=True,
            null=True,
            auto_now_add=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)


    class Meta:
        ordering = ['order']


    def __unicode__(self):
        return u'page image: %s' % self.pk

class PageAttachment(models.Model):
    page = models.ForeignKey(Page)
    src = models.FileField(
            upload_to='ccpages/%Y/%m/%d')
    title = models.CharField(
            max_length=255,
            null=True,
            blank=True)
    order = models.DecimalField(
            default=10.00,
            max_digits=8,
            decimal_places=2)
    created = models.DateTimeField(
            blank=True,
            null=True,
            auto_now_add=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)

    def __unicode__(self):
        return u'page attachment: %s' % self.pk


models.signals.pre_save.connect(
        listeners.set_attachment_title,
        sender=PageAttachment,
        dispatch_uid='ccpages_set_attachment_title')

models.signals.pre_save.connect(
        listeners.set_content_rendered,
        sender=Page,
        dispatch_uid='page_set_content_rendered')

models.signals.pre_save.connect(
        listeners.set_hash,
        sender=Page,
        dispatch_uid='page_set_hash')

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
    created = models.DateTimeField(
            blank=True,
            null=True,
            auto_now_add=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)

    custom = PagesManager()

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('ccpages:view', (),{
            'slug': self.slug})

class PageImage(models.Model):
    page = models.ForeignKey(Page)
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

    @property
    def name(self):
        filename = self.src.path.rsplit('/', 1)
        filename.reverse()
        return filename[0]

models.signals.pre_save.connect(
        listeners.create_hash,
        sender=Page,
        dispatch_uid='page_create_hash')

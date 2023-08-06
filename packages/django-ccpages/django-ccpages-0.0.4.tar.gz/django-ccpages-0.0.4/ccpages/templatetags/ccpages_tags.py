from django import template
from django.conf import settings
from ccpages.models import Page

register = template.Library()

@register.assignment_tag
def ccpages_nav_breadcrumbs(page):
    """returns a breadcrumb of pages for a given page"""
    return Page.objects.nav_breadcrumbs(page)

@register.assignment_tag
def ccpages_nav_global():
    """returns the global pages"""
    return Page.objects.nav_global()

@register.assignment_tag
def ccpages_nav_local(page):
    """returns the pages for a given page's root"""
    return Page.objects.nav_local(page)

@register.filter
def icon_for_attachment(attachment, size="small"):
    """based on the file extention this will return a suitable icon"""
    path, ext = attachment.src.path.rsplit('.', 1)
    document_name = path.rsplit('/', 1)
    document_name.reverse()

    if ext == 'docx':
        ext = 'doc'

    extentions = ('aac','ai','aiff','avi','bmp','c','cpp','css',
    'dat','dmg','doc','dotx','dwg','dxf','eps','exe','flv','gif',
    'h','hpp','html','ics','iso','java','jpg','key','mid','mp3',
    'mp4','mpg','odf','ods','odt','otp','ots','ott','pdf','php',
    'ppt','psd','py','qt','rar','rb','rtf','sql','tga','tgz',
    'tiff','txt','wav','xls','xlsx','xml','yml','zip')

    if ext in extentions:
        image = '%s/%s.png' % (size, ext)
    else:
        image = '%s/_blank.png' % size

    return '%sccpages/img/icons/%s' % (
            settings.STATIC_URL,
            image)

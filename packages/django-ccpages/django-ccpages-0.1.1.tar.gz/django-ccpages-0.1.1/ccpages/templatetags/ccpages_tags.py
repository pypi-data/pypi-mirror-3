from django import template
from django.conf import settings
from ccpages.models import Page

register = template.Library()

@register.inclusion_tag('ccpages/_js.html')
def ccpages_js():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.inclusion_tag('ccpages/_css.html')
def ccpages_css():
    return {
        'STATIC_URL': settings.STATIC_URL,
    }

@register.inclusion_tag('ccpages/_nav_breadcrumb.html')
def ccpages_nav_breadcrumbs(page):
    """returns a breadcrumb"""
    return {
        'pages': Page.objects.nav_breadcrumbs(page),
        'page': page,
    }

@register.inclusion_tag('ccpages/_nav_local.html')
def ccpages_nav_local(page):
    """returns the local nav for a given page's root"""
    return {
        'pages': Page.objects.nav_local(page)
    }


@register.assignment_tag
def ccpages_nav_global():
    """returns the global pages"""
    return Page.objects.nav_global()


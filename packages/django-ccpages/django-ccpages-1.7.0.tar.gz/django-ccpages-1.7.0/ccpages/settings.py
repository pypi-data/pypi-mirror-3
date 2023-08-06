from django.conf import settings

"""The default status for pages. 1 is visible and 0 is hidden"""
CCPAGES_DEFAULT_STATUS = getattr(
            settings,
            'CCPAGES_DEFAULT_STATUS',
            1)

"""Sizes for the images in the PageImage model"""
CCPAGES_IMAGE_SIZES = getattr(
        settings,
        'CCPAGES_IMAGE_SIZES',
        (   (140, 140),
            (240,160),
            (480,320),
            (960,640)))

CCPAGES_LAYOUTS = (
    ('ccpages/view.html', 'default'),
)
try:
    CCPAGES_LAYOUTS += settings.CCPAGES_LAYOUTS
except AttributeError:
    pass



"""Path to the custom layouts"""
try:
    layouts = settings.TEMPLATE_DIRS[0] + 'ccpages/layouts/'
except IndexError:
    layouts = None
CUSTOM_LAYOUTS = getattr(
        settings,
        'CCPAGES_CUSTOM_LAYOUTS',
        layouts)

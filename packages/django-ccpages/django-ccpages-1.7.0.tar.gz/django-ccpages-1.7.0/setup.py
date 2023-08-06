import os
from distutils.core import setup
from ccpages import get_version

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name="django-ccpages",
    version=get_version(),
    license = 'BSD 3 Clause',
    description='A lightweight pages application for Django',
    long_description=open('README.rst').read(),
    author='c&c',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccpages',
    package_data = {
        'ccpages' : [
            'templates/ccpages/*.html',
            'templates/search/indexes/ccpages/*.txt',
            'templates/ccpages/*.html',
            'static/ccpages/css/*.css',
            'static/ccpages/test.pdf',
            'static/ccpages/fancybox/source/*.gif',
            'static/ccpages/fancybox/source/*.png',
            'static/ccpages/fancybox/source/*.css',
            'static/ccpages/fancybox/source/*.js',
            'static/ccpages/fancybox/source/*.png',
            'static/ccpages/fancybox/source/helpers/*.png',
            'static/ccpages/fancybox/source/helpers/*.css',
            'static/ccpages/fancybox/source/helpers/*.js',
        ],
    },
    packages=[
        'ccpages',
        'ccpages.templatetags',
        'ccpages.tests',
        'ccpages.migrations'
    ],
    classifiers = [
        'Framework :: Django',],
    install_requires = [
        'django-mptt',
        'django-ccthumbs',
        'django-ccfiletypes',
        'django-writingfield',
        'markdown2'])

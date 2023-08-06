import os
from distutils.core import setup
from ccpages import VERSION

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

setup(
    name="django-ccpages",
    version=VERSION,
    license = 'BSD 3 Clause',
    description='A lightweight pages appliction for Django',
    long_description=open('README.rst').read(),
    author='c&c',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccpages',
    package_data = {
        'ccpages' : [
            'templates/ccpages/*.html',
            'static/ccpages/css/*.css',
            'static/ccpages/test.pdf',
        ],
    },
    packages=[
        'ccpages',
        'ccpages.templatetags',
        'ccpages.tests'
    ],
    install_requires = [
        'django-mptt',
        'django-ccthumbs',
        'django-ccfiletypes',
        'markdown'])

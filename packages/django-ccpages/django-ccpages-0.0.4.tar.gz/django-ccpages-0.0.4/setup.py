import os
from distutils.core import setup
from ccpages import VERSION


def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)

core_packages = [
    'ccpages',
]
for package in core_packages:
    for dirpath, dirnames, filenames in os.walk(package):
        # Ignore dirnames that start with '.'
        for i, dirname in enumerate(dirnames):
            if dirname.startswith('.'): del dirnames[i]
        if '__init__.py' in filenames:
            packages.append('.'.join(fullsplit(dirpath)))
        elif filenames:
            data_files.append(
                    [dirpath, [os.path.join(dirpath, f) for f in filenames]])


setup(
    name="django-ccpages",
    version=VERSION,
    license = 'BSD 3 Clause',
    description='A lightweight pages appliction for Django',
    author='c&c',
    author_email='studio@designcc.co.uk',
    url='https://github.com/designcc/django-ccpages',
    package_data = {
        'ccpages' : [
            'templates/ccpages/*.html',
        ],
    },
    packages=packages,
    data_files=data_files,
    install_requires = [
        'django-mptt',
        'django-ccthumbs',
        'markdown'])

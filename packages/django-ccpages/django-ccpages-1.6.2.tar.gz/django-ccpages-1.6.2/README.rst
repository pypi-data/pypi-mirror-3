About
==================================================

ccpages is a lightweight pages application.

Requirements
--------------------------------------------

- `Django`_ > 1.4
- `mptt`_
- `Markdown`_
- `ccfiletypes`_

Markdown, django-mptt and ccfiletypes will be installed if you don't already have them.

Quick Installation Instructions
--------------------------------------------

Install ccpages::

    pip install django-ccpages


Next add `ccpages` & `MPTT` to your installed apps::

    INSTALLED_APPS = (
         ...
        'ccpages',
        'mptt',
    )


`ccpages` requires `ccfiletypes`_ and this will be installed with pip. Make
sure that `ccfiletypes`_ is also in your installed apps. It only needs to be
once::

    INSTALLED_APPS = (
         ...
        'ccfiletypes',
    )

Wire it up to your root urls.py::

    urlpatterns += ('',
    ...
        ('^pages/', include('ccpages.urls', namespace='ccpages')),
    )

Then run syncdb::

    python manage.py syncdb


Finally you'll need to run the collectstatic command to get all of the static
files into your static root::

    python manage.py collectstatic


For full info please refer to the `documentation`_.

Features
==================================================

Password protected pages
----------------------------

Pages can be password protected with a password. The password is stored in
plain text and this mechanism is not meant to store highly sensitive
information. It is merely intended to provide a means of allowing a group of
people access to content without having a dependancy on user authentication.



License
==================================================

ccpages is released under a `3 clause BSD license.`_

.. _`3 clause BSD license.`: http://www.opensource.org/licenses/bsd-3-clause
.. _`Markdown`: http://pypi.python.org/pypi/Markdown 
.. _`ccfiletypes`: https://github.com/designcc/django-ccfiletypes
.. _`Django`: https://www.djangoproject.com/
.. _`mptt`: https://github.com/django-mptt/django-mptt
.. _`documentation`: http://readthedocs.org/docs/django-ccpages/en/latest/
.. _`ccpages`: https://github.com/designcc/django-ccpages

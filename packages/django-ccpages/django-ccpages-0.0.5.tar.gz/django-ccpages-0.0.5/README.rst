About
==================================================

ccpages is a lightweight pages application.

Full documentation to follow when I return from holidays, but in short you need
to :

Install ccpages::

    pip install django-ccpages


Next add `ccpages` to your installed apps::

    INSTALLED_APPS = (
         ...
        'ccpages'
    )

wire it up to your root urls.py::

    urlpatterns += ('',
    ...
        ('^pages/$, include('ccpages.urls', namespace='ccpages'))
    )

Then run syncdb::

    python manage.py syncdb


Finally you'll need to run the collectstatic command to get all of the static
files into your static root::

    python manage.py collectstatic
	
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

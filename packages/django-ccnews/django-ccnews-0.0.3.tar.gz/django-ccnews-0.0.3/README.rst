About
--------------------------------------------

ccnews is a lightweight news application.

Installation
--------------------------------------------

First, You need to install ccnews::

    pip install django-ccnews


Next add `ccnews` to your installed apps::

    INSTALLED_APPS = (
         ...
        'ccnews'
    )

wire it up to your root urls.py::

    urlpatterns += ('',
    ...
        ('^news/$, include('ccnews.urls', namespace='ccnews'))
    )

Then run syncdb::

    python manage.py syncdb


Finally you'll need to run the collectstatic command to get all of the static
files into your static root::

    python manage.py collectstatic
	
License
--------------------------------------------
ccnews is released under a 3 clause BSD license.


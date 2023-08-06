Quick Start Guide
=================


Requirements
------------

Interactive API Docs requires::

    south
    django 1.3 or greater


Installation
------------

Using ``pip``::

    pip install django-api-docs

Go to https://github.com/dstegelman/django-interactive-api-docs if you need to download a package or clone the repo.


Setup
-----

Open ``settings.py`` and add ``api_docs`` to your ``INSTALLED_APPS``::

    INSTALLED_APPS = (
        'api_docs',
        'south',
    )
    

Add URL-patterns::

    urlpatterns = patterns('',
        (r'^docs/', include('api_docs.urls')),
    )
    
Static Files
------------

Run collect static to fetch the files for production, or copy the files out of api_docs/static to your static directory.


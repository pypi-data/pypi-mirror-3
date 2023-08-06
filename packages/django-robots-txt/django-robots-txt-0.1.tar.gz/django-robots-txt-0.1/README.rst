======
README
======

This is a simple application to create a ``robots.txt`` for django. It has no models at all and you're supposed to edit a template to update the ``robots.txt`` file. I just got tired of copy & pasting this into my apps.

See the `robots page <http://www.robotstxt.org/>`_ for details what the file should look like.

Usage
-----

Get ``django-robots-txt`` into your python path::

    pip install django-robots-txt
    
Add ``robots_txt`` to your INSTALLED_APPS in settings.py::

    INSTALLED_APPS = (
        ...,
        'robots_txt',
        ...,
    )
    
Add a ``robots.txt`` view to your root urlconf (urls.py)::

    from django.conf.urls.defaults import patterns, include, url
    from robots_txt.views import RobotsTextView

    urlpatterns = patterns('',
        ...,
        url(r'^robots.txt$', RobotsTextView.as_view()),
        ...,        
    )

This urlconf entry is also supported::

    urlpatterns = patterns('',
        ...,
        url(r'', include('robots_txt.urls')),
        ...,        
    )

Create your custom robots.txt file in one of your template directories under ``robots_txt/robots.txt``. The default template is empty.

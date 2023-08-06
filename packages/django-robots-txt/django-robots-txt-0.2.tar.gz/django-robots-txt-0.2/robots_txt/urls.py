from django.conf.urls.defaults import patterns, include, url

from robotstxt.views import RobotsTextView

urlpatterns = patterns('',
    url(
        r'^robots.txt$',
        RobotsTextView.as_view(),
    ),
)

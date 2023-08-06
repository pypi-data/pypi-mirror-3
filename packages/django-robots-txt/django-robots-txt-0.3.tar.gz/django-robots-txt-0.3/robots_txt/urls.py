from django.conf.urls.defaults import patterns, include, url

from robots_txt.views import RobotsTextView

urlpatterns = patterns('',
    url(
        r'^robots.txt$',
        RobotsTextView.as_view(),
    ),
)

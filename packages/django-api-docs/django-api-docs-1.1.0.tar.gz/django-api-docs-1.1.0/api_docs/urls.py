from django.conf.urls.defaults import patterns, include, url
from api_docs.views import *

urlpatterns = patterns('',
    url(r'^$', home, name="home"),
    url(r'^js/docs.js', build_js, name="build_js"),
)

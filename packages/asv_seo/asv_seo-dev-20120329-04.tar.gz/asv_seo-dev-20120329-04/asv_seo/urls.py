# -*- coding: utf-8 -*-
try:
    from django.conf.urls import patterns, url
except ImportError:
    # for Django < 1.4
    from django.conf.urls.defaults import patterns, url
from asv_seo.views import *

urlpatterns = patterns('',
    url(r'^yandex_(?P<K>.*).txt$', Yandex),
    url(r'^robots.txt$', GetRobotsTxt),
)

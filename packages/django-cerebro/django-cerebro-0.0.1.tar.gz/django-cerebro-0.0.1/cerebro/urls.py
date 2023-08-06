#!/usr/bin/python
# -*- coding:utf8 -*-

from django.conf.urls.defaults import patterns

# Catch all
#		url(r'^.*$','fail')
#		url(r'^.*$', 'index')

BASE = '^'
urlpatterns = patterns('cerebro.views',
        (BASE + r'$',
            'index'),
        (BASE + r'getPromotion/$',
            'getPromotion'),
        (BASE + r'send_mail',
            'send_mail'),
        (BASE + r'getLab/$',
            'getLab'),
        (BASE + r'getHighSchool/$',
            'getHighSchool'),
        (BASE + r'getPublicInfo/$',
            'getPublicInfo'),
        (BASE + r'getText/$',
            'getText'),
        (BASE + r'getInterest/$',
            'getInterest'),
        )

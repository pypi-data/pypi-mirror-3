#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Settings for administration pages
"""

from cerebro.models import UserProfile
from cerebro.models import Interest
from cerebro.models import Organisateur
from cerebro.models import Student
from cerebro.models import Supervisor
from cerebro.models import HighSchool
from cerebro.models import Lab
from cerebro.models import Intership
from cerebro.models import Meeting
from cerebro.models import Text

from django.contrib.gis import admin

# Databrowsing mode

from django.contrib import databrowse

databrowse.site.register(Interest)
databrowse.site.register(Organisateur)
databrowse.site.register(Student)
databrowse.site.register(Supervisor)
databrowse.site.register(HighSchool)
databrowse.site.register(Lab)
databrowse.site.register(Intership)
databrowse.site.register(Meeting)

# Admin mode

admin.site.register(Interest)
admin.site.register(Text)
admin.site.register(UserProfile, admin.OSMGeoAdmin)
admin.site.register(Organisateur, admin.OSMGeoAdmin)
admin.site.register(Student, admin.OSMGeoAdmin)
admin.site.register(Supervisor, admin.OSMGeoAdmin)
admin.site.register(HighSchool, admin.OSMGeoAdmin)
admin.site.register(Lab, admin.OSMGeoAdmin)
admin.site.register(Intership)
admin.site.register(Meeting)

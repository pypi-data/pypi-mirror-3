#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views of the project
"""

import simplejson

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.core import serializers
from django.template import RequestContext

from cerebro.models import HighSchool
from cerebro.models import Lab
from cerebro.models import Student
from cerebro.models import Interest
from cerebro.models import Text


def index(request):
    """
    Main page
    """
    c = RequestContext(request)
    return render_to_response('base.html', c)


def getLab(request):
    data = dict()
    data['type'] = 'FeatureCollection'
    features = []
    for obj in Lab.objects.all():
        features += obj.getGeoJSON()
    data['features'] = features
    return HttpResponse(simplejson.dumps(data))


def getText(request):
    return HttpResponse(serializers.serialize("json", Text.objects.all()))


def getSearchCriteria(request):
    data = dict()
    data['promo'] = Student.objects.value_list('promo', flat=True).distinct()
    data['gender'] = Student.objects.value_list('gender', flat=True).distinct()
    data['interests'] = Interest.objects.all()
    # TODO : Add geographic research
    return HttpResponse(simplejson.dumps(data))


def getHighSchool(request):
    data = dict()
    data['type'] = 'FeatureCollection'
    features = []
    for obj in HighSchool.objects.all():
        features += obj.getGeoJSON()
    data['features'] = features
    return HttpResponse(simplejson.dumps(data))

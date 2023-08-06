#!/usr/bin/python
# -*- coding: utf-8 -*-

import simplejson as json
import requests

from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

GENDER_CHOICES = (
        ('M', 'M.'),
        ('F', 'Madame')
        )

LEVEL_CHOICES = (
        ('1ere', 'Premiere'),
        ('2nd', 'Seconde'),
        ('Term', 'Terminale')
        )

class Interest(models.Model):
    """
    Description of a topic interest. They are use to make tagging of
    information easier. Also they can allow objects to be grouped by common
    interests and so it makes the searching easier.
    """
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['name']


# Classe mere pour la geolocalisation


class CommonInfo(models.Model):
    """
    Root class of all geolocalizable objects
    """
    name = models.CharField(max_length=200)
    zipcode = models.IntegerField(null=True, blank=True)
    city = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=200, blank=True)
    objects = models.GeoManager()
    point = models.PointField(blank=True, null=True)

    class Meta:
        ordering = ['name']
        abstract = True

    def geocoding(self):
        """
        Utilitaire de geolocalisation des objets
        """
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        params = dict(
            adress = self.address.replace(' ', '+'),
            zipcode = str(self.zipcode),
            city = self.city.replace(' ', '+'),
            sensor = 'false'
            )
        r = requests.get(url, params=params)
        data_json = json.loads(r.content)
        if data_json["status"] == "OK":
            latitude = data_json["results"][0]["geometry"]["location"]["lat"]
            longitude = data_json["results"][0]["geometry"]["location"]["lng"]
            print str(latitude) + "," + str(longitude)
            self.point = Point((longitude, latitude))
            self.save()


    def getGeoJSON(self):

        geom = dict()
        geom['type'] = "Point"
        if self.point.coords:
            geom['coordinates'] = self.point.coords

        properties = dict()
        if self.name:
            properties['name'] = self.name
        if self.zipcode:
            properties['zipcode'] = self.zipcode
        if self.city:
            properties['city'] = self.city
        if self.mail:
            properties['mail'] = self.mail
        if self.address:
            properties['address'] = self.address
        if self.activity:
            properties['activity'] = self.activity

        dict_geoJSON = dict()
        dict_geoJSON['type'] = 'Feature'
        dict_geoJSON['geometry'] = geom
        dict_geoJSON['properties'] = properties

        return dict_geoJSON

# People models


class UserProfile(CommonInfo):
    """
    Root class of all people person
    """
    firstname = models.CharField(max_length=42, blank=True, null=True)
    user = models.OneToOneField(User, blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, choices=GENDER_CHOICES)
    ScientificInterest = models.ManyToManyField('Interest', blank=True)

    def __unicode__(self):
        return self.firstname + ' ' + self.name


class Student(UserProfile):
    """
    Student class.
    level -- The level he/she got when she integrated the program
    promo -- The year she was involved for the first time with Paris-Montagne.
    To request an filter a set of student :
    request = Student.objects.filter(scacScientificInterest__equals='maths')
    """
    level = models.CharField(max_length=4, choices=LEVEL_CHOICES, blank=True)
    highschool = models.ForeignKey('HighSchool', blank=True, null=True)
    promo = models.IntegerField(null=True, blank=True)


class Organizer(UserProfile):
    """
    An organizer is a person that is help organizing events, internship and
    various other activities involving students.
    """
    pass


class Supervisor(UserProfile):
    """
    A supervisor is a person that was in charge to take care of students when
    they were in intership/events
    """
    pass


# Place


class Place(CommonInfo):
    """
    activity -- Number of persons involved with this place.
    This counter have to be refreshed every time a new event is happening.
    """
    activity = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ['name', 'city']


class Lab(Place):
    """
    Laboratory class
    """
    ScientificInterest = models.ManyToManyField('Interest')
    ThematicWeek = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name


class HighSchool(Place):
    """
    High school class
    """
    phone = models.IntegerField(null=True, blank=True)
    mail = models.CharField(max_length=100, blank=True)

    def __unicode__(self):
        return self.name + " ( " + self.city + " ) "

# Textes statiques


class Text(models.Model):
    """
    Text used on the website
    """
    name = models.CharField(max_length=200)
    content = models.TextField(max_length=2000)

    def __unicode__(self):
        return self.name


class Activity(models.Model):
    """
    Class used to discribe the activity
    """
    name = models.CharField(max_length=200)
    begin = models.DateField()
    end = models.DateField()
    summary = models.CharField(max_length=200, blank=True)

    class Meta:
        abstract = True
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Intership(Activity):
    """
    Class used to describe what the intership is about.
    """
    supervisor = models.ManyToManyField(Supervisor)
    students = models.ManyToManyField(Student)
    lab = models.ManyToManyField(Lab)
    ScientificInterest = models.ManyToManyField('Interest', blank=True)

    def giveActivityPoint(self):
        """
        Used to refresh the activity account of each place.
        """
        for std in self.students.all():
            highschool = std.highschool
            highschool.activity += 1
            highschool.save()
        for laboratory in self.lab.all():
            laboratory.activity += 1
            laboratory.save()


class Meeting(Activity):
    """
    Class related to an activity/meeting or any other event.
    """
    members = models.ManyToManyField(UserProfile)


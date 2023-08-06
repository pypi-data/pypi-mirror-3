# -*- coding:utf-8 -*-

from setuptools import setup
from setuptools import find_packages

setup(
         name='django-cerebro',
         version='0.0.1',
         license="GNU",

         install_requires = [
             "django",
             ],

         description='A django-app that allows a people geolocalisation service',
         long_description=open('README.md').read(),

         author='Rémy Léone',
         author_email='remy.leone@gmail.com',

         url='http://github.com/sieben/django-cerebro',
         download_url='http://github.com/sieben/django-cerebro',

         include_package_data=True,

         packages=['cerebro'],

         zip_safe=False,
         classifiers=[
             'Environment :: Web Environment',
             'Intended Audience :: Developers',
             'Operating System :: OS Independent',
             'Programming Language :: Python',
             'Framework :: Django',
             ]
         )

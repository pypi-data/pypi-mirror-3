#!/usr/bin/env python
import os
import codecs

from setuptools import setup

if os.path.exists("README"):
    long_description = codecs.open("README", "r", "utf-8").read()
else:
    long_description = '''\
This is a bundle of several packages that you can use as a shortcut in the
requirements lists of your applications.  Bundles are used to follow a
common group of packages, or a package with an optional extension feature.
'''

setup(name='django-celery-with-mongodb',
      version='2.5',
      description='''Bundle installing the dependencies for Django-Celery and MongoDB''',
      author='''Celery Project''',
      author_email='bundles@celeryproject.org',
      url='''http://celeryproject.org''',
      platforms=['all'],
      license='''BSD''',
      zip_safe=False,
      install_requires=['django-celery>=2.5,<3.0', 'pymongo'],
      classifiers=[
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      long_description=long_description,
)

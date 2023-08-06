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

setup(name='celery-with-redis',
      version='2.5',
      description='''Bundle installing the dependencies for Celery and Redis''',
      author='''Celery Project''',
      author_email='bundles@celeryproject.org',
      url='''http://celeryproject.org''',
      platforms=['all'],
      license='''BSD''',
      zip_safe=False,
      install_requires=['celery>=2.5,<3.0', 'redis>=2.4.4'],
      classifiers=[
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      long_description=long_description,
)

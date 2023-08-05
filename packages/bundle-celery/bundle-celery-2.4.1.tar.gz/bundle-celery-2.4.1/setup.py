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

setup(name='bundle-celery',
      version='2.4.1',
      description='''Bundle that installs Celery related modules''',
      author='''Celery Project''',
      author_email='bundles@celeryproject.org',
      url='''http://celeryproject.org''',
      platforms=['all'],
      license='''BSD''',
      zip_safe=False,
      install_requires=['celery>=2.4,<3.0', 'django-celery>=2.4,<3.0',
                        'Flask-Celery>=2.4,<3.0', 'django',
                        'setproctitle', 'celerymon', 'cyme',
                        'kombu-sqlalchemy', 'django-kombu'],
      classifiers=[
          "Topic :: Software Development :: Libraries :: Python Modules",
      ],
      long_description=long_description,
)

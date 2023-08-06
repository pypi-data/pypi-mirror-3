# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
from setuptools import setup, find_packages
import sys, os

version = '1.2'

long_description = ''
long_description += open('README.txt').read()
long_description += '\n'

for filename in ('description.txt',
                 'upload.txt',
                 'storage.txt',
                 'paste-factories.txt',
                 'jquery-plugin.txt',
                 'contributors.txt'):
    long_description += open(os.path.join('docs', filename)).read()
    long_description += '\n'


requires = [
    'setuptools',
    'Paste',
    'WebOb',
    ]

if sys.version_info < (2, 6):
    requires.append('simplejson')

setup(name='gp.fileupload',
      version=version,
      description="A WSGI middleware to get some stats on large files upload,"
                  "and provide a progress bar for your users",
      long_description=long_description + \
                       'News\n****\n\n' +
                       open('CHANGES.txt').read(),
      # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: JavaScript",
        ],
      keywords='wsgi middleware upload progress bar',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://www.gawel.org/docs/gp.fileupload/',
      license='MIT',
      namespace_packages=['gp'],
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      package_data={'gp/fileupload': ['static/*',]},
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      entry_points="""
      # -*- Entry points: -*-
      [paste.app_factory]
      sample = gp.fileupload.sampleapp:make_app

      [paste.filter_app_factory]
      main = gp.fileupload:make_app
      demo = gp.fileupload.demo:make_demo
      """,
      )


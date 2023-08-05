#!/usr/bin/env python

import os.path
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='django-aloha',
      version='0.0.1',
      description='django app to easily integrate editing with Aloha '\
          'WYSIWIG editor in django apps.',
      long_description=read('README.rst'),
      author='Igor Katson',
      author_email='igor.katson@gmail.com',
      url='https://bitbucket.org/descent/django-aloha',
      packages=['aloha', 'aloha.templatetags'],
      package_data={'aloha': ['templates/*.html',
                              'templates/*/*.html',
                              'templates/*/*/*.html',
                              ]},
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Operating System :: POSIX',
          'Programming Language :: Python',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          ],
     )

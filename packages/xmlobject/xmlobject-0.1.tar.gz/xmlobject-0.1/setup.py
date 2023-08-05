#!/usr/bin/env python

from setuptools import setup, find_packages

from xmlobject import __version__

desc = """Interface XML using neat Python syntax"""
summ = """xmlobject lets you access your XML document with beautiful and easy to read Python syntax so that you don't need to deal with lxml, minidom or sax."""

PACKAGE_NAME = "xmlobject"
PACKAGE_VERSION = __version__

setup(name=PACKAGE_NAME,
      version=PACKAGE_VERSION,
      description=desc,
      long_description=summ,
      author='Tobias Mueller',
      author_email='tobiasmue@gnome.org',
      urls='http://bitbucket.org/muelli/xmlobject',
      license='GNU GPL v3+',
      packages=['xmlobject'],
      platforms =['Any'],
      classifiers=['Development Status :: 4 - Beta',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: OS Independent',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: Text Processing :: Markup :: XML',
                  ]
     )

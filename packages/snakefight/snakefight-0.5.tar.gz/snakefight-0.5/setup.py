#!/usr/bin/env python
from __future__ import with_statement
import os
from setuptools import setup, find_packages

version = '0.5'

with open(os.path.join(os.path.dirname(__file__), 'docs', 'usage.rst')) as fp:
    long_description = fp.read()

setup(name='snakefight',
      version=version,
      description="Assembles WAR files from Python (Jython) WSGI applications",
      long_description=long_description,
      classifiers="""
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Programming Language :: Python
Programming Language :: Python :: Implementation :: Jython
Topic :: Internet :: WWW/HTTP
Topic :: Internet :: WWW/HTTP :: Dynamic Content
Topic :: Internet :: WWW/HTTP :: WSGI
""".strip().splitlines(),
      keywords='jython war',
      author='Philip Jenvey',
      author_email='pjenvey@underboss.org',
      url='http://pypi.python.org/pypi/snakefight',
      license='BSD',
      packages=find_packages(exclude=['ez_setup']),
      include_package_data=True,
      zip_safe=True,
      entry_points="""
      [distutils.commands]
      bdist_war = snakefight.command:bdist_war
      """,
      )

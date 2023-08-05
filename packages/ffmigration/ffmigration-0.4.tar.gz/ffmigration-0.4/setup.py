#!/usr/bin/env python
"""
   Setup script for ffmigration
"""
#from distutils.core import setup
from setuptools import setup
import os
README = os.path.join(os.path.dirname(__file__), 'README')

import ffmigration

LONG_DESCRIPTION = open(README).read() + '\n\n'

setup(name='ffmigration',
      version=ffmigration.VERSION,
      author='Ferran Pegueroles Forcadell',
      author_email='ferran@pegueroles.com',
      description='Simple Forward-only database migrations',
      url='http://www.pegueroles.com/',
      long_description=LONG_DESCRIPTION,
      license='GPL',
      platforms='linux,windows',
      download_url='https://bitbucket.org/ferranp/ffmigration/downloads',
      packages=[],
      py_modules=['ffmigration'],
      scripts=["ffmigration"],
      data_files=[],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Information Technology',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License (GPL)',
          'Programming Language :: Python',
          'Topic :: Database',
          'Topic :: Utilities',
          ],
      )

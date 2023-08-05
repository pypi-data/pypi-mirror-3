#!/usr/bin/env python

import os
from distutils.core import setup
from glob import glob

README = open(os.path.join(os.path.dirname(__file__), 'README.txt')).read()

setup(name='tigreBrowser',
      version='1.0.2',
      license='AGPL3',
      author='Miika-Petteri Matikainen',
      author_email='mimatika@cc.hut.fi',
      maintainer='Antti Honkela',
      maintainer_email='antti.honkela@hiit.fi',
      url='http://users.ics.tkk.fi/ahonkela/tigre/',
      description='Gene expression model browser for results from tigre R package (http://www.bioconductor.org/packages/release/bioc/html/tigre.html)',
      long_description=README,
      scripts=['tigreServer.py'],
      packages=['tigreBrowser'],
      data_files=[('share/tigreBrowser', glob('tigreBrowser/*.js') + glob('tigreBrowser/tigreBrowser.*') + ['tigreBrowser/imagehelper.cgi', 'database.sqlite'])],
      classifiers=[
          'Environment :: Web Environment',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Natural Language :: English',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Database :: Front-Ends',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Scientific/Engineering :: Bio-Informatics',
      ],
      )

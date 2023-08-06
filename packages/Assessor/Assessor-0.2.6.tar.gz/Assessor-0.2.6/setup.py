#!/usr/bin/env python

'''
setup
@updated: on Jul 18, 2012
@author: justin
@license:  AGPLv3
    Copyright (C) 2012  Justin Chudgar,
    5040 Saddlehorn Rd, Weed, CA 96094
    <justin@justinzane.com>

     is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

     is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from distutils.core import setup
import os


def get_data_files(data_dirs):
    files = []
    for d in data_dirs:
        for f in os.listdir(d):
            if os.path.isdir(os.path.join(d, f)):
                data_dirs.append(os.path.join(d, f))
            else:
                files.append(os.path.join(d, f))
    return files


setup(name='Assessor',
      version='0.2.6',
      author='Justin Chudgar',
      author_email='justin@justinzane.com',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'Intended Audience :: Education',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Natural Language :: English',
          'Operating System :: POSIX :: Linux',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: JavaScript',
          ],
      description='Django Assessment App',
      maintainer='Justin Chudgar',
      url='http://www.justinzane.com/',
      scripts=['manage.py'],
      packages=['Assessor', 'tastypie'],
      data_files=[('/var/www/Assessor/static',
                   get_data_files(['Assessor/deploy-static'])),
                  ('Assessor/fixtures',
                   get_data_files(['Assessor/fixtures'])),
                  ('/var/lib/Assessor', ['Assessor.db', 'uwsgi.ini']),
                  ],
      install_requires=["Django", "uWSGI", ],
      )

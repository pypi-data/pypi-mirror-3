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
import os, sys

STATICPATH = '/var/lib/www'


def get_data_files(sources):
    target_list = []
    for (target, source) in sources:
        if os.path.isdir(source):
            dirs = [source]
            for d in dirs:
                files = []
                for f in os.listdir(d):
                    if os.path.isdir(os.path.join(d, f)):
                        dirs.append(os.path.join(d, f))
                    else:
                        files.append(os.path.join(d, f))
                target_list.append((os.path.join(target, d), files))
        else:
            target_list.append((target, source))
    for t in target_list:
        sys.stderr.write(str(t) + '\n')
    return target_list

data_files_sources = [(STATICPATH, 'Assessor/static/app-min.js'),
                      (STATICPATH, 'Assessor/static/extjs/ext.js'),
                      (STATICPATH, 'Assessor/static/resources/css'),
                      (STATICPATH,
                       'Assessor/static/resources/images/default'),
                      (STATICPATH,
                       'Assessor/static/resources/images/a_icon01_opt.svg'),
                      (STATICPATH,
                       'Assessor/static/resources/images/assessor01.svg'),
                      (STATICPATH, 'Assessor/fixtures/fixture_5.json'),
                      ('/var/lib', 'Assessor/Assessor.db'),
                      ('/var/lib', 'Assessor/uwsgi.ini')]

setup(name='Assessor',
      version='0.2.7',
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
      #
      data_files=get_data_files(data_files_sources),
      install_requires=["Django", "uWSGI", ],
      )

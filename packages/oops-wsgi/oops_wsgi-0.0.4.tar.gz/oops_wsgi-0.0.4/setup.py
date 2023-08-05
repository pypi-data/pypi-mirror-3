#!/usr/bin/env python
#
# Copyright (c) 2011, Canonical Ltd
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
  

from distutils.core import setup
import os.path

description = file(
        os.path.join(os.path.dirname(__file__), 'README'), 'rb').read()

setup(name="oops_wsgi",
      version="0.0.4",
      description=\
              "OOPS wsgi middleware.",
      long_description=description,
      maintainer="Launchpad Developers",
      maintainer_email="launchpad-dev@lists.launchpad.net",
      url="https://launchpad.net/python-oops-wsgi",
      packages=['oops_wsgi'],
      package_dir = {'':'.'},
      classifiers = [
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          ],
      install_requires = [
          'oops',
          'paste',
          ],
      extras_require = dict(
          test=[
              'testtools',
              ]
          ),
      )

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright © 2009 Neil Martinsen-Burrell
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from distutils.core import setup

from info import (bzr_plugin_version,
                  bzr_plugin_name,
                  bzr_minimum_version,
                  bzr_commands,
                  __version__,
                 )

if __name__ == '__main__':
    setup(name="bzr-colo",
          version=__version__,
          description="Work with colocated Bazaar branches "
                      "using current technology.",
          author="Neil Martinsen-Burrell",
          author_email="nmb@wartburg.edu",
          url="https://launchpad.net/bzr-colo",
          packages=['bzrlib.plugins.colo',
                    'bzrlib.plugins.colo.tests',
                    'bzrlib.plugins.colo.explorer',
                    ],
          package_dir={'bzrlib.plugins.colo': '.'},
          package_data={'bzrlib.plugins.colo': ['folder.png'],
                        'bzrlib.plugins.colo.explorer': ['tools.xml'],
                       },
          classifiers=['Development Status :: 4 - Beta',
                       'Intended Audience :: Developers',
                       'License :: OSI Approved :: GNU General Public License (GPL)',
                       'Programming Language :: Python :: 2',
                       'Topic :: Software Development :: Version Control',
                      ]
          
         )

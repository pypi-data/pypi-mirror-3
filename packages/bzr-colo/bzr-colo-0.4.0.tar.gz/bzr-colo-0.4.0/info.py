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

"""Store version info separately for use in __init__.py and setup.py"""
bzr_plugin_name = 'colo'
bzr_plugin_version = (0, 4, 0, 'final', 0)
bzr_minimum_version = (2, 1, 0)

if bzr_plugin_version[3] == 'final':
    __version__ = '%d.%d.%d' % bzr_plugin_version[:3]
else:
    __version__ = '%d.%d.%d%s%d' % bzr_plugin_version

bzr_commands = ['colo-init',
                'colo-branch',
                'colo-branches',
                'colo-fetch',
                'colo-pull',
                'colo-checkout',
                'colo-co',
                'colo-mv',
                'colo-move',
                'colo-rename',
                'colo-prune',
                'colo-delete',
                'colo-clean',
                'colo-ify',
                'colo-fixup',
                'qprune',
                'qdelete',
                'qbranches',
                'qcoloswitch',
                'colo-sync-from',
                'colo-sync-to',
               ]

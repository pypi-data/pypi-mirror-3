# Copyright 2010 Neil Martinsen-Burrell

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

import os
from bzrlib.tests import TestCaseWithTransport
from bzrlib import osutils

class TestQBzrCommands(TestCaseWithTransport):

    def test_disabled(self):
        # Incantation from MBP 20100413
        self.run_bzr_subprocess('qbranches', retcode=3,
                                env_changes=dict(BZR_DISABLE_PLUGINS='qbzr'),
                                allow_plugins=True)

    def test_enabled(self):
        try:
            from bzrlib.plugins import qbzr
        except ImportError:
            return
        self.run_bzr_error(['No colocated workspace'],
                           ['qbranches'])

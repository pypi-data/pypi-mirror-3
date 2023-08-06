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

from bzrlib.plugins.colo.tests.script import ScriptTestCase
from bzrlib.plugins.colo.colocated import ColocatedWorkspace


class TestColoSyncFrom(ScriptTestCase):

    def test_sync(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ bzr colo-sync-from ../remote
2>Updating branch trunk from colo:../remote:trunk.
No revisions or tags to pull.
""")

    def test_sync_nontrivial(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd remote
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision'
$ cd ../local
$ bzr colo-sync-from ../remote
2>Updating branch trunk from colo:../remote:trunk.
2>All changes applied successfully.
Now on revision 1.
""")

    def test_sync_missing_branch(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ bzr colo-branch other
$ bzr colo-sync-from ../remote
$ bzr colo-branches
* other
  trunk
""")

    def test_sync_creates_branch(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd remote
$ bzr colo-branch other
$ cd ../local
$ bzr colo-sync-from ../remote
$ bzr colo-branches
  other
* trunk
""")


    def test_sync_diverged(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd remote
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision in remote branch'
$ cd ../local
$ echo stuff > file1
$ bzr add
$ bzr ci -m 'a different revision in local branch'
""")
        self.run_bzr_error(['These branches have diverged. Use the missing command to see how.'],
                           ['colo-sync-from', '../remote'])

    def test_sync_multiple_diverged(self):
        self.run_script("""
$ bzr colo-init local
$ bzr colo-init remote
$ cd remote
$ echo content > file
$ bzr add
$ bzr ci -m 'trunk revision'
$ bzr colo-branch other
$ cd ../local
$ echo stuff > file
$ bzr add
$ bzr ci -m 'a different trunk revision'
$ bzr colo-sync-from ../remote
2>Creating new branch other from colo:../remote:other.
2>Branched 1 revision.
2>Updating branch trunk from colo:../remote:trunk.
2>bzr: ERROR: These branches have diverged...
2>...
""")

    def test_sync_overwrite(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd remote
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision in remote branch'
$ cd ../local
$ echo stuff > file1
$ bzr add
$ bzr ci -m 'a different revision in local branch'
$ bzr colo-sync-from --overwrite ../remote
2>Updating branch trunk from colo:../remote:trunk.
2>All changes applied successfully.
Now on revision 1.
""")

    def test_sync_from_empty(self):
        self.run_script("""
$ mkdir empty
$ bzr colo-init local
$ cd local
$ bzr colo-sync-from ../empty
2>bzr: ERROR: No colocated workspace in ../empty
""")

    def test_sync_from_standalone(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init standalone
$ cd local
$ bzr colo-sync-to ../standalone
2>bzr: ERROR: No colocated workspace in ../standalone
""")

    def test_sync_from_repository(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ bzr init repo/trunk
$ cd repo/trunk
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision in repository branch'
$ cd ../../local
$ bzr colo-sync-from --repository ../repo
2>Updating branch trunk from colo:../repo:trunk.
2>All changes applied successfully.
Now on revision 1.
""")

    def test_sync_from_repository_no_argument(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ bzr init repo/trunk
$ cd repo/trunk
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision in repository branch'
$ cd ../../local
$ bzr colo-sync-from ../repo
$ cat file
2>file: No such file or directory
""")

    def test_sync_from_repository_creates_branch(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ bzr init repo/not_trunk
$ cd repo/not_trunk
$ bzr ci -m 1 --unchanged
$ cd ../../local
$ bzr colo-sync-from --repository ../repo
$ bzr colo-branches
  not_trunk
* trunk
""")

    def test_sync_from_repository_not_remembered(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ cd local
$ bzr colo-sync-from --repository ../repo
$ bzr colo-sync-from
2>bzr: ERROR: No synchronization location known or specified.
""")



class TestColoSyncTo(ScriptTestCase):

    def test_sync(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ bzr colo-sync-to ../remote
2>Updating colo:../remote:trunk from trunk.
2>No new revisions or tags to push.
""")

    def test_sync_nontrivial(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ echo content > file
$ bzr add
$ bzr ci -m 'first revision'
$ bzr colo-sync-to ../remote
2>Updating colo:../remote:trunk from trunk.
2>Pushed up to revision 1.
$ cd ../remote
$ bzr revno
1
""")

    def test_sync_to_empty(self):
        self.run_script("""
$ mkdir branch
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-sync-to ../branch
2>bzr: ERROR: No colocated workspace in .../branch
""")

    def test_sync_to_standalone(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init standalone
$ cd local
$ bzr colo-sync-to ../standalone
2>bzr: ERROR: No colocated workspace in ../standalone
""")

    def test_sync_to_no_trees(self):
        self.run_script("""
$ bzr colo-init --no-tree remote
$ bzr colo-init local
$ cd local
$ bzr colo-sync-to ../remote
2>Updating colo:../remote:trunk from trunk.
2>No new revisions or tags to push.
$ cd ../remote
$ bzr colo-branches
  trunk
""")

    def test_sync_to_creates_branch(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ bzr colo-branch other
$ bzr colo-sync-to ../remote
2>Updating colo:../remote:other from other.
2>Created new branch.
2>Updating colo:../remote:trunk from trunk.
2>No new revisions or tags to push.
$ cd ../remote
$ bzr colo-branches
  other
* trunk
""")

    def test_sync_to_diverged(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd remote
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision'
$ cd ../local
$ echo stuff > file
$ bzr add
$ bzr ci -m 'a separate revision'
$ bzr colo-sync-to ../remote
2>Updating colo:../remote:trunk from trunk.
2>bzr: ERROR: These branches have diverged. ...
""")

    def test_sync_to_repository(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ bzr init repo/trunk
$ cd local
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision in colocated branch'
$ bzr colo-sync-to --repository ../repo
2>Updating colo:../repo:trunk from trunk.
2>All changes applied successfully.
2>Pushed up to revision 1.
""")

    def test_sync_to_repository_no_argument(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ bzr init repo/trunk
$ cd local
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision in colocated branch'
$ bzr colo-sync-to ../repo
$ cat ../repo/trunk/.bzr/README
$ cat ../repo/trunk/file
2>../repo/trunk/file: No such file or directory
""")

    def test_sync_to_repository_creates_branch(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ cd local
$ bzr ci -m 1 --unchanged
$ bzr colo-sync-to --repository ../repo
$ cat ../repo/trunk/.bzr/README
""")

    def test_sync_to_repository_not_remembered(self):
        self.run_script("""
$ bzr colo-init local
$ bzr init-repo repo
$ cd local
$ bzr ci -m 1 --unchanged
$ bzr colo-sync-to --repository ../repo
$ bzr colo-sync-to
2>bzr: ERROR: No synchronization location known or specified.
""")


class TestColoSyncLocations(ScriptTestCase):

    def test_set_locations(self):
        self.run_script('$ bzr colo-init')
        w = ColocatedWorkspace()
        c = w.get_config()
        self.assertEqual(c.get_sync_from_location(), None)
        self.assertEqual(c.get_sync_to_location(), None)
        c.set_sync_from_location('location')
        c.set_sync_to_location('other_location')
        self.assertEqual(c.get_sync_from_location(), 'location')
        self.assertEqual(c.get_sync_to_location(), 'other_location')

    def test_set_location_none(self):
        self.run_script('$ bzr colo-init')
        w = ColocatedWorkspace()
        c = w.get_config()
        c.set_sync_from_location(None)
        self.assertEqual(c.get_sync_from_location(), None)
        c.set_sync_to_location(None)
        self.assertEqual(c.get_sync_to_location(), None)

    def test_sync_from_default_location(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ bzr colo-sync-from ../remote
$ bzr colo-sync-from
2>Updating branch trunk from .../remote/:trunk.
No revisions or tags to pull.
""")

    def test_sync_from_remembered_location(self):
        self.run_script("""
$ bzr colo-init remote1
$ bzr colo-init remote2
$ bzr colo-init local
$ cd local
$ bzr colo-sync-from ../remote1
2>Updating branch trunk from ...:trunk.
No revisions or tags to pull.
$ bzr colo-sync-from --remember ../remote2
$ bzr colo-sync-from
2>Updating branch trunk from ...remote2/:trunk.
""")

    def test_sync_from_no_default(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-sync-from
2>bzr: ERROR: No synchronization location known or specified.
""")

    def test_sync_to_default_location(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init local
$ cd local
$ bzr colo-sync-to ../remote
$ bzr colo-sync-to
2>Updating colo:.../remote/:trunk from trunk.
2>No new revisions or tags to push.
""")

    def test_sync_to_remembered_location(self):
        self.run_script("""
$ bzr colo-init remote1
$ bzr colo-init remote2
$ bzr colo-init local
$ cd local
$ bzr colo-sync-to ../remote1
2>Updating colo:.../remote1:trunk from trunk.
2>No new revisions or tags to push.
$ bzr colo-sync-to --remember ../remote2
$ bzr colo-sync-to
2>Updating colo:.../remote2/:trunk from trunk.
2>No new revisions or tags to push.
""")

    def test_sync_to_no_default(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-sync-to
2>bzr: ERROR: No synchronization location known or specified.
""")

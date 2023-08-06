# Copyright 2009 Neil Martinsen-Burrell

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


from bzrlib.plugins.colo.colocated import (
    COLOCATED_LOCATION,
    ColocatedDirectory,
    ColocatedWorkspace,
    NoColocatedWorkspace,
    colo_nick_hook,
    )
from bzrlib.plugins.colo.commands import (init_workspace,
                                          COLOCATED_STAGING,
                                         )
from bzrlib.plugins.colo.tests.script import ScriptTestCase

from bzrlib.lazy_import import lazy_import
lazy_import(globals(), '''
from bzrlib import (branch,
                    bzrdir,
                    directory_service,
                    errors,
                    tests,
                    osutils,
                    urlutils,
                   )
''')


def make_colo_branch(workspace, name):
    transport = workspace.repo_transport().clone(name)
    transport.create_prefix()
    return bzrdir.BzrDir.create_branch_convenience(transport.base)


class TestColoLookup(tests.TestCaseWithTransport):

    def test_colo_lookup_fail(self):
        """Look up a colo: URL while not in a colocated workspace"""
        directory = ColocatedDirectory()
        self.assertRaises(NoColocatedWorkspace,
                          directory.look_up, '', 'colo:')

    def test_colo_lookup_nonexistent(self):
        """Look up a nonexistent branch under colo:"""
        directory = ColocatedDirectory()
        init_workspace(self.test_dir, outf=tests.StringIOWrapper())
        self.assertEqual(directory.look_up('test', 'colo:test'),
                         urlutils.local_path_to_url(osutils.pathjoin(
                             self.test_dir, COLOCATED_LOCATION, 'test')))

    def test_colo_in_directory_services(self):
        """Look up a branch via directory services."""
        self.assertRaises(NoColocatedWorkspace,
                          directory_service.directories.dereference, 
                          'colo:test')

    def test_colo_remote_error(self):
        self.assertRaises(NoColocatedWorkspace,
                          directory_service.directories.dereference,
                          'colo:test:remote')

    def test_colo_remote(self):
        self.run_bzr('colo-init test')
        self.assertEqual(directory_service.directories.dereference(
                         'colo:test:remote'),
                          urlutils.join(self.get_url(), 'test', COLOCATED_LOCATION, 'remote'))

    def test_error_code(self):
        self.run_bzr_error(['No colocated workspace'],
                           ['colo-branches'])

    def test_backslash_name(self):
        """A name with a backslash should be converted to a forward slash"""
        self.run_bzr('colo-init')
        self.assertEqual(directory_service.directories.dereference(
                         r'colo:test\backslash'),
                         urlutils.join(self.get_url(), COLOCATED_LOCATION,  'test/backslash'))



class TestColocatedWorkspace(tests.TestCaseInTempDir):

    def test_creation(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        self.assertStartsWith(z.base,
                              urlutils.local_path_to_url(self.test_dir))

    def test_creation_directory(self):
        init_workspace(u'branch', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace('branch')
        self.assertEndsWith(z.base, 'branch/')

    def test_repo_location(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        self.assertEqual(z.repo_location, 
                         urlutils.local_path_to_url(
                             urlutils.join(self.test_dir, COLOCATED_LOCATION))
                        )

    def test_remote_no_tree_repo_location(self):
        init_workspace(u'.', create_tree=False, outf=tests.StringIOWrapper())
        z = ColocatedWorkspace(urlutils.normalize_url(self.test_dir))
        self.assertEqual(z.repo_location,
                         urlutils.normalize_url(
                             urlutils.join(self.test_dir, COLOCATED_LOCATION))
                        )

    def test_branch_names(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        self.assertEqual(list(z.branch_names()), ['trunk'])

    def test_current_branch(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        self.assertEndsWith(z.current_branch().base, 'trunk/')

    def test_current_branch_name(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        self.assertEqual(z.current_branch_name(), 'trunk')

    def test_is_pipe_non_existent(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        self.assertFalse(z.is_pipe('non_existent'))

    def test_is_pipe_plain_branch(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'has_next')
        self.assertFalse(z.is_pipe('has_next'))

    def test_is_pipe_has_next(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'has_next')
        branch.get_config().set_user_option('next_pipe', 'foo')
        self.assertTrue(z.is_pipe('has_next'))

    def test_is_pipe_has_blank_next(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'has_next')
        branch.get_config().set_user_option('next_pipe', '')
        self.assertFalse(z.is_pipe('has_next'))

    def test_is_pipe_has_prev(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'has_prev')
        branch.get_config().set_user_option('prev_pipe', 'foo')
        self.assertTrue(z.is_pipe('has_prev'))

    def test_is_pipe_has_blank_prev(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'has_prev')
        branch.get_config().set_user_option('prev_pipe', '')
        self.assertFalse(z.is_pipe('has_prev'))


class TestColoScripts(ScriptTestCase):

    def test_colo_blackbox(self):
        """colo: from the command line"""
        self.run_script("""
$ bzr colo-init
$ bzr init colo:test
$ cat .bzr/branches/test/.bzr/README
""")

    def test_colo_remote_blackbox(self):
        self.run_script("""
$ bzr colo-init b1
$ bzr colo-init b2
$ cd b1
$ bzr log colo:../b2:trunk
""")

    def test_colo_remote_url(self):
        script_text = '\n'.join(["$ bzr colo-init",
                                 "$ bzr log colo:%s:trunk" % self.get_url(),
                                    ])
        self.run_script(script_text)

    def test_colo_init(self):
        """Creating a colocated branch using the alias."""
        self.run_script("""
$ bzr colo-init branch
$ cat branch/.bzr/README
$ cat branch/.bzr/branches/.bzr/README
$ cat branch/.bzr/branches/trunk/.bzr/README
""")

    def test_branches(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch fix1
$ bzr colo-branch --no-switch fix2
""")
        z = ColocatedWorkspace()
        self.assertEqual(len(list(z.branches())), 3)

    def test_hierarchical_names(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch a/b
$ bzr colo-branches
* a/b
  trunk
""")
        z = ColocatedWorkspace()
        self.assertEqual(z.current_branch_name(), 'a/b')

    def test_backslash_names(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch trunk\\test
$ bzr colo-branches
  trunk
* trunk/test
$ bzr log colo:trunk\\test
""")

    def test_backslash_bialix(self):
        self.run_script("""
$ bzr colo-init
$ bzr ci -m1 --unchanged
$ bzr switch -b colo:trunk\\bar
$ bzr colo-branches
  trunk
* trunk/bar
$ bzr ci -m2 --unchanged
$ bzr switch colo:trunk
$ bzr merge colo:trunk\\bar
""")

    def test_colo_init_hidden(self):
        out, err = self.run_bzr(['colo-init'])
        self.assertNotContainsRe(out,
                                 COLOCATED_STAGING)

    def test_colo_init_format(self):
        """Creating a colocated branch using the alias."""
        self.run_script("""
$ bzr colo-init --format=1.9 branch
$ cat branch/.bzr/README
$ cat branch/.bzr/branches/.bzr/README
$ cat branch/.bzr/branches/trunk/.bzr/README
""")

    def test_colo_init_create_prefix(self):
        self.run_script("""
$ bzr colo-init --create-prefix branch/test/long/path
$ cat branch/test/long/path/.bzr/README
""")

    def test_colo_init_trunk_name(self):
        self.run_script("""
$ bzr colo-init --trunk-name=HEAD
$ bzr colo-branches
* HEAD
""")

    def test_colo_init_trunk_name_hierarchical(self):
        self.run_script("""
$ bzr colo-init --trunk-name=origin/trunk
$ bzr colo-branches
* origin/trunk
""")

    def test_colo_init_no_tree(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-branches
  trunk
""")

    def test_colo_checkin(self):
        """Use a colocated branch to check in under trunk."""
        self.run_script("""
$ bzr colo-init
$ cat > file1
<text
$ cat < file1
text
$ bzr add
$ bzr ci -m 'first check-in'
2>Committing to: .../.bzr/branches/trunk/
2>added file1
2>Committed revision 1.
$ bzr log -r1
------------------------------------------------------------
revno: 1
committer: ...
branch nick: trunk
timestamp: ...
message:
  first check-in
""")

    def test_colo_switch_creates_branch(self):
        """Branch using the switch command in a colocated tree"""
        self.run_script("""
$ bzr colo-init
$ bzr switch -b newtip
$ cat .bzr/branches/newtip/.bzr/README
$ bzr nick
newtip
""")

    def test_colo_switch_creates_branch_use_directory_service(self):
        """Branch using the switch command in a colocated tree"""
        self.run_script("""
$ bzr colo-init
$ bzr switch -b colo:newtip/  # slash for workaround on switch bug
$ cat .bzr/branches/newtip/.bzr/README
$ bzr nick
newtip
""")

    def test_colo_merging(self):
        """Merge in colocated branches"""
        self.run_script("""
$ bzr colo-init
$ cat > file1
<text
$ bzr add
$ bzr ci -m 'adding first file'
$ bzr switch -b newtip
$ bzr nick
newtip
$ cat >> file1
<more text
$ cat < file1
text
more text
$ bzr ci -m 'change in newtip'
2>Committing to: .../.bzr/branches/newtip/
2>modified file1
2>Committed revision 2.
$ bzr switch trunk
$ bzr merge colo:newtip
$ bzr ci -m 'merge in changes from newtip'
2>Committing to: .../.bzr/branches/trunk/
2>modified file1
2>Committed revision 2.
$ bzr log --line -n0
2: ... [merge] merge in changes from newtip
  1.1.1: ... change in newtip
1: ... adding first file
""")

class TestColoBranch(ScriptTestCase):

    def test_colo_branch_then_switch(self):
        """Branch in a colocated tree."""
        self.run_script("""
$ bzr colo-init
$ bzr branch . colo:newtip
$ bzr switch newtip  # works because newtip is a sibling of trunk
$ bzr nick
newtip
""")

    def test_colo_branch(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch newtip
2>Branched 0 revisions.
2>Tree is up to date at revision 0.
2>Switched to branch: .../.bzr/branches/newtip/
$ bzr nick
newtip
""")

    def test_colo_branch_no_switch(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch newtip
2>Branched 0 revisions.
$ bzr nick
trunk
""")

    def test_colo_branch_from(self):
        self.run_script("""
$ bzr colo-init
$ bzr ci -m 'commit in trunk' --unchanged
$ bzr colo-branch new
$ bzr ci -m 'commit in new branch' --unchanged
$ bzr colo-branch --from-branch=trunk new2
$ bzr log --line
1: ...
""")

    def test_colo_branch_revision(self):
        self.run_script("""
$ bzr colo-init
$ cat >file1
<content
$ bzr add
$ bzr ci -m 'first'
$ cat >>file1
<more content
$ bzr ci -m 'second'
$ bzr colo-branch -r1 new
$ cat file1
content
""")


class TestColoBranches(ScriptTestCase):

    def test_colo_branches(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch new
$ bzr colo-branch newer
$ bzr colo-branches
  new
* newer
  trunk
""")

    def test_colo_branches_location(self):
        self.run_script("""
$ bzr colo-init test
$ cd test
$ bzr colo-branch new
$ cd ..
$ bzr colo-branches test
  new
  trunk
""")

    def test_colo_branches_hidden(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch .test
$ bzr colo-branches
* trunk
""")

    def test_colo_branches_config_hidden(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch test
$ bzr colo-branches
* test
  trunk
$ bzr config bzr.branch.status=hidden
$ bzr colo-branches
* test
  trunk
$ bzr switch trunk
$ bzr colo-branches
* trunk
$ bzr colo-branches --all
  test
* trunk
$ bzr switch test
$ bzr config bzr.branch.status=active
$ bzr colo-branches
* test
  trunk
$ bzr switch trunk
$ bzr colo-branches
  test
* trunk
""")

    def test_colo_branches_hidden_config_other_values(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'test')
        for hidden_value in ColocatedWorkspace.HIDDEN_STATUSES:
            self.run_script("""
$ bzr switch test
$ bzr config bzr.branch.status=%s
$ bzr switch trunk
$ bzr colo-branches
* trunk
""" % hidden_value)

    def test_colo_branches_all(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch .test
$ bzr colo-branches --all
  .test
* trunk
""")

    def test_colo_branches_current_not_hidden(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch .other
$ bzr colo-branch .this
$ bzr colo-branches 
* .this
  trunk
$ bzr colo-branches --all
  .other
* .this
  trunk
""")

    def test_colo_branches_hidden_subdirectory(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch other
$ bzr colo-branch --no-switch this
$ bzr colo-branches
  other
  this
* trunk
$ bzr colo-mv other .hidden/other
$ bzr colo-mv this .hidden/this
$ bzr colo-branches
* trunk
$ bzr colo-branches --all
  .hidden/other
  .hidden/this
* trunk
""")

    def test_colo_branches_hidden_in_subdirectory(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch subdir/.this
$ bzr colo-branch --no-switch foo/.bar/spam
$ bzr colo-branches
* trunk
$ bzr colo-branches --all
  foo/.bar/spam
  subdir/.this
* trunk
""")


class TestColoFetch(ScriptTestCase):

    def test_fetch(self):
        self.make_branch('branch')
        self.run_script("""
$ bzr colo-fetch branch branch-colo
$ cd branch-colo
$ bzr colo-branches
* origin/trunk
""")

    def test_fetch_format(self):
        self.make_branch('branch')
        self.run_script("""
$ bzr colo-fetch --format=1.9 branch branch-colo
$ cd branch-colo
$ bzr colo-branches
* origin/trunk
""")

    def test_fetch_current_directory(self):
        self.make_branch('branch')
        self.run_script("""
$ bzr colo-fetch branch
2>bzr: ERROR: A control directory already exists: .../branch/...
""")

    def test_fetch_one_argument(self):
        self.run_script("""
$ bzr init --create-prefix other/branch
$ bzr colo-fetch other/branch
$ bzr colo-branches branch
  origin/trunk
""")

    def test_fetch_url(self):
        self.make_branch('branch')
        branch_url = urlutils.local_path_to_url('branch')
        self.run_script(
            ''.join(["$ bzr colo-fetch %s .\n" % branch_url,
                     "$ bzr colo-branches\n",
                     "* origin/trunk"]))

    def test_fetch_branch_name(self):
        self.make_branch('branch')
        self.run_script("""
$ bzr colo-fetch --trunk-name=master branch .
$ bzr colo-branches
* master
""")


class TestColoCheckout(ScriptTestCase):

    def test_checkout(self):
        self.run_script("""
$ bzr colo-init branch
$ cd branch
$ bzr colo-checkout ../branch2
$ cd ../branch2
$ cat .bzr/README
""")

    def test_checkout_example(self):
        self.run_script("""
$ bzr colo-init branch
$ cd branch
$ bzr colo-branch fix-eol-bug
$ bzr colo-branches
* fix-eol-bug
  trunk
$ bzr switch trunk
$ bzr colo-branch fix-unicode-normalization
$ bzr colo-checkout ../fix-unicode-normalization
$ cd ../fix-unicode-normalization
$ cat .bzr/README
""")

    def test_checkout_create(self):
        self.run_script("""
$ bzr colo-init branch
$ cd branch
$ bzr colo-checkout --create ../fix1
$ bzr colo-branches
  fix1
* trunk
$ bzr nick
trunk
$ cd ../fix1
$ cat .bzr/README
$ bzr nick
fix1
$ bzr colo-branches
* fix1
  trunk
""")

    def test_checkout_create_dash_b(self):
        self.run_script("""
$ bzr colo-init branch
$ cd branch
$ bzr colo-checkout -b ../fix1
$ bzr colo-branches
  fix1
* trunk
$ bzr nick
trunk
$ cd ../fix1
$ cat .bzr/README
$ bzr nick
fix1
$ bzr colo-branches
* fix1
  trunk
""")

    def test_checkout_in_directory(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-checkout tree
$ cd tree
$ cat .bzr/README
$ bzr nick
trunk
""")

    def test_checkout_from_branch(self):
        self.run_script("""
$ bzr colo-init branch
$ cd branch
$ bzr colo-branch fix-eol-bug
$ bzr colo-branches
* fix-eol-bug
  trunk
$ bzr colo-checkout --from-branch trunk ../fix-unicode-normalization
$ cd ../fix-unicode-normalization
$ bzr nick
trunk
$ bzr colo-branches
  fix-eol-bug
* trunk
""")


class TestColoPrune(ScriptTestCase):

    def test_prune(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch new
$ bzr colo-branches
* new
  trunk
$ bzr switch trunk
$ bzr colo-branches
  new
* trunk
$ bzr colo-prune new
$ bzr colo-branches
* trunk
""")

    def test_prune_multiple(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch new
$ bzr colo-branch --no-switch newer
$ bzr colo-prune new newer
$ bzr colo-branches
* trunk
""")

    def test_prune_clean(self):
        self.run_script("""
$ bzr colo-init
$ bzr ci -m 'trunk revision' --unchanged
$ bzr colo-branch new
$ bzr ci -m 'a revision' --unchanged
$ bzr switch trunk
$ bzr colo-prune --clean new
$ bzr colo-branches
* trunk
""")
        repo = ColocatedWorkspace().repository()
        self.assertEqual(len(repo.all_revision_ids()), 1)

    def test_prune_current(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-prune trunk
2>Not removing current branch trunk.
""")

    def test_dont_prune_everything(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch one
$ bzr colo-prune .
2>Not removing . because it is not a branch.
$ cat .bzr/branches/.bzr/README
""")

    def test_dont_prune_subdirectories(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch origin/trunk
$ bzr colo-prune origin
2>Not removing origin because it is not a branch.
$ cat .bzr/branches/origin/trunk/.bzr/README
""")

    def test_do_prune_common_prefixes(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch other
$ bzr colo-branch other-and-more
$ bzr colo-prune other
""")

    def test_dont_prune_subdirectories_of_branch(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch --no-switch origin
$ bzr colo-branch --no-switch origin/trunk
$ bzr colo-prune origin
2>Not removing because of branches in subdirectories.
$ bzr colo-branches
  origin
  origin/trunk
* trunk
""")

    def test_prune_colo_prefix(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch new
$ bzr colo-prune colo:trunk
$ bzr colo-branches
* new
""")

    def test_prune_pipe(self):
        init_workspace(u'.', outf=tests.StringIOWrapper())
        z = ColocatedWorkspace()
        branch = make_colo_branch(z, 'has_next')
        branch.get_config().set_user_option('next_pipe', 'foo')
        self.run_script("""
$ bzr colo-prune colo:has_next
2>Not removing has_next because it is a pipe.  Use remove-pipe --branch.
$ bzr colo-branches
  has_next
* trunk""")


class TestColoClean(ScriptTestCase):

    def test_clean(self):
        self.run_script("""
$ bzr colo-init
$ bzr ci -m 'trunk revision' --unchanged
$ bzr colo-branch new
$ bzr ci -m 'a revision' --unchanged
$ bzr switch trunk
$ bzr colo-prune new
$ bzr colo-clean
""")
        repo = ColocatedWorkspace().repository()
        self.assertEqual(len(repo.all_revision_ids()), 1)

    def test_clean_early_branch(self):
        self.run_script("""
$ bzr colo-init
$ bzr ci -m 'first revision' --unchanged
$ bzr ci -m 'second revision' --unchanged
$ bzr colo-branch -r 1 new
$ bzr ci -m 'new revision' --unchanged
$ bzr switch trunk
$ bzr colo-prune new
$ bzr colo-clean
""")
        self.assertEqual(
            len(ColocatedWorkspace().repository().all_revision_ids()), 2)

    def test_clean_merge(self):
        self.run_script("""
$ bzr colo-init
$ bzr ci -m 'first revision' --unchanged
$ bzr ci -m 'second revision' --unchanged
$ bzr colo-branch -r 1 new
$ bzr ci -m 'new revision' --unchanged
$ bzr switch trunk
$ bzr merge colo:new
$ bzr ci -m 'merge revision'
$ bzr colo-prune new
$ bzr colo-clean
""")
        # clean shouldn't remove anything
        self.assertEqual(
            len(ColocatedWorkspace().repository().all_revision_ids()), 4)

    def test_clean_very_old_format(self):
        self.run_script("""
$ bzr colo-init --knit
$ bzr colo-clean
2>bzr: ERROR: Can't clean the repository at .../.bzr/branches
""")

    def test_clean_old_format(self):
        self.run_script("""
$ bzr colo-init --pack-0.92
$ bzr colo-clean
""")


class TestColoIfy(ScriptTestCase):

    def test_colo_ify(self):
        self.run_script("""
$ bzr init test
$ cd test
$ bzr colo-ify
""")

    def test_colo_ify_change_name(self):
        self.run_script("""
$ bzr init test
$ cd test
$ bzr colo-ify --trunk-name=HEAD
$ bzr colo-branches
* HEAD
""")

    def test_colo_ify_others(self):
        self.run_script("""
$ bzr init test
$ bzr init test2
$ cd test
$ bzr colo-ify ../test2
$ bzr colo-branches
  test2
* trunk
""")

    def test_colo_ify_check_no_parent(self):
        self.run_script("""
$ bzr init test
$ cd test
$ bzr colo-ify
""")
        out, err = self.run_bzr(['info'])
        self.assertNotContainsRe(out, 'parent')

    def test_colo_ify_check_parent(self):
        self.run_script("""
$ bzr init test
$ bzr branch test test2
$ bzr branch test2 test3
$ cd test
$ bzr colo-ify ../test2 ../test3
$ bzr info colo:test3
...
  parent branch: .../test2
""")

    def test_colo_ify_bound(self):
        self.run_script("""
                        $ bzr init a
                        $ bzr co a b
                        $ cd b
                        $ bzr colo-ify
                        $ bzr info
                        """)
        out, err = self.run_bzr(['info'])
        self.assertContainsRe(out, 'checkout of branch')

class TestColoFixup(ScriptTestCase):

    def test_fixup_is_needed(self):
        self.run_script("""
$ bzr colo-init test
$ mv test test2
$ cd test2
""")
        self.run_bzr(['colo-branches'], retcode=3, 
                     error_regexes=['Not a branch:'])

    def test_fixup(self):
        self.run_script("""
$ bzr colo-init test
$ mv test test2
$ cd test2
$ bzr colo-fixup
$ bzr colo-branches
* trunk
""")

    def test_fixup_multiple(self):
        self.run_script("""
$ bzr colo-init test
$ cd test
$ bzr colo-branch feature
$ cd ..
$ mv test test2
$ cd test2
$ bzr colo-fixup
$ bzr colo-branches
* feature
  trunk
""")

    def test_fixup_hierarchical(self):
        self.run_script("""
$ bzr colo-init test
$ cd test
$ bzr colo-branch a/b
$ cd ..
$ mv test test2
$ cd test2
$ bzr colo-fixup
$ bzr colo-branches
* a/b
  trunk
""")

    def test_fixup_hierarchical_from_trunk(self):
        self.run_script("""
$ bzr colo-init test
$ cd test
$ bzr colo-branch a/b
$ bzr switch colo:trunk
$ cd ..
$ mv test test2
$ cd test2
$ bzr colo-fixup
$ bzr colo-branches
  a/b
* trunk
""")

    def test_fixup_from_subdir(self):
        self.run_script("""
$ bzr colo-init test
$ cd test
$ mkdir subdir
$ cd ..
$ mv test test2
$ cd test2/subdir
$ bzr colo-fixup
$ bzr colo-branches
* trunk
""")


class TestHierarchicalNames(ScriptTestCase):

    def test_branch(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch a/b
$ bzr colo-branch a/c
$ bzr colo-branch a/c/d
""")

    def test_branches(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch a/b
$ bzr colo-branches
* a/b
  trunk
""")

    def test_checkout(self):
        self.run_script("""
$ bzr colo-init test
$ cd test
$ bzr colo-branch a/b
$ bzr colo-checkout ../b-checkout
$ cd ../b-checkout
$ bzr switch colo:trunk
""")

    def test_prune(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch a/b
$ bzr switch colo:trunk
$ bzr colo-prune a/b
$ bzr colo-branches
* trunk
""")


class TestColoPull(ScriptTestCase):

    def test_pull(self):
        self.run_script("""
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-branch origin/test
$ bzr colo-pull
2>Updating origin/test from .../trunk/
No revisions or tags to pull.
""")

    def test_pull_outside_branch(self):
        self.run_script("""
$ bzr init branch
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-branch origin/test
$ bzr pull --remember ../branch
$ bzr colo-pull
2>Updating origin/test from .../branch/
No revisions or tags to pull.
""")

    def test_pull_revision(self):
        self.run_script("""
$ bzr init branch
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-branch origin/test
$ bzr pull --remember ../branch
$ cd ../branch
$ echo "contents" > file
$ bzr add
$ bzr ci -m 'first'
$ cd ../workspace
$ bzr colo-pull
Now on revision 1.
""")

    def test_pull_diverged(self):
        self.run_script("""
$ bzr init branch
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-branch origin/test
$ bzr pull --remember ../branch
$ cd ../branch
$ echo "contents" > file
$ bzr add
$ bzr ci -m 'first'
$ cd ../workspace
$ echo "other contents" > file2
$ bzr add
$ bzr ci -m 'a new revision'
""")
        out, err = self.run_bzr('colo-pull', retcode=3)
        self.assertEqual(out, '')
        self.assertContainsRe(err, 'bzr: ERROR: These branches have diverged.'
                              ' Use the missing command to see how.\n'
                              'Use the merge command to reconcile them.\n')

    def test_pull_multiple(self):
        self.run_script("""
$ bzr init branch
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-branch origin/test
$ bzr pull --remember ../branch
$ bzr colo-branch origin/other
$ bzr pull --remember ../branch
$ cd ../branch
$ echo "contents" > file
$ bzr add
$ bzr ci -m 'first'
$ cd ../workspace
$ bzr colo-pull
2>Updating origin/other from .../branch/
2>All changes applied successfully.
2>Updating origin/test from .../branch/
Now on revision 1.
Now on revision 1.
""")

    def test_pull_current(self):
        self.run_script("""
$ bzr init branch
$ bzr colo-init workspace
$ cd workspace
$ bzr colo-mv trunk origin/trunk
$ bzr pull --remember ../branch
$ cd ../branch
$ echo content > file
$ bzr add
$ bzr ci -m 'a revision on branch'
$ cd ../workspace
$ bzr colo-pull
Now on revision 1.
$ cat file
content
""")

    def test_pull_subdirectory(self):
        self.run_script("""
$ bzr init branch
$ bzr colo-init workspace
$ cd workspace
$ bzr pull --remember ../branch
$ mkdir subdir
$ cd subdir
$ bzr colo-pull
""")
                        


class TestColoMv(ScriptTestCase):

    def test_mv(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branches
* trunk
$ bzr colo-mv trunk test
$ bzr colo-branches
* test
""")

    def test_mv_hierarchical(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branches
* trunk
$ bzr colo-mv trunk origin/trunk
$ bzr colo-branches
* origin/trunk
""")

    def test_mv_hierarchical_existing(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch origin/test
$ bzr colo-mv trunk origin/trunk
""")

    def test_mv_not_current(self):
        self.run_script("""
$ bzr colo-init
$ bzr colo-branch new
$ bzr colo-mv trunk HEAD
$ bzr colo-branches
  HEAD
* new
""")


class TestNoTree(ScriptTestCase):

    def test_list_branches(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-branches
  trunk
""")

    def test_branch_current(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-branch new
2>bzr: ERROR: Cannot find a current branch in a no-tree colocated workspace.
""")

    def test_branch_from(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-branch --from=trunk new
$ bzr colo-branches
  new
  trunk
""")

    def test_pull(self):
        self.run_script("""
$ bzr colo-init remote
$ bzr colo-init --no-tree --trunk-name=origin/trunk local
$ cd local
$ bzr branch colo:../remote:trunk colo:origin/remote
$ bzr colo-pull
2>Updating origin/remote from .../remote/.bzr/branches/trunk/
""")

    def test_checkout(self):
        self.run_script("""
$ bzr colo-init --no-tree branch
$ cd branch
$ bzr colo-checkout ../checkout
2>bzr: ERROR: Cannot find a current branch in a no-tree colocated workspace.
""")

    def test_prune(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-branch --from=trunk new
$ bzr colo-prune new
""")

    def test_mv(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-mv trunk HEAD
""")

    def test_clean(self):
        self.run_script("""
$ bzr colo-init --no-tree
$ bzr colo-clean
""")

    def test_fixup(self):
        self.run_script("""
$ bzr colo-init --no-tree first
$ mv first second
$ cd second
$ bzr colo-fixup
2>bzr: ERROR: Not a branch: ...
""")

class TestNick(ScriptTestCase):

    def setUp(self):
        ScriptTestCase.setUp(self)
        branch.Branch.hooks.install_named_hook('post_branch_init',
            colo_nick_hook, 'colocated branch name nick')
        
    def test_no_dir_in_nick(self):
        self.run_script("""
$ bzr config --scope=bazaar colo.dir_in_nick=False
$ bzr hooks
...
  post_branch_init:
    colocated branch name nick
...
$ bzr colo-init test
$ cd test
$ bzr nick
trunk
$ bzr colo-branch bug/long-name
$ bzr nick
bug/long-name
""")

    def test_dir_in_nick(self):
        self.run_script("""
$ bzr config --scope=bazaar colo.dir_in_nick=True
$ bzr colo-init test
$ cd test
$ bzr nick
test/trunk
$ bzr switch -b feature
$ bzr nick
test/feature
$ bzr colo-branch subdir/feature
$ bzr nick
test/subdir/feature
""")

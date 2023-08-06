# Copyright 2009 Neil Martinsen-Burrell
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

"""Work with colocated branches using current technology.

In order to provide a faster and simpler working model, this plugin tries
to support a configuration similar to git and Mercurial's colocated branches,
where there is a single working tree that can be switched between multiple
branches that all co-exist in the same directory.  This working model is
entirely possible using Bazaar's existing technology, and this plugin aims to
make it as simple as possible to use that model.  

This plugin does not add any new formats or objects to Bazaar, it simply
provides convenience commands for working with a certain *convention* for
branch storage.  This plugin provides the following commands

    * colo-init
    * colo-branch
    * colo-branches
    * qbranches (if the qbzr plugin is installed)
    * colo-fetch
    * colo-pull
    * colo-checkout
    * colo-prune
    * qprune (if the qbzr plugin is installed)
    * colo-mv
    * colo-clean
    * colo-ify
    * colo-fixup
    * colo-sync-from
    * colo-sync-to
    * qcoloswitch (if the qbzr plugin is installed)

For more information on working with this plugin, see ``bzr help
colo-tutorial`` and the help for the individual commands.

Referring to Colocated Branches
-------------------------------

This plugin adds a directory service of "colo:" that can be used to refer to
branches inside of the ``.bzr/branches`` directory.  So, for example we could
``bzr switch colo:fix-eol-bug`` to do work in the colocated ``fix-eol-bug``
branch.  Note that in some cases, the "colo:" prefix is unnecessary because
Bazaar automatically looks for branches in the directory where the current
branch is located.  So the previous command would also work with ``bzr switch
fix-eol-bug`` because switch searches sibling directories automatically.  (If
hierarchical branch names such as ``bugs/1024`` are used, then simply doing
``bzr switch trunk`` may fail, while ``bzr switch colo:trunk`` will always
work.)

From within a colocated workspace, the specifier ``colo:branch_name`` refers
to the branch with that name in the current colocated workspace.  It is
possible to refer to colocated branches in *other* workspaces using the syntax
``colo:workspace_location:branch_name``.  The ``workspace_location`` in this
form can be either a path (e.g. ``colo:../other_project:trunk``) or a URL
(e.g. ``colo:bzr+ssh://hostname/path/to/workspace:trunk``).

"""


from bzrlib import branch, directory_service, config
from bzrlib.commands import plugin_cmds
from bzrlib.help_topics import topic_registry

from bzrlib.plugins.colo.info import bzr_plugin_version as version_info
from bzrlib.plugins.colo.colocated import colo_nick_hook


def test_suite():
    from unittest import TestSuite
    import bzrlib.plugins.colo.tests
    res = TestSuite()
    res.addTest(bzrlib.plugins.colo.tests.test_suite())
    return res

directory_service.directories.register_lazy('colo:',
    'bzrlib.plugins.colo.colocated', 'ColocatedDirectory',
    'Easy access to colocated branches')

topic_registry.register_lazy("colo-tutorial",
    "bzrlib.plugins.colo.tutorial", "_colo_tutorial",
    "Tutorial on colocated branches with the colo plugin")

debug_option = config.GlobalConfig().get_user_option('colo.debug')
if debug_option is not None:
    if debug_option.lower() == 'false':
        import trace
        trace.DEBUG = False

lazy_commands = [('cmd_colo_init', []),
                 ('cmd_colo_branch', []),
                 ('cmd_colo_branches', []),
                 ('cmd_colo_fetch', []),
                 ('cmd_colo_pull', []),
                 ('cmd_colo_checkout', ['colo-co']),
                 ('cmd_colo_mv', ['colo-move', 'colo-rename']),
                 ('cmd_colo_prune', ['colo-delete']),
                 ('cmd_colo_clean', []),
                 ('cmd_colo_ify', []),
                 ('cmd_colo_fixup', []),
                 ('cmd_qprune', ['qdelete']),
                 ('cmd_qbranches', []),
                 ('cmd_qcoloswitch', []),
                 ('cmd_colo_sync_from', []),
                 ('cmd_colo_sync_to', []),
                ]
for cmd, aliases in lazy_commands:
    plugin_cmds.register_lazy(cmd, aliases, 'bzrlib.plugins.colo.commands')

branch.Branch.hooks.install_named_hook('post_branch_init',
                                       colo_nick_hook,
                                       'colocated branch name nick'
                                      )

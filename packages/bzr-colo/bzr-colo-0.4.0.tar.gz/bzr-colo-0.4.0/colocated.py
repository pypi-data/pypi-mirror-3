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

from bzrlib.lazy_import import lazy_import
lazy_import(globals(), '''
from bzrlib import (branch as _mod_branch,
                    bzrdir,
                    config,
                    repository,
                    transport,
                    urlutils, 
                   )
''')
from bzrlib import (config,
                    errors,
                    osutils,
                   )

from trace import mutter

COLOCATED_LOCATION = osutils.pathjoin(u'.bzr', u'branches')

class NoColocatedWorkspace(errors.BzrCommandError):

    _fmt = "No colocated workspace in %(directory)s"


class NoCurrentBranch(errors.BzrCommandError):

    _fmt = "Cannot find a current branch in a no-tree colocated workspace."


class ColocatedWorkspace(object):

    """An abstract representation of a colocated workspace."""

    def __init__(self, location=u'.'):
        """A colocated workspace that contains the given path or URL."""
        try:
            a_bzrdir, extra_path = bzrdir.BzrDir.open_containing(location)
        except errors.NotBranchError:
            raise NoColocatedWorkspace(directory=location)
        self.has_tree = a_bzrdir.has_workingtree()

        if not self.has_tree:
            self.base = urlutils.normalize_url(location)
        else:
            branch = a_bzrdir.open_branch()
            try:
                self.base = branch.base[:branch.base.index(COLOCATED_LOCATION)]
            except ValueError:
                raise NoColocatedWorkspace(directory=location)

        self.repo_location = urlutils.join(self.base, COLOCATED_LOCATION)

    @classmethod
    def open_contains_branch(klass, a_branch):
        """A colocated workspace that contains the given branch object."""
        index = a_branch.base.find(COLOCATED_LOCATION)
        if index < 0:
            raise NoColocatedWorkspace(directory=a_branch.base)
        return ColocatedWorkspace(a_branch.base[:index])
        

    def url_for_name(self, name):
        """Return a URL to the named branch."""
        # normalize backslashes to forward slashes here
        if '\\' in name:
            mutter('bzr-colo: Replacing backslash in %s' % name)
            name = name.replace('\\', '/')

        return urlutils.join(self.repo_location, name)

    def branches(self):
        """A generator of the branches in the colocated workspace."""
        t = self.repo_transport()
        return (b for b in bzrdir.BzrDir.find_branches(t) 
                if b.base.startswith(t.base))

    def _name_from_branch(self, branch):
        """A name for the given branch object."""
        return branch.base[len(self.repo_location):].strip('/')

    def repo_transport(self):
        """A transport pointing to the shared repository."""
        return transport.get_transport(self.repo_location)

    def repository(self):
        """The shared repository object."""
        return repository.Repository.open(self.repo_location)

    HIDDEN_STATUSES = ['merged',
                       'abandoned',
                       'hidden',
                      ]

    def _should_display_branch(self, br_to_display, name=None):
        if name is None:
            name = self._name_from_branch(br_to_display)
        for p in name.split('/'):
            if p.startswith('.'):
                return False

        status = br_to_display.get_config().get_user_option('bzr.branch.status')
        if status is not None:
            if status.lower() in self.HIDDEN_STATUSES:
                return False

        return True

    def branch_names(self, all=True):
        """A generator of the names of the branches."""
        current_name = self.current_branch_name()
        for b in self.branches():
            name = self._name_from_branch(b)
            if not all and name != current_name:
                if self._should_display_branch(b, name):
                    yield name
                else:
                    continue
            else:
                yield name

    def branch_with_name(self, name):
        return _mod_branch.Branch.open(self.url_for_name(name))

    def current_branch(self, directory=u'.'):
        """The current branch object.

        If this workspace doesn't have a working tree and thus doesn't have a
        current branch, raise an exception.
        """
        if not self.has_tree:
            raise NoCurrentBranch()
        return _mod_branch.Branch.open_containing(directory)[0]

    def current_branch_name(self, directory=u'.'):
        """The name of the current branch.

        If this workspace doesn't have a working tree and thus doesn't have
        a current branch, return None.
        """
        try:
            return self._name_from_branch(self.current_branch(directory))
        except NoCurrentBranch:
            return None

    def is_pipe(self, name):
        """Return True if the name is a pipe.

        If name does not correspond to a branch, or the branch is not part of
        a pipeline, return False.
        """
        try:
            branch = self.branch_with_name(name)
        except errors.NotBranchError:
            return False
        config = branch.get_config()
        next_pipe = config.get_user_option('next_pipe')
        if next_pipe == '':
            next_pipe = None
        if next_pipe is not None:
            return True
        prev_pipe = config.get_user_option('prev_pipe')
        if prev_pipe == '':
            prev_pipe = None
        if prev_pipe is not None:
            return True
        return False

    def get_config(self):
        return ColocatedConfig(self)


class RepositoryWorkspace(ColocatedWorkspace):

    """A workspace with branches stored as subdirectories of the root."""

    def __init__(self, location='.'):
        super(RepositoryWorkspace, self).__init__(location)
        self.repo_location = self.base


class ColocatedDirectory(object):

    """Directory lookup for branches that are colocated with the tree.
    
    If the name portion contains a ":", then interpret the name as
    workspace_location:branch_name.  If not, interpret name as a branch in the
    current colocated workspace. 
    """

    def look_up(self, name, url):
        url_piece, sep, branch_name = name.rpartition(':') 
        if not url_piece:
            url_piece = u'.'
        return ColocatedWorkspace(url_piece).url_for_name(branch_name)


class ColocatedConfig(config.BzrDirConfig):

    """Store configuration information for a colocated workspace."""

    def __init__(self, workspace):
        super(ColocatedConfig, self).__init__(bzrdir.BzrDir.open(workspace.base))

    def _get_option(self, option):
        if self._config is None:
            return None
        value = self._config.get_option(option)
        if value == '':
            value = None
        return value

    def get_sync_from_location(self):
        """Get the location to synchronize from"""
        return self._get_option('colo.sync_from_location')

    def get_sync_to_location(self):
        """Get the location to synchronize to"""
        return self._get_option('colo.sync_to_location')

    def set_sync_from_location(self, location):
        """Set the location to synchronize from"""
        if location is None:
            location = ''
        self._config.set_option(location, 'colo.sync_from_location')

    def set_sync_to_location(self, location):
        """Set the location to synchronize to"""
        if location is None:
            location = ''
        self._config.set_option(location, 'colo.sync_to_location')

def colo_nick_hook(branch_init_params):
    mutter('setting nick from hook')
    branch = branch_init_params.branch
    try:
        workspace = ColocatedWorkspace.open_contains_branch(branch)
    except NoColocatedWorkspace:
        return
    option = config.GlobalConfig().get_user_option('colo.dir_in_nick')
    if option is None:
        option = 'false'
    if option.lower() == 'true':
        basename = workspace.repo_location.split('/')[-3]
        branch.nick = basename+'/'+workspace._name_from_branch(branch)
    else:
        branch.nick = workspace._name_from_branch(branch)

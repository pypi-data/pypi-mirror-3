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

import sys
import bzrlib
from bzrlib.lazy_import import lazy_import
lazy_import(globals(), '''
from bzrlib import (api,
                    branch as _mod_branch,
                    builtins,
                    bzrdir,
                    directory_service,
                    option,
                    osutils,
                    reconfigure,
                    switch,
                    trace, 
                    transport,
                    urlutils, 
                    workingtree,
                   )
from bzrlib.repofmt import groupcompress_repo, knitpack_repo
''')
from bzrlib import (commands,
                    errors,
                   )


from colocated import (COLOCATED_LOCATION,
                       ColocatedWorkspace,
                       NoColocatedWorkspace,
                       RepositoryWorkspace
                      )
from trace import mutter

COLOCATED_STAGING = u'.bzrbranches'

def _ensure_base_of_location(to_transport, create_parent_dirs):
    try:
        to_transport.ensure_base()
    except errors.NoSuchFile:
        if not create_parent_dirs:
            raise
        to_transport.create_prefix()


def _wrap_command_object(cmd_obj, outf):
    # We explicitly reuse the current command's output stream rather than
    # setup a fresh one here
    cmd_obj.outf = outf
    if (2,0) < api.get_current_api_version(bzrlib) < (2,2):
        mutter('Using 2.1 compatibility')
        cmd_obj.run = cmd_obj.run_direct
    return cmd_obj
    

class HideStagingWrapper(object):

    """Hide the staging directory in output."""

    def __init__(self, stream):
        self.stream = stream

    def __getattr__(self, name):
        return getattr(self.stream, name)

    def _hide(self, input_string):
        return input_string.replace(COLOCATED_STAGING,
                                    COLOCATED_LOCATION
                                   )

    def write(self, input_string, *args, **kwargs):
        self.stream.write(self._hide(input_string),
                          *args, **kwargs)

    def writelines(self, line_list, *args, **kwargs):
        self.stream.writelines(self._hide(line) for line in line_list)


def init_workspace(location, format=None, create_parent_dirs=False,
                   outf=None, branch_name='trunk', create_tree=True):
    """Create a colocated workspace at the specified location.
    
    :param location: A path or URL for where to make the workspace
    :param format: A Bazaar format to use for the branches and trees
    :param create_parent_dirs: Whether or not to create the directories
      containing the workspace
    """
    if outf is None:
        outf = sys.stdout
    if format is None:
        format = bzrdir.format_registry.get('default')()
    
    # if the repository is going to live inside of the checkout's .bzr,
    # we need to create the checkout's .bzr first since if that can't happen
    # then we don't want to create the repository under that.  But, we can't
    # create a checkout since we don't have a branch to check out.  Instead
    # we put the repository in a staging location
    top_transport = transport.get_transport(location)
    _ensure_base_of_location(top_transport, create_parent_dirs)
    topdir = format.initialize_on_transport(top_transport)

    repo_transport = top_transport.clone(COLOCATED_LOCATION)
    repo_transport.ensure_base()
    repodir = format.initialize_on_transport(repo_transport)
    repo = repodir.create_repository(shared=True)
    repo.set_make_working_trees(False)

    branch_transport = repo_transport.clone(branch_name)
    branch_transport.create_prefix()
    branch_transport.ensure_base()
    branchdir = format.initialize_on_transport(branch_transport)
    branch = branchdir.create_branch()

    if create_tree:
        from_branch = _mod_branch.BranchReferenceFormat().initialize(
            topdir, target_branch=branch)
        topdir.create_workingtree(from_branch=from_branch)
        


class cmd_colo_init(commands.Command):

    """Create a working tree with colocated branches.

    A colocated workspace is a working tree that also contains all of its
    branches within the same directory.  The branches are stored in the
    .bzr/branches subdirectory.  They may be easily referred to using the 
    colo: specifier.

    By default, the initial branch is called "trunk".  A different name can 
    be specified with the --trunk-name option.  For creating colocated
    workspaces remotely, a --no-tree options is available for situations
    where it isn't possible or desired to create a working tree.
    """

    takes_options = [
        option.Option('create-prefix',
           help='Create the path leading up to the location '
                'if it does not already exist.'),
        option.RegistryOption('format',
                help='Specify a format for the repository, etc. '
                'See "help formats".',
                lazy_registry=('bzrlib.bzrdir', 'format_registry'),
                converter=lambda name: bzrdir.format_registry.make_bzrdir(name),
                value_switches=True,
                title="Storage Format",
                ),
        option.Option('trunk-name',
                      help='Name for the trunk branch',
                      type=unicode),
        option.Option('no-tree',
                      help='Create a workspace without a working tree'),
        ]
    takes_args = ['location?']
    
    def run(self, location=u'.', format=None, create_prefix=False,
            trunk_name='trunk', no_tree=False):
        if format is None:
            format = bzrdir.format_registry.make_bzrdir('default')
        init_workspace(location, format=format, 
                       create_parent_dirs=create_prefix,
                       outf=self.outf, branch_name=trunk_name,
                       create_tree=(not no_tree)
                      )


class cmd_colo_branch(commands.Command):

    """Make a new branch from the currently active branch.

    In a colocated workspace, there is always one branch active at a time,
    so to create a new branch, we need to only specify the name of the new
    branch.  If the ``-r`` option is given, then the branch is made from
    the specified revision of the current branch.  By default, the branch
    is made from the current branch, but a different branch name to branch
    from can be specified with the ``--from-branch`` option.
    """

    takes_options = ['revision',
        option.Option('no-switch',
               help="Don't switch the workspace to the new branch"),
        option.Option('from-branch',
               type=unicode,
               help='name of the branch to branch from'),
                    ]
    takes_args = ['new_branch']

    def run(self, new_branch, revision=None, no_switch=False,
            from_branch=None):
        if not new_branch.startswith('colo:'):
            new_branch = 'colo:' + new_branch
        new_location = directory_service.directories.dereference(new_branch)
        transport.get_transport(new_location).create_prefix()
        workspace = ColocatedWorkspace()
        if not workspace.has_tree:
            no_switch = True
        if from_branch is not None:
            from_branch = workspace.branch_with_name(from_branch)
        else:
            from_branch = workspace.current_branch()
        branch_cmd = _wrap_command_object(builtins.cmd_branch(), self.outf)
        branch_cmd.run(from_branch.base, revision=revision,
                       to_location=new_location, no_tree=True,
                       switch=(not no_switch), use_existing_dir=True)


class cmd_colo_branches(commands.Command):

    """List all of the branches in a colocated workspace.
    
    If the current directory is a working tree pointing to one of the branches,
    that branch is marked with a "*".

    Branches whose names start with a period or that have the option 
    bzr.branch.status=hidden (or "merged", or "abandoned") are not shown
    unless the "--all" option is given.
    """

    takes_options = [option.Option('all', 
                                   help="Show all branches, even hidden ones"),
                    ]
    takes_args = ['location?']
    
    def run(self, location=u'.', all=False):
        workspace = ColocatedWorkspace(location)
        current_name = workspace.current_branch_name()
        for name in workspace.branch_names(all):
            leader = '  '
            if name == current_name:
                leader = '* '
            self.outf.write(leader + name + '\n')


class cmd_colo_fetch(commands.Command):
    
    """Fetch an external project into a new colocated workspace.
    
    This creates a colocated workspace at the specified location with a single
    branch named "origin/trunk" that has the contents of the external project.
    If you would like to specify a different name for the new branch, use the
    ``--trunk-name`` option.  If you don't specify a TO_LOCATION, then one
    will be derived from the final component of the FROM_LOCATION (similar
    to ``bzr branch``).
    
    """

    takes_args = ['from_location', 'to_location?']
    takes_options = [
        option.Option('create-prefix',
           help='Create the path leading up to the location '
                'if it does not already exist.'),
        option.RegistryOption('format',
                help='Specify a format for the repository, etc. '
                'See "help formats".',
                lazy_registry=('bzrlib.bzrdir', 'format_registry'),
                converter=lambda name: bzrdir.format_registry.make_bzrdir(name),
                value_switches=True,
                title="Storage Format",
                ),
        option.Option('trunk-name',
            help='Name of the branch to create; default is "origin/trunk"',
            type=unicode),
        ]

    def run(self, from_location=None, to_location=None,
            create_prefix=False, format=None, trunk_name='origin/trunk'):
        if to_location is None:
            to_location = urlutils.derive_to_location(from_location)
        init_workspace(to_location, format=format, 
                       create_parent_dirs=create_prefix,
                       outf=self.outf, branch_name=trunk_name,
                      )
        pull_cmd = _wrap_command_object(builtins.cmd_pull(), self.outf)
        pull_cmd.run(location=from_location, directory=to_location,
                     remember=True)


class cmd_colo_checkout(commands.Command):

    """Create a checkout of this branch in a new directory.
    
    By default this command makes a new checkout of the current branch in
    the specified directory.  Using the ``--create`` option, a new branch
    named after the last component of the new directory is created, and
    the new checkout is switched to that new branch.
    """

    aliases = ['colo-co']
    takes_args = ['to_directory']
    takes_options = [
        option.Option('create', short_name='b',
               help="Also create a new colocated branch by this name"),
        option.Option('from-branch',
               type=unicode,
               help='name of the branch to branch from'),
        ]

    def run(self, to_directory, create=False, from_branch=None):
        workspace = ColocatedWorkspace()
        if from_branch is not None:
            from_branch = workspace.branch_with_name(from_branch)
        else:
            from_branch = workspace.current_branch()
        current_branch_url = from_branch.base
        if create:
            new_branch_name = osutils.basename(to_directory)
            _wrap_command_object(cmd_colo_branch(), self.outf).run(
                new_branch_name, no_switch=True)
            branch_location = urlutils.join(current_branch_url, '..',
                                            new_branch_name)
        else:
            branch_location = current_branch_url
        # create a new checkout
        checkout_cmd = _wrap_command_object(builtins.cmd_checkout(),
                                            self.outf)
        checkout_cmd.run(branch_location, to_location=to_directory,
                         lightweight=True)


class cmd_colo_prune(commands.Command):
    
    """Remove a branch from the colocated workspace.
    
    This commands removes the specified branches from the colocated workspace
    by removing them from the filesystem.  By default, it does not remove the
    revisions from the shared repository.  If it is desired to remove the
    revisions that are only present in the removed branches, then the
    ``--clean`` option may be given.
    """

    aliases = ['colo-delete']
    takes_options = [option.Option('clean',
                            help='Clean the repository after pruning.'),
                    ]
    takes_args = ['branch*']
    _see_also = ['colo-clean']

    def run(self, branch_list=None, clean=False):
        if branch_list is None:
            return
        if len(branch_list) < 1:
            raise errors.BzrOptionError('Must specify a branch to prune.')
        workspace = ColocatedWorkspace()
        all_branches = list(workspace.branch_names())
        to_transport = workspace.repo_transport()
        current_name = workspace.current_branch_name()
        for branch_name in branch_list:
            if branch_name.startswith('colo:'):
                branch_name = branch_name[5:]
            if branch_name == current_name:
                trace.note('Not removing current branch %s.' % branch_name)
                return
            elif branch_name not in all_branches:
                trace.note('Not removing %s because it is not a branch.' %
                           branch_name)
                return
            elif workspace.is_pipe(branch_name):
                trace.note('Not removing %s because it is a pipe.  Use'
                           ' remove-pipe --branch.' % branch_name)
                return
            else:
                # don't delete the whole tree if there are other branches
                # that are subdirectories of this one
                other_branches = all_branches
                other_branches.remove(branch_name)
                if any([br.startswith(branch_name+'/') 
                        for br in other_branches]):
                    trace.note('Not removing because of branches in '
                               'subdirectories.')
                    return
                to_transport.delete_tree(branch_name)
        if clean:
            _clean(self.outf)


class cmd_colo_pull(commands.Command):

    """Update all remote branches.

    A remote branch is one whose name starts with "origin/".  This command
    updates all such branches by doing a pull from their default pull
    location.  To set this location, do ``bzr switch colo:origin/branch_name``
    and ``bzr pull --remember URL``.
    """

    takes_options = [option.Option('directory', short_name='d',
                                   help='colocated workspace to use',
                                   type=unicode),
                    ]
    
    def run(self, directory=u'.'):
        conflicts = 0
        workspace = ColocatedWorkspace(directory)
        current = workspace.current_branch_name()
        for name in (_ for _ in workspace.branch_names()
                       if _.startswith('origin/')):
            br = workspace.branch_with_name(name)
            parent = br.get_parent()
            if parent is None:
                continue
            trace.note('Updating %s from %s' % 
                       (name, urlutils.unescape_for_display(parent,
                                                            self.outf.encoding
                                                           )))
            parent_branch = _mod_branch.Branch.open(parent)
            if parent_branch is not br: # can a branch be its own parent?
                                        # cribbed from bzrlib/builtins.py
                parent_branch.lock_read()
                self.add_cleanup(parent_branch.unlock)
            
            br.lock_write()
            self.add_cleanup(br.unlock)
            result = br.pull(parent_branch)
            self.cleanup_now()

            result.report(self.outf)
            if name == current:
                # update the working tree
                tree, _ = workingtree.WorkingTree.open_containing(directory)
                conflicts = tree.update()
        if conflicts > 0:
            return 1
        else:
            return 0


class cmd_colo_mv(commands.Command):

    """Rename a colocated branch."""

    takes_args = ['oldname', 'newname']
    aliases = ['colo-move', 'colo-rename']

    def run(self, oldname, newname):
        workspace = ColocatedWorkspace()
        current = workspace.current_branch_name()
        repo_transport = workspace.repo_transport()
        to_transport = repo_transport.clone(newname)
        to_transport.create_prefix()
        repo_transport.move(oldname, newname)
        if current == oldname:  #switch checkout to new name
            this_bzrdir, _ = bzrdir.BzrDir.open_containing(u'.')
            switch.switch(this_bzrdir, 
                          workspace.branch_with_name(newname),
                          force=True)


class NotPackRepository(errors.BzrError):

    _fmt = "Can't clean the repository at %(repo)s"

    def __init__(self, repo):
        self.repo = repo


def _clean(outf, directory=u'.'):
    """Clean a colocated workspace's repository"""
    workspace = ColocatedWorkspace(directory)
    repo_path = urlutils.local_path_from_url(workspace.repo_location)
    outf.write("Cleaning repository in %s.\n" % repo_path)
    repo = workspace.repository()
    try:
        pack_collection = repo._pack_collection
    except AttributeError:
        raise NotPackRepository(repo_path)
    repo.lock_read()
    try:
        pack_collection.ensure_loaded()
    finally:
        repo.unlock()

    # Keep all of the revision ids in the ancestry of the current heads
    ancestry = set()
    for b in workspace.branches():
        b.lock_read()
        try:
            ancestry.update(set(rev[0] for rev in 
                b.iter_merge_sorted_revisions(b.last_revision())))
        finally:
            b.unlock()

    old_packs = pack_collection.all_packs()
    if isinstance(repo._format, groupcompress_repo.RepositoryFormat2a):
        packer_class = groupcompress_repo.GCCHKPacker
    elif isinstance(repo._format, 
                    (knitpack_repo.RepositoryFormatKnitPack1,
                     knitpack_repo.RepositoryFormatKnitPack3,
                     knitpack_repo.RepositoryFormatKnitPack4,
                     knitpack_repo.RepositoryFormatKnitPack5,
                     knitpack_repo.RepositoryFormatKnitPack5RichRoot,
                     knitpack_repo.RepositoryFormatKnitPack5RichRootBroken,
                     knitpack_repo.RepositoryFormatKnitPack6,
                     knitpack_repo.RepositoryFormatKnitPack6RichRoot,
                     knitpack_repo.RepositoryFormatPackDevelopment2Subtree,)):
        packer_class = knitpack_repo.KnitPacker
    else:
        trace.show_error("Can't clean repository of type %s",
                         repo.get_format_string()) 
    packer = packer_class(pack_collection,
                          old_packs,
                          suffix='.clean', 
                          revision_ids=ancestry)
    repo.lock_write()
    try:
        result = packer.pack()
    finally:
        repo.unlock()

    if result is None:
        trace.note('No cleaning necessary.')
        return

    for pack in old_packs:
        pack_collection._remove_pack_from_memory(pack)
    pack_collection._save_pack_names(clear_obsolete_packs=True)
    pack_collection._obsolete_packs(old_packs)


class cmd_colo_clean(commands.Command):
    
    """Clean unused revisions from the repository.

    An unused revision is one that is not in the ancestry of any of the 
    active branches in the workspace.  This command can be used after the
    ``colo-prune`` command to remove revisions that were only present in
    the branch that was pruned.
    """

    def run(self):
        _clean(self.outf)


class cmd_colo_ify(commands.Command):

    """Convert an existing branch into a colocated workspace.

    This converts an existing branch into a colocated workspace.  Other
    branches can be added to the workspace by giving them as arguments.  The
    names of the other branches will be determined from their nicknames.  To
    use a different name for the current branch in the colocated workspace,
    use the ``--trunk-name`` option.
    """

    _see_also = ['nick']
    takes_args = ['other_location*']
    takes_options = [option.Option('trunk-name',
                                   help='The name to use for this branch in '
                                        'the colocated workspace',
                                   type=unicode),
                    ]

    def run(self, other_location_list=[], trunk_name='trunk'):
        the_bzrdir, relpath = bzrdir.BzrDir.open_containing(u'.')
        the_bzrdir.root_transport.mkdir(COLOCATED_LOCATION)
        repo_location = urlutils.join(the_bzrdir.root_transport.base,
                          COLOCATED_LOCATION)
        new_transport = transport.get_transport(repo_location,
            possible_transports=[the_bzrdir.root_transport])
        new_bzrdir = the_bzrdir.cloning_metadir().initialize_on_transport(
                         new_transport)
        new_repo = new_bzrdir.create_repository(shared=True)
        new_repo.set_make_working_trees(False)

        the_branch = _mod_branch.Branch.open_containing(u'.')[0]
        branch_location = urlutils.join(repo_location, trunk_name)
        new_branch_bzrdir = the_bzrdir.sprout(branch_location,
                                       source_branch=the_branch,
                                       create_tree_if_local=False)
        new_branch = new_branch_bzrdir.open_branch()
        new_branch.set_parent(None)
        self._copy_locations(the_branch, new_branch)

        reconfiguration = reconfigure.Reconfigure.to_lightweight_checkout(
                              the_bzrdir, reference_location=branch_location)
        reconfiguration.apply()

        if other_location_list is None:
            return
        for location in other_location_list:
            source_branch = _mod_branch.Branch.open(location)
            to_location = urlutils.join(repo_location, source_branch.nick)
            new_bzrdir = source_branch.bzrdir.sprout(to_location,
                source_branch=source_branch,
                create_tree_if_local=False)
            self._copy_locations(source_branch, new_bzrdir.open_branch())

    def _copy_locations(self, source, dest):
        """Set all of the locations for one branch to those of another."""
        location_methods = [(source.get_parent, dest.set_parent),
                            (source.get_push_location,
                             dest.set_push_location),
                            (source.get_submit_branch,
                             dest.set_submit_branch),
                           ]
        for source_meth, dest_meth in location_methods:
            val = source_meth()
            if val is not None:
                dest_meth(val)
        dest.set_bound_location(source.get_bound_location())


class cmd_colo_fixup(commands.Command):

    """Fix the checkout reference after moving a colocated workspace.

    Because Bazaar uses absolute pathnames in storing references to branches,
    when a colocated workspace is moved on disk, the link from the
    checkout to the current branch gets broken.  This command uses a simple
    heuristic to try to fix that reference.  If it doesn't work, then the
    command ``bzr switch --force .bzr/branches/<current branch name>`` will
    always work.
    """
    
    def run(self):
        # get the current location which is assumed to be wrong
        the_bzrdir = bzrdir.BzrDir.open_containing(u'.')[0]
        format = the_bzrdir.find_branch_format()
        if getattr(format, 'get_reference', None) is not None:
            location = format.get_reference(the_bzrdir)
        # find the root of the working tree
        root_location = the_bzrdir.root_transport.base
        orig, _, location_in_repo = location.partition(COLOCATED_LOCATION)
        try:
            format.set_reference(the_bzrdir,
                                 None,
                                 _mod_branch.Branch.open(
                                     urlutils.join(root_location,
                                         COLOCATED_LOCATION,
                                         location_in_repo.strip('/'))))
        except TypeError:
            # In 2.1, need to use one less argument
            format.set_reference(the_bzrdir,
                                 _mod_branch.Branch.open(
                                     urlutils.join(root_location,
                                         COLOCATED_LOCATION,
                                         location_in_repo.strip('/'))))


class NoQBzrError(errors.BzrCommandError):

    _fmt = '%(name)s requires the qbzr plugin version >= 0.18.1.'


class cmd_qbranches(commands.Command):

    """List colocated branches (requires qbzr)"""

    def run(self):
        raise NoQBzrError(name='qbranches')


class cmd_qprune(commands.Command):

    """Remove colocated branches (requires qbzr)"""

    aliases = ['qdelete']

    def run(self):
        raise NoQBzrError(name='qprune')


class cmd_qcoloswitch(commands.Command):

    """Remove colocated branches (requires qbzr)"""

    def run(self):
        raise NoQBzrError(name='qcoloswitch')


qbzr = None
try:
    import bzrlib.plugins.qbzr as qbzr
    import qcommands
except StandardError as e:
    mutter("Can't import qbzr so not defining GUI commands:\n"
        "%s" % str(e)
        )
else:
    cmd_qprune = qcommands.cmd_qprune
    cmd_qbranches = qcommands.cmd_qbranches
    cmd_qcoloswitch = qcommands.cmd_qcoloswitch


class NoSavedSyncLocation(errors.BzrCommandError):

    _fmt = ("No synchronization location known or specified.")

class cmd_colo_sync_from(commands.Command):

    """Synchronize this colocated workspace from the state of another one.
    
    LOCATION should be a path or URL to a colocated workspace such that the
    branches it holds are accessible as colo:LOCATION:branch_name.  For every
    branch in that remote workspace, if there is a local branch with the same 
    name, the remote branch is pulled into the corresponding local branch.  
    If there is not a local branch with a name, then a new branch is created
    in the local colocated workspace.

    The first time colo-sync-from is used, it records a default location so 
    that future synchronizations can just use "bzr colo-sync-from".  To change
    the saved synchronization location, use the "--remember" option.

    The "--repository" option can be used to synchronize from a regular bzr
    repository.  Note that with this option LOCATION will not be remembered
    even if "--remember" is also specified.
    """

    takes_args = ['location?']

    takes_options = [option.Option('overwrite',
                                   help='Ignore differences between branches '
                                        'and overwrite unconditionally'),
                     option.Option('repository',
                                   help='The from LOCATION is a regular '
                                        'repository instead of colocated.'),
                    'remember',
                    ]

    def _remote_workspace(self, location):
        if self.repository:
            return RepositoryWorkspace(location)
        else:
            return ColocatedWorkspace(location)

    def run(self, location=None, overwrite=False, remember=False,
            repository=False):
        workspace = ColocatedWorkspace()
        self.repository = repository

        config = workspace.get_config()
        if location is None:
            # no specified location, must successfully get a saved location
            location = config.get_sync_from_location()
            if location is None:
                raise NoSavedSyncLocation
            remote_workspace = self._remote_workspace(location)
        else:
            # location specified
            remote_workspace = self._remote_workspace(location)
            if not repository and (
                remember or config.get_sync_from_location() is None):
                config.set_sync_from_location(remote_workspace.base)

        conflicts = 0
        current = workspace.current_branch_name()
        for name in remote_workspace.branch_names():
            remote_branch = remote_workspace.branch_with_name(name)
            try:
                local_branch = workspace.branch_with_name(name)
            except errors.NotBranchError:
                local_branch = None

            if local_branch is not None:
                trace.note('Updating branch %s from colo:%s:%s.' % (name,
                                                                    location,
                                                                    name))
                result = local_branch.pull(remote_branch, overwrite=overwrite)
                result.report(self.outf)

                if name == current:
                    # update the working tree
                    tree = workingtree.WorkingTree.open_containing(u'.')[0]
                    conflicts = tree.update()
            else:
                trace.note('Creating new branch %s from colo:%s:%s.' %
                           (name, location, name))
                branch_cmd = _wrap_command_object(builtins.cmd_branch(),
                                                  self.outf)
                branch_cmd.run(remote_branch.base,
                    to_location=workspace.url_for_name(name), no_tree=True)

        if conflicts > 0:
            return 1
        else:
            return 0


class cmd_colo_sync_to(commands.Command):

    """Synchronize this colocated workspace to another one.
    
    LOCATION should be a path or URL for a colocated workspace.  The branches
    in the current workspace are pushed to the specified remote workspace.
    If that path does not already contain matching branches, they will be
    created.

    The first time colo-sync-to is used, it records a default location so
    that future synchronizations can just use "bzr colo-sync-to".  To change
    the saved synchronization location, use the "--remember" option.

    The "--repository" option can be used to synchronize to a regular bzr
    repository.  Note that with this option LOCATION will not be remembered
    even if "--remember" is also specified.
    """

    takes_args = ['location?']

    takes_options = [option.Option('overwrite',
                                   help='Ignore differences between branches '
                                        'and overwrite unconditionally.'),
                     option.Option('repository',
                                   help='The to LOCATION is a regular '
                                        'repository instead of colocated.'),
                     'remember',
                    ]

    def _remote_workspace(self, location):
        if self.repository:
            return RepositoryWorkspace(location)
        else:
            return ColocatedWorkspace(location)

    def run(self, location=None, overwrite=False, remember=False,
            repository=False):
        workspace = ColocatedWorkspace()
        self.repository = repository

        config = workspace.get_config()
        if location is None:
            # no specified location, must successfully get a saved location
            location = config.get_sync_to_location()
            if location is None:
                raise NoSavedSyncLocation
            remote_workspace = self._remote_workspace(location)
        else:
            # location specified
            remote_workspace = self._remote_workspace(location)
            if not repository and (
                remember or config.get_sync_from_location() is None):
                config.set_sync_to_location(remote_workspace.base)

        for name in workspace.branch_names():
            remote_branch_location = remote_workspace.url_for_name(name)
            trace.note('Updating colo:%s:%s from %s.' % (location,
                                                         name,
                                                         name))
            local_branch = workspace.branch_with_name(name)
            bzr_push_cmd = _wrap_command_object(builtins.cmd_push(), 
                                                self.outf)
            bzr_push_cmd.run(
                directory=urlutils.local_path_from_url(local_branch.base),
                location=remote_branch_location,
                overwrite=overwrite,
                create_prefix=True)

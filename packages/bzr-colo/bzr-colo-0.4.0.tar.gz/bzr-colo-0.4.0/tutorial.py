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

_colo_tutorial = \
"""
=========================================
Colocated Branches with the `colo` plugin
=========================================

Basic Concepts
==============

Colocated Workspaces
--------------------

I'll refer to the amalgamation of a working tree and some number of related
branches within that same directory as a colocated workspace.  A colocated
workspace for developing on Bazaar itself would be a single directory named
``bazaar``.  It would consist of a single working tree in the ``bazaar``
directory, and one or more branches stored in a shared repository located at
``bazaar/.bzr/branches``.  This location is inside Bazaar's control directory
``bazaar/.bzr``, but the branches in that directory can still be referred to
just like any Bazaar branches.  The default branch is called ``trunk``.

Referring to Colocated Branches
-------------------------------

This plugin adds a directory service of "colo:" that can be used to
refer to branches inside of the ``.bzr/branches`` directory.  So, for example
we could ``bzr switch colo:fix-eol-bug`` to do work in the colocated
``fix-eol-bug`` branch.  Note that in some cases, the "colo:" prefix is
unnecessary because Bazaar automatically looks for branches in the directory
where the current branch is located.  So the previous command would also work
with ``bzr switch fix-eol-bug`` because switch searches sibling directories 
automatically.

From within a colocated workspace, the specifier ``colo:branch_name`` refers
to the specified branch in the current colocated workspace.  It is possible
to refer to colocated branches in arbitrary workspaces using the syntax 
``colo:workspace_location:branch_name``.  The ``workspace_location`` in this
form can be either a path (e.g. ``colo:../other_project:trunk``) or a URL
(e.g. ``colo:bzr+ssh://hostname/path/to/workspace:trunk``).

Branch names may use the chracter "/" to create hierarchical storage for
branches.  For example, one might store all branches related to bug fixes with
names that start with ``bugs/``.  This corresponds to the actual branches being
stored in a subdirectory of ``.bzr/branches``.

Inspecting Colocated Branches
-----------------------------

Since Bazaar doesn't have a built-in command for listing the branches in a
given repository, this plugin provides the ``colo-branches`` command to list
all of the branches in the ``.bzr/branches`` repository.  This is very similar
to the ``branches`` command provided by the bzrtools__ plugin.  If the current
directory is a checkout of one of the colocated branches, the current
branch is marked with a "*".  If the qbzr__ plugin is installed, then this
plugin also defines a graphical ``qbranches`` command to show all of the 
colocated branches, with the current one marked in bold.

__ http://launchpad.net/bzrtools
__ http://launchpad.net/qbzr

Also, since the ``.bzr/branches`` directory is an ordinary Bazaar shared
repository, tools such as ``bzr qlog`` from the qbzr plugin which are able
to show the log information for all of the branches found in a repository
can be easily used.  Just do ``bzr qlog colo:`` to see all of the
history for all of the branches in this colocated workspace.  Individual
branches can be logged simply by using the "colo:" specifier: ``bzr log
colo:trunk``.

To allow branches to be hidden from the listing, branches whose name starts
with a period are not shown in the listing.  To show them, use the ``--all``
option (the current branch is always shown).  This also allows multiple
branches to be hidden under a directory named, for example, ".hidden"::

    $ bzr colo-mv bug1 .hidden/bug1
    $ bzr colo-mv bug2 .hidden/bug2
    $ bzr colo-branches
    ... no bug1 and bug2 ...

Branches are also hidden if they have the option "bzr.branch.status" set to
"Hidden", "Merged" or "Abandoned".


Creating a Colocated Workspace
------------------------------

This plugin provides a ``colo-init`` command which creates a new colocated
workspace with a single working tree that is a checkout of a single branch
called "trunk".  This can then be the starting point for either a new project,
or for pulling in the sources of an existing project.  Within this directory,
"colo:" branch names can be used as the targets of commands such as ``bzr
branch`` and ``bzr pull`` in the process of building up a colocated workspace
from existing branches.

The colo-init command has an option ``--no-tree`` that creates colocated
workspaces with no working tree.  In this case, there will just be a
collection of branches in a shared repository at ``.bzr/branches``.  This can
be useful for workspaces created remotely where it isn't possible to make a
working tree and for any time where the working files aren't needed.

This plugin also offers a ``colo-ify`` command to convert an existing branch
into a colocated workspace.  That command can also take additional branch
arguments to add to the workspace.  For example, consider a situation where we
have branches in separate directories ``master/`` and ``fix-eol-bug/``.  Then,
the following commands would convert the master branch into a colocated
workspace with two branches inside::

    $ cd master
    $ bzr colo-ify ../fix-eol-bug 
    $ bzr colo-branches
      fix-eol-bug
    * trunk

Making Another Colocated Branch
-------------------------------

In the colocated workflow, a common operation is to create a new branch and
then switch the working tree to that new branch.  Using standard Bazaar
commands in a colocated workspace, this is a two step process::

    $ bzr branch . colo:new-branch
    $ bzr switch colo:new-branch

Since this is such a common process in the colocated workflow, this plugin
provides a command ``colo-branch`` that simplifies this process, condensing
the two commands above to::

    $ bzr colo-branch new-branch

Note that by default colo-branch branches from the current branch, so one
should be careful that the current branch is the correct one, or use the
``--from-branch`` option to specify the name of a source branch.  (Often ``bzr
branch --from-branch=trunk new_branch`` is the correct thing to do.)
The nick of the branch is set to the name of the branch.


Making a New Working Tree from a Workspace
------------------------------------------

Sometimes it is nice to be able to make a second working tree for the same
colocated workspace, for example to work on a second bug fix in parallel.
This plugin provides the ``colo-checkout`` command which creates a second
checkout of the current branch in the specified directory.  Often, the
specified directory will be a sibling of the current workspace.  For example::

    $ bzr colo-branches
      fix-eol-bug
    * trunk
    $ bzr colo-branch fix-unicode-normalization # creates a colocated branch
    $ bzr colo-checkout ../fix-unicode-normalization
    $ cd ../fix-unicode-normalization
    $ bzr colo-branches
      fix-eol-bug
    * fix-unicode-normalization
      trunk

Note that while the new checkout isn't a full colocated workspace (it doesn't
contain branches inside ``.bzr/branches``), it is still possible to use the
"colo:" directory specifier to refer to other branches in the original
colocated workspace.  For example, to see the effect of the unicode
normalization fixes, one could do::

    $ bzr diff --old=colo:trunk

Since creating a new colocated branch for work in a new checkout is a common
operation, the ``colo-checkout`` command takes a ``--create`` option
to indicate that a new colocated branch should be created and then the new
checkout should be switched to that new branch.  The name of the new branch
comes from the basename of the directory that is being created.
For example, we could shorten the above example as::

    $ bzr colo-checkout --create ../fix-unicode-normalization

As an additional simplification, the ``colo-checkout`` command also takes a
``--from-branch`` option to simplify the process of making additional
checkouts from branches other than the current branch.  Following the above
example, if we wanted to create the fix-unicode-normalization branch off of
the fix-eol-bug branch, we could do::

    $ bzr colo-checkout --create --from-branch=fix-eol-bug ../fix-unicode-normalization

Fetching an Existing Project
----------------------------

This plugin provides a ``colo-fetch`` command for getting an existing branch
into a new colocated workspace.  This can typically be used as the first step
in starting to do work on an existing project.  For example, to begin work on
developing Bazaar, one could do::
 
  $ bzr colo-fetch lp:bzr ~/src/bzr
  $ cd ~/src/bzr
  $ bzr colo-branches
  * origin/trunk

The ``colo-fetch`` command creates a single colocated branch named
"origin/trunk" by default.  If a different name is wanted, then the
``--trunk-name`` option can be specified.

To add additional branches to the colocated workspace, use the ordinary
``branch`` command and specify a branch name using the "colo:" specifier.  To
add Bazaar's stable 2.0 branch to the above colocated workspace would be::
  
  $ cd ~/src/bzr
  $ bzr branch lp:bzr/2.0 colo:origin/2.0
  $ bzr colo-branches
    origin/2.0
  * origin/trunk

This will reuse the existing revisions from the trunk branch and should
provide for a very quick download.  Branches whose name start with "origin/"
have a special meaning to the ``colo-pull`` command.

Updating Multiple Branches
--------------------------

This plugin provides a ``colo-pull`` command for updating all of the remote
branches that are mirrored in this workspace.  Since it often isn't desired to
pull every single branch from its parent, this plugin uses a simple convention
for indicating which branches should be updated by ``colo-pull``: all branches
whose name begins with "origin/" will be pulled from their parent locations.
By default, the ``colo-fetch`` command uses "origin/trunk" for the name of its
initial branch, indicating that it should be updated by ``colo-pull``.
Merging the "origin/" branches into the other local branches that have been
made from them must be done manually.

Using the colocated workspace set up in the previous section for Bazaar 
development using two branches, the colo-pull command would show the
following::

    $ bzr colo-pull
    Updating origin/2.0 from bzr+ssh://bazaar.launchpad.net/~bzr-pqm/bzr/2.0/
    Now on revision ...
    Updating origin/trunk from bzr+ssh://bazaar.launchpad.net/~bzr-pqm/bzr/bzr.dev/
    Now on revision ...

Renaming a Colocated Branch
---------------------------

Since colocated branches exist inside Bazaar's hidden control directory, it
can be inconvenient to move those branches using ordinary filesystem tools.
This plugin provides a ``colo-mv`` command to rename colocated branches. 
This command simply moves the branch on disk.  As a result, relationships 
between the moved branch and other checkouts or between the moved branch and 
other branches may be severed.  These relationships must be manually restored
after moving a branch, so use this command with caution.

An important use of this command is to designate a branch as remote by giving
it a name that starts with "origin/".  If the "trunk" branch should now be a
mirror of a remote branch, say on Launchpad at lp:project, then the following
would make that connection::

    $ bzr colo-branches
    ...
    * trunk
    $ bzr pull --remember lp:project
    $ bzr colo-mv trunk origin/trunk
    $ bzr colo-branches
    ...
    * origin/trunk
    $ bzr colo-pull
    Updating origin/trunk from bzr+ssh://bazaar.launchpad.net/~project/trunk
    No revisions to pull.

Synchronizing Colocated Workspaces
----------------------------------

For purposes of backup or moving work from one computer to another, one may
want to synchronize all of the branches in one colocated workspace with all
of the branches in another colocated workspace.  This plugin provides the
``colo-sync-to`` and ``colo-sync-from`` commands for this purpose.  These
commands take the location of another colocated workspace as an argument and
perform the synchronization in the specified direction using Bazaar's native
push and pull facilities.

For example, consider the case of synchronizing work on the local machine with
a corresponding workspace on a USB key at ``/mnt/usb_key``.  At the end of a
workday, one would want to update the workspace on the USB key to match that
of the local workspace::

    $ bzr colo-init /mnt/usb_key/bzr   # only necessary once
    $ cd ~/src/bzr
    $ bzr colo-sync-to /mnt/usb_key/bzr
    Updating colo:/mnt/usb_key/bzr:trunk from trunk
    ...

Then, if one did some work using their USB key overnight, then in the morning
they could sync from there to their local workspace::

    $ cd ~/src/bzr
    $ bzr colo-sync-from /mnt/usb_key/bzr
    Updating trunk from colo:/mnt/usb_key/bzr:trunk

Note that the colo-sync-from and colo-sync-to commands are symmetric in the
sense that both of them will update all of the branches that exist in the
*source* workspace.  This means that newly created branches in the local
workspace will also be created in the remote workspace upon ``colo-sync-to``
and newly created remote branches will be created in the local workspace when
using ``colo-sync-from``.  Neither of these commands will delete any branches,
but branches can be deleted in any workspace with ``colo-prune``.

For remote workspaces accessed over a network, Bazaar may refuse to create
working trees, but these workspaces can still be used for synchronization by
creating them with ``colo-init --no-tree``.  For example::

    $ bzr colo-init --no-tree bzr+ssh://hostname/path/to/backup
    $ bzr colo-sync-to bzr+ssh://hostname/path/to/backup

The ``colo-sync-to`` and ``colo-sync-from`` commands each save a default
location the first time they are used.  To synchronize somewhere other than
the default location, simply specify that location in the command, as 
was done on the first invocation.  To change the default location,
give the ``--remember`` option when specifying a new location.  Even if
you want to synchronize from and to the same workspace, you have to 
specify that location once to both ``colo-sync-from`` and ``colo-sync-to``:
the commands don't make use of each other's defaults.

For synchronizing to and from locations that are not colocated workspaces, 
there is a ``--repository`` option, which allows synchronization with ordinary
Bazaar repositories that contain branches in subdirectories.  For example, if
there is a repository at server.example.com:/bzr/project with branches at
/bzr/project/trunk and /bzr/project/feature, then::

    $ bzr colo-init
    $ bzr colo-sync-from --repository bzr+ssh://server.example.com/bzr
    $ bzr colo-branches
      feature
    * trunk


Removing a Colocated Branch
---------------------------

Because colocated branches are stored in a relatively hidden directory, this
plugin provides a ``colo-prune`` command for removing a colocated branch.
It is equivalent to removing the branch's directory on the filesystem.  If 
the qbzr plugin is installed, then there is a graphical equivalent command
called ``qprune``.

To remove the revisions that were only present in the pruned branches, the
``--clean`` option can be specified.  This may be a long-running operation
if the history of the project is large.  In the case where one or more
``colo-prune`` operations has already happened, there is a ``colo-clean``
command that will remove all of the unused revisions.

Moving Colocated Workspaces on Disk
-----------------------------------

Because Bazaar uses absolute path names to record the connection between a
working tree and a branch, when colocated workspaces are moved around on the
filesystem, the connection between the working tree and the current branch is
broken.  To fix this, run ``bzr colo-fixup`` from within the working tree.  If
this doesn't work for some reason, then one can always run the command ``bzr
switch --force .bzr/branches/<current branch>``, provided one knows what the
current branch should be.


Example Usages
==============

Develop an existing project in a colocated workspace
----------------------------------------------------

We want to develop a GUI feature on the Bazaar project, using colocated
branches.

::

    $ bzr colo-fetch lp:bzr bzr
    $ cd bzr
    $ bzr colo-branches
    * origin/trunk
    $ bzr colo-branch feature-gui
    # make changes
    $ bzr ci -m 'add the new feature'
    ...
    $ bzr missing colo:origin/trunk
    You have 1 extra revision(s):
    ------------------------------------------------------------
    revno:...
    ...
    # submit the change, in this case using a merge directive
    $ bzr send colo:origin/trunk

Starting a new project using a colocated workspace
--------------------------------------------------

We want to start a new project and be ready to use colocated branches going
forward with the development.

::

    $ bzr colo-init newproj
    Shared repository (format: 2a)
    Location:
      shared repository: newproj/.bzr/branches
    Created a repository branch (format: 2a)
    Using shared repository: /tmp/newproj/.bzr/branches/
    $ cd newproj
    $ echo "I'm new!" > README.txt
    $ bzr add
    adding README.txt
    $ bzr ci -m 'first revision'
    Committing to: /tmp/newproj/.bzr/branches/trunk/
    added README.txt
    Committed revision 1.
    $ bzr log colo:trunk
    ------------------------------------------------------------
    revno: 1
    committer: ...
    branch nick: trunk
    timestamp: ...
    message:
      first revision!
    
Converting an existing project to a colocated workspace
-------------------------------------------------------

We want to take an existing project with a trunk and numerous bug fix branches
and convert it into a single colocated workspace.  Assume that we have the main
branch in the ``master/`` directory and bug fix branches in directories named
``fix-001/`` and ``fix-002/`.  We can convert the ``master/`` directory to a
colocated workspace using ``colo-ify``::

    $ cd master
    $ bzr colo-ify
    $ bzr colo-branches
    * trunk

If we want to use a different name for the trunk branch, we can use the
``--trunk-name`` option.

If we would now like the bug fix branches also as colocated branches, we can
simply branch them in using standard Bazaar commands::

    $ bzr branch ../fix-001 colo:fix-001
    $ bzr branch ../fix-002 colo:fix-002
    $ bzr colo-branches
      fix-001
      fix-002
    * trunk

We could also have specified the bug fix branches as arguments to the
``colo-ify`` command to specify bringing in those additional branches all at
once, making the preceding commands equivalent to::

    $ bzr colo-ify ../fix-001 ../fix-002

The new branches are created with names derived from their locations ("fix-001"
and "fix-002" in this case, as above).

Using two checkouts with a colocated workspace
----------------------------------------------

One of the advantages of a colocated workspace is having a single directory
which will always contain the active code for a project, for example when
using an IDE or when there are generated files that are expensive to
re-create.  This can be a disadvantage when we want to have two separate
working trees, for example to compare two sets of files or to maintain a
working tree that is up to date with a particular branch.  We can do this
using a colocated workspace and the ``colo-checkout`` command.

For example, when developing a project such as Bazaar, it can be important to
have a pristine copy of the trunk from which to run Bazaar while developing so
that the development work doesn't prevent working with the version control
system.

::

    $ bzr colo-fetch lp:bzr bzr
    $ cd bzr
    $ bzr colo-checkout ../bzr.dev
    $ bzr colo-branch fix-doc-bugs
    $ bzr colo-branches
    * fix-doc-bugs
      origin/trunk
    $ ../bzr.dev/bzr --version  # this runs the trunk version of bzr
    $ ./bzr --version  # this runs the version in the fix-doc-bugs branch

Another use for the ``colo-checkout`` command is to create a second working
tree to do some work without interrupting the work that is happening in the
colocated workspace (although a judicious use of ``bzr shelve`` can sometimes
make this unnecessary).  Here is an example that uses the ``--create`` option
to create a new branch and make a new checkout of it::

    $ bzr colo-branches
    * fix-doc-bugs
      origin/trunk
    $ bzr colo-checkout --create ../urgent-fix
    $ bzr colo-branches
    * fix-doc-bugs
      origin/trunk
      urgent-fix
    $ cd ../urgent-fix
    $ bzr colo-branches
      fix-doc-bugs
      origin/trunk
    * urgent-fix

Note that the original working tree still points at the same branch while only
the new checkout was switched to the newly created branch.


Configuration
=============

This plugin uses some Bazaar options to control its behavior.  These
options can be set using Bazaar's standard configuration mechanism.
See "bzr help configuation" and "bzr help config" for more details.

- bzr.branch.status: if set on a branch to "Hidden", "Merged" or
  "Abandoned" then that branch is not shown in branch listings
- colo.debug: if set to "False" then don't log messages from the plugin
- colo.dir_in_nick: if set to "True" then include the basename of the
  colocated workspace in the branch nick, so a workspace in Bug-1234
  would have a branch nick of "Bug-1234/trunk"


Limitations
===========

1. Colocated workspaces that are moved on disk need to have their checkout
   reconnected to its branch, due to the fact that Bazaar checkouts refer to
   absolute paths.  Do this using::
   
     $ bzr switch --force .bzr/branches/trunk

   from the root directory of the checkout, or try the ``colo-fixup`` command
   which should work in most cases.
"""

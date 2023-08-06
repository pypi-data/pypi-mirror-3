# Copyright 2010 Neil Martinsen-Burrell
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

import os
from bzrlib.lazy_import import lazy_import
lazy_import(globals(), '''
from bzrlib import (bzrdir,
                    option,
           )
''')
from colocated import ColocatedWorkspace
from PyQt4 import QtCore, QtGui

from bzrlib.plugins.qbzr.lib.commands import QBzrCommand
from bzrlib.plugins.qbzr.lib.util import (QBzrWindow,
                                          BTN_CLOSE,
                                          runs_in_loading_queue,
                                         )
from bzrlib.plugins.qbzr.lib.uifactory import ui_current_widget
from bzrlib.plugins.qbzr.lib.switch import QBzrSwitchWindow
from bzrlib.plugins.qbzr.lib.trace import reports_exception
from bzrlib.plugins.qbzr.lib.subprocess import run_subprocess_command


class ColocatedBranchesList(QtGui.QListWidget):

    def __init__(self, workspace, show_all=False):
        super(ColocatedBranchesList, self).__init__()
        self.workspace = workspace
        self.show_all = show_all
        self.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.branch_icon = QtGui.QIcon(
            os.path.join(os.path.dirname(__file__), 'folder.png'))

    def refresh_branches(self):
        self.clear()
        current_name = self.workspace.current_branch_name()
        for name in reversed(sorted(list(self.workspace.branch_names(self.show_all)))):
            item = QtGui.QListWidgetItem(name)
            item.setIcon(self.branch_icon)
            item.setToolTip(self.workspace.branch_with_name(name).base)
            if name == current_name:
                bold = QtGui.QFont(); bold.setWeight(QtGui.QFont.Bold)
                item.setFont(bold)
            self.insertItem(-1, item)


class ColocatedBranchesWindow(QBzrWindow):

    def __init__(self, title=None, parent=None, ui_mode=True,
                       show_all=False):
        super(ColocatedBranchesWindow, self).__init__(title=title,
                                                      parent=parent,
                                                      ui_mode=ui_mode)
        self.workspace = ColocatedWorkspace()
        self.branches_list = ColocatedBranchesList(self.workspace,
                                                   show_all=show_all)
        self.show_all_knob = QtGui.QCheckBox("Show all")
        state = QtCore.Qt.Unchecked
        if show_all:
            state = QtCore.Qt.Checked
        self.show_all_knob.setCheckState(state)
        QtCore.QObject.connect(self.show_all_knob,
                               QtCore.SIGNAL("stateChanged(int)"),
                               self.show_all_clicked)

    def show(self):
        QBzrWindow.show(self)
        QtCore.QTimer.singleShot(1, self.initial_load)

    @runs_in_loading_queue
    @ui_current_widget
    @reports_exception()
    def initial_load(self):
        self.branches_list.refresh_branches()

    def show_all_clicked(self, newstate):
        show_all = bool(newstate)
        self.branches_list.show_all = show_all
        QtCore.QTimer.singleShot(1, self.initial_load)


class PruneWindow(ColocatedBranchesWindow):
    
    def __init__(self, title=None, **kwargs):
        super(PruneWindow, self).__init__(title=None, **kwargs)
        if title is None:
            self.set_title(("Delete Colocated Branches", os.getcwdu()))  
        
        self.restoreSize("prune", (340, 220))

        self.layout = QtGui.QVBoxLayout(self.centralwidget)

        hbox = QtGui.QHBoxLayout()
        self.layout.addLayout(hbox)
        hbox.addWidget(self.branches_list)

        actions_box = QtGui.QVBoxLayout()
        hbox.addLayout(actions_box)
        prune_button = QtGui.QPushButton('Delete')
        actions_box.addWidget(prune_button, 0, QtCore.Qt.AlignTop)
        refresh_button = QtGui.QPushButton('Refresh')
        actions_box.addWidget(refresh_button, 1, QtCore.Qt.AlignTop)
        
        buttonbox = self.create_button_box(BTN_CLOSE)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.show_all_knob, 1)
        hbox.addWidget(buttonbox)
        self.layout.addLayout(hbox)

        QtCore.QObject.connect(refresh_button, 
                               QtCore.SIGNAL("clicked(bool)"),
                               self.branches_list.refresh_branches)
        QtCore.QObject.connect(prune_button,
                               QtCore.SIGNAL("clicked(bool)"),
                               self.do_prune)
        
    def do_prune(self):
        for item in self.branches_list.selectedItems():
            branch_name = item.text()
            if branch_name == self.workspace.current_branch_name():
                self._warn_no_delete_current()
                continue
            run_subprocess_command('colo-prune %s' % branch_name)
        self.branches_list.refresh_branches()

    def _warn_no_delete_current(self):
        msg_box = QtGui.QMessageBox(
            QtGui.QMessageBox.Warning,
            'Warning',
            'Not deleting current branch: %s' %
            self.workspace.current_branch_name(),
            QtGui.QMessageBox.Ok,
            self)
        msg_box.exec_()


class cmd_qprune(QBzrCommand):

    """Remove colocated branches."""

    takes_options = [option.Option('directory', short_name='d',
                                   type=unicode,
                                   help='location of colocated workspace'),
                     option.Option('all', 
                                   help="Show all branches, even hidden ones"),
                    ]

    def _qbzr_run(self, directory=None, all=False):
        if directory is not None:
            os.chdir(directory)
        self.main_window = PruneWindow(show_all=all)
        self.main_window.show()
        self._application.exec_()


class BranchesWindow(ColocatedBranchesWindow):

    def __init__(self, title=None, **kwargs):
                       
        super(BranchesWindow, self).__init__(title=title, **kwargs)
        if title is None:
            self.set_title(('Colocated Branches', os.getcwdu()))

        self.restoreSize("branches", (340, 220))
        
        self.layout = QtGui.QVBoxLayout(self.centralwidget)
        self.layout.addWidget(self.branches_list)
        buttonbox = self.create_button_box(BTN_CLOSE)
        refresh_button = buttonbox.addButton('Refresh',
                                             QtGui.QDialogButtonBox.ActionRole)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.show_all_knob, 1)
        hbox.addWidget(buttonbox)
        self.layout.addLayout(hbox)

        QtCore.QObject.connect(refresh_button,
                               QtCore.SIGNAL('clicked(bool)'),
                               self.branches_list.refresh_branches
                              )


class cmd_qbranches(QBzrCommand):

    """List colocated branches.
    
    The current branch is marked in bold.  Branches whose names start with a 
    period are not shown unless the "--all" option is given.
    """

    takes_options = [option.Option('directory', short_name='d',
                                   type='unicode',
                                   help='location of colocated workspace'),
                     option.Option('all', 
                                   help="Show all branches, even hidden ones"),
                    ]

    def _qbzr_run(self, directory=None, all=False):
        if directory is not None:
            os.chdir(directory)

        self.main_window = BranchesWindow(show_all=all)
        self.main_window.show()
        self._application.exec_()


class QColoSwitchDialog(QBzrSwitchWindow):

    def __init__(self, show_all=False, parent=None):
        """A window to switch between colocated branches.
        """
        self.workspace = ColocatedWorkspace()
        self.show_all = show_all
        super(QColoSwitchDialog, self).__init__(
            self.workspace.current_branch(),
            bzrdir.BzrDir.open(u'.'),
            location=None)
        self.parent = parent

    @runs_in_loading_queue
    def initial_load(self):
        super(QColoSwitchDialog, self).initial_load()
        self.branch_combo.clear()
        for br in self.workspace.branch_names(self.show_all):
            self.processEvents()
            self.branch_combo.addItem(br)

    def do_start(self):
        branch_name = self.branch_combo.currentText()
        if self.create_branch_box.isChecked():
            self.process_widget.do_start(None, 'switch', '--create-branch',
                                         'colo:%s' % branch_name)
        else:
            self.process_widget.do_start(None, 'switch', 
                                         'colo:%s' % branch_name)


class cmd_qcoloswitch(QBzrCommand):

    """Switch between colocated branches graphically."""

    takes_options = [option.Option('directory', short_name='d',
                                   type='unicode',
                                   help='location of colocated workspace'),
                     option.Option('all', 
                                   help="Show all branches, even hidden ones"),
                    ]

    def _qbzr_run(self, directory=None, all=False):
        if directory is not None:
            os.chdir(directory)

        self.main_window = QColoSwitchDialog(show_all=all)
        self.main_window.show()
        self._application.exec_()

#  config_scripts.py
#  
#  Copyright 2011 Alexey Zotov <alexey.zotov@gmail.com>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

# -*- coding: utf-8 -*-

from PyQt4 import QtCore
from PyQt4 import QtGui

import os

from nwqt4 import logger

from config_scripts_ui import Ui_Form

class ConfigScripts(QtGui.QWidget, Ui_Form):
    def __init__(self, settings, scripts, parent=None):
        super(ConfigScripts, self).__init__(parent)
        self.setupUi(self)

        self.scripts = scripts

        self.otherRadio.setChecked(True)
        
        self.nameRadios = []
        for ind, (name, path) in enumerate(scripts):
            nameRadio = QtGui.QRadioButton(name, self)
            self.nameRadios.append(nameRadio)
            pathLabel = QtGui.QLabel(path)
            self.scriptsContents.layout().insertRow(ind, nameRadio, pathLabel)
            nameRadio.setChecked(path == settings['script/path'])

        if self.otherRadio.isChecked():
            self.otherEdit.setText(settings['script/path'])

        self.otherBrowseButton.clicked.connect(self.browse_clicked)

    def browse_clicked(self):
        self.file_dialog = QtGui.QFileDialog(directory=os.path.dirname(
            unicode(self.otherEdit.text())))
        self.file_dialog.selectFile(unicode(self.otherEdit.text()))
        self.file_dialog.setAcceptMode(QtGui.QFileDialog.AcceptOpen)
        self.file_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        self.file_dialog.accepted.connect(self.file_dialog_accepted)
        self.file_dialog.show()

    def file_dialog_accepted(self):
        self.otherEdit.setText(self.file_dialog.selectedFiles()[0])
        self.otherRadio.setChecked(True)

    def export_settings(self):
        script_path = ''
        
        if self.otherRadio.isChecked():
            script_path = unicode(self.otherEdit.text())
        else:
            for radio, (name, path) in zip(self.nameRadios, self.scripts):
                if not radio.isChecked():
                    continue

                script_path = path
                break

        return {
            'script/path': script_path
        }

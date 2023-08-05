#  choice_duplicate.py
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

import os

from PyQt4.QtCore import Qt
from PyQt4 import QtGui

from choice_duplicate_ui import Ui_Form

class ChoiceDuplicate(QtGui.QWidget, Ui_Form):
    def __init__(self, thumbsdir, potential, parent=None,
            flags=Qt.WindowFlags()):

        super(ChoiceDuplicate, self).__init__(parent, flags)
        self.setupUi(self)

        self.potential = potential
        self.wallpaper1, self.wallpaper2 = potential[:2]

        self.horizontalLayout.setAlignment(
            self.notDuplicatesRadio, Qt.AlignHCenter)

        self.wallpaper1Layout.setAlignment(
            self.wallpaper1SizeLabel, Qt.AlignHCenter)
        self.wallpaper1Layout.setAlignment(
            self.wallpaper1Label, Qt.AlignHCenter)
        self.wallpaper1Layout.setAlignment(
            self.original1Radio, Qt.AlignHCenter)

        self.wallpaper2Layout.setAlignment(
            self.wallpaper2SizeLabel, Qt.AlignHCenter)
        self.wallpaper2Layout.setAlignment(
            self.wallpaper2Label, Qt.AlignHCenter)
        self.wallpaper2Layout.setAlignment(
            self.original2Radio, Qt.AlignHCenter)

        self.wallpaper1SizeLabel.setText(
            _('File size:') + ' ' + self.wallpaper1.split('_')[2])
        self.wallpaper2SizeLabel.setText(
            _('File size:') + ' ' + self.wallpaper2.split('_')[2])

        self.wallpaper1Label.setText(
            '<img src="%s">' % os.path.join(thumbsdir, self.wallpaper1))
        self.wallpaper2Label.setText(
            '<img src="%s">' % os.path.join(thumbsdir, self.wallpaper2))

    def get_status(self):
        if self.notDuplicatesRadio.isChecked():
            return self.potential + (0, )
        if self.original1Radio.isChecked():
            return self.potential + (1, )
        if self.original2Radio.isChecked():
            return self.potential + (2, )

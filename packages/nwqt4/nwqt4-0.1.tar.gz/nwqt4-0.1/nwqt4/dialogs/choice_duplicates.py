#  choice_duplicates.py
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

from PyQt4.QtCore import Qt
from PyQt4 import QtGui

from dialog_ui import Ui_Dialog

from nwqt4 import widgets

class ChoiceDuplicates(QtGui.QDialog, Ui_Dialog):
    def __init__(self, thumbsdir, values, parent=None, flags=Qt.WindowFlags()):
        super(ChoiceDuplicates, self).__init__(parent, flags)
        self.setupUi(self)

        self.setWindowTitle(_('Choice duplicates'))

        self.choices = []
        for pair in values['duplicates']:
            choice_duplicate = widgets.ChoiceDuplicate(thumbsdir, pair)
            self.choices.append(choice_duplicate)
            self.verticalLayout.insertWidget(0, choice_duplicate)
    
    def get_choices(self):
        return [choice.get_status() for choice in self.choices]

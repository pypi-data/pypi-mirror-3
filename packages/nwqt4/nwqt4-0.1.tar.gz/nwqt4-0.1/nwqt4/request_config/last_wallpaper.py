#       last_wallpaper.py
#       
#       Copyright 2010 Alexey Zotov <alexey.zotov@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

# -*- coding: utf-8 -*-

from PyQt4.QtCore import Qt
from PyQt4 import QtGui

from nwqt4 import logger

from last_wallpaper_ui import Ui_Form

class LastWallpaper(QtGui.QWidget, Ui_Form):
    def __init__(self, values, parent=None, flags=Qt.WindowFlags()):
        super(LastWallpaper, self).__init__(parent, flags)
        self.setupUi(self)
        
        self.countSlider.setValue(values['count'])
        self.actionCheck.setChecked(values['set_wallpaper'])
        self.actionCheck.setDisabled(values['count'] > 1)
        
        self.countSlider.valueChanged.connect(self.set_action_state)
    
    @logger.log_exc
    def set_action_state(self, value):
        if value > 1:
            self.actionCheck.setChecked(False)
            self.actionCheck.setDisabled(True)
        else:
            self.actionCheck.setDisabled(False)
    
    def export_values(self):
        values = {}
        values['count'] = self.countSlider.value()
        values['set_wallpaper'] = self.actionCheck.isChecked()
        return values

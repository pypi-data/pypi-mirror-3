#       random_wallpaper.py
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

from random_wallpaper_ui import Ui_Form
from nwqt4 import validators

class RandomWallpaper(QtGui.QWidget, Ui_Form):
    def __init__(self, values, parent=None, flags=Qt.WindowFlags()):
        super(RandomWallpaper, self).__init__(parent, flags)
        self.setupUi(self)
        
        self.countSlider.setValue(values['count'])
        self.resolutionsEdit.setText(values['resolutions'])
        self.tagsEdit.setText(values['tags'])
        self.notagsEdit.setText(values['notags'])
        self.useronlyCheck.setChecked(not values['anonymous'] \
            and values['useronly'])
        self.useronlyCheck.setDisabled(values['anonymous'])
        self.actionCheck.setChecked(values['set_wallpaper'])
        self.actionCheck.setDisabled(values['count'] > 1)
        
        self.resolutionsEdit.setValidator(validators.ResolutionsValidator(5))
        self.tagsEdit.setValidator(validators.TagsValidator(5))
        self.notagsEdit.setValidator(validators.TagsValidator(5))
        
        self.countSlider.valueChanged.connect(self.set_action_state)
    
    @logger.log_exc
    def set_action_state(self, value):
        if value > 1:
            self.actionCheck.setChecked(False)
            self.actionCheck.setDisabled(True)
        else:
            self.actionCheck.setDisabled(False)

    @logger.log_exc
    def auth_changed(self, anonymous):
        if anonymous:
            self.useronlyCheck.setChecked(False)
        self.useronlyCheck.setDisabled(anonymous)
    
    def is_valid(self):
        if not validators.validate_widget(self.resolutionsEdit):
            return False
        if not validators.validate_widget(self.tagsEdit):
            return False
        if not validators.validate_widget(self.notagsEdit):
            return False       
        return True
    
    def export_values(self):
        values = {}
        values['count'] = self.countSlider.value()
        values['resolutions'] = unicode(self.resolutionsEdit.text())
        values['tags'] = unicode(self.tagsEdit.text())
        values['notags'] = unicode(self.notagsEdit.text())
        values['useronly'] = self.useronlyCheck.isChecked()
        values['set_wallpaper'] = self.actionCheck.isChecked()
        return values

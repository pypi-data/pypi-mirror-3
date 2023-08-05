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
        
        self.numberSlider.setValue(values['number'])
        if values['reslist'] == 'minmax':
            self.resMinMaxRadioButton.setChecked(True)
        self.resolutionsEdit.setText(values['resolutions'])
        self.tagsEdit.setText(values['tags'])
        self.notagsEdit.setText(values['notags'])
        self.useronlyCheck.setChecked(not values['anonymous'] \
            and values['useronly'])
        self.useronlyCheck.setDisabled(values['anonymous'])
        self.actionCheck.setChecked(values['set_wallpaper'])
        self.actionCheck.setDisabled(values['number'] > 1)

        if values['reslist'] == 'minmax':
            self.resolutionsLabel.setText(_('Comma separated min and/or max resolutions,\n'
                'e.g. 1024x768,1280x1024 or 1024x768 or ,1280x768'))
        
        if values['reslist'] == 'minmax':
            self.resolutionsEdit.setValidator(validators.ResMinMaxValidator())
        else:
            self.resolutionsEdit.setValidator(validators.ResolutionsValidator(5))
        self.tagsEdit.setValidator(validators.TagsValidator(5))
        self.notagsEdit.setValidator(validators.TagsValidator(5))
        
        self.numberSlider.valueChanged.connect(self.set_action_state)
        self.resListRadioButton.toggled.connect(self.res_list_toggled)
        self.resMinMaxRadioButton.toggled.connect(self.res_minmax_toggled)
    
    @logger.log_exc
    def set_action_state(self, value):
        if value > 1:
            self.actionCheck.setChecked(False)
            self.actionCheck.setDisabled(True)
        else:
            self.actionCheck.setDisabled(False)

    @logger.log_exc
    def res_list_toggled(self, value):
        if not value:
            return

        self.resolutionsLabel.setText(_('Comma separated list of resolutions (max 5), in preferred order,\n'
            'e.g. 1024x768, 1280x1024:'))
        self.resolutionsEdit.setValidator(validators.ResolutionsValidator(5))

    @logger.log_exc
    def res_minmax_toggled(self, value):
        if not value:
            return

        self.resolutionsLabel.setText(_('Comma separated min and/or max resolutions,\n'
                'e.g. 1024x768,1280x1024 or 1024x768 or ,1280x768'))
        self.resolutionsEdit.setValidator(validators.ResMinMaxValidator())

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
        values['number'] = self.numberSlider.value()
        values['resolutions'] = unicode(self.resolutionsEdit.text())
        values['reslist'] = 'minmax' if self.resMinMaxRadioButton.isChecked() else ''
        values['tags'] = unicode(self.tagsEdit.text())
        values['notags'] = unicode(self.notagsEdit.text())
        values['useronly'] = self.useronlyCheck.isChecked()
        values['set_wallpaper'] = self.actionCheck.isChecked()
        return values

#       config_icon.py
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

from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui

from nwqt4 import logger

from config_icon_ui import Ui_Form

class ConfigIcon(QtGui.QWidget, Ui_Form):
    def __init__(self, settings, parent=None, flags=Qt.WindowFlags()):
        super(ConfigIcon, self).__init__(parent, flags)
        self.setupUi(self)

        self.set_up_action_map()

        if settings['icon/action'] in self.action_map:
            self.action_map[settings['icon/action']].setChecked(True)
        else:
            self.doNothingRadio.setChecked(True)

    def set_up_action_map(self):
        self.action_map = {
            'do_nothing': self.doNothingRadio,
            'request_random_wallpaper': self.requestRandomWallpaperRadio,
            'request_last_wallpaper': self.requestLastWallpaperRadio,
            'request_new_wallpaper': self.requestNewWallpaperRadio,
            'add_url': self.addUrlRadio,
            'force_scheduled_request': self.forceScheduledRequestRadio
        }

    @logger.log_exc
    def auth_changed(self, anonymous):
        self.requestLastWallpaperRadio.setDisabled(anonymous)
        self.requestNewWallpaperRadio.setDisabled(anonymous)
        self.addUrlRadio.setDisabled(anonymous)
        if anonymous and (
            self.requestLastWallpaperRadio.isChecked() or \
            self.requestNewWallpaperRadio.isChecked() or \
            self.addUrlRadio.isChecked()
        ):
            self.doNothingRadio.setChecked(True)
    
    def get_action(self):
        for action, radio_button in self.action_map.iteritems():
            if radio_button.isChecked():
                return action
    
    def export_settings(self):
        return {
            'icon/action': self.get_action()
        }

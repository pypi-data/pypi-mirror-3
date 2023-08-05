#       config_requests.py
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

from config_requests_ui import Ui_Form

from nwqt4 import request_config

class ConfigRequests(QtGui.QWidget, Ui_Form):
    def __init__(self, settings, parent=None, flags=Qt.WindowFlags()):
        QtGui.QWidget.__init__(self)
        super(ConfigRequests, self).__init__(parent, flags)
        self.setupUi(self)

        self.randomWallpaperAskCheck.setChecked(
            settings['random_wallpaper/ask_settings'])
        self.randomWallpaperAskCheck.toggled.connect(
            self.random_wallpaper_ask_toggled)

        values = {
            'anonymous': settings['auth/anonymous'],
            'count': settings['random_wallpaper/count'],
            'resolutions': settings['random_wallpaper/resolutions'],
            'tags': settings['random_wallpaper/tags'],
            'notags': settings['random_wallpaper/notags'],
            'useronly': settings['random_wallpaper/useronly'],
            'set_wallpaper': settings['random_wallpaper/set_wallpaper']
        }
        self.random_wallpaper_config = request_config.RandomWallpaper(
            values, self)
        self.random_wallpaper_config.setDisabled(
            settings['random_wallpaper/ask_settings'])
        self.randomWallpaperTab.layout().insertWidget(
            1, self.random_wallpaper_config)

        self.lastWallpaperAskCheck.setChecked(
            settings['last_wallpaper/ask_settings'])
        self.lastWallpaperAskCheck.toggled.connect(
            self.last_wallpaper_ask_toggled)

        values = {
            'count': settings['last_wallpaper/count'],
            'set_wallpaper': settings['last_wallpaper/set_wallpaper']
        }
        self.last_wallpaper_config = request_config.LastWallpaper(values, self)
        self.last_wallpaper_config.setDisabled(
            settings['last_wallpaper/ask_settings'])
        self.lastWallpaperTab.layout().insertWidget(
            1, self.last_wallpaper_config)
        self.lastWallpaperTab.setDisabled(settings['auth/anonymous'])

        self.newWallpaperAskCheck.setChecked(
            settings['new_wallpaper/ask_settings'])
        self.newWallpaperAskCheck.toggled.connect(
            self.new_wallpaper_ask_toggled)

        values = {
            'count': settings['new_wallpaper/count'],
            'weight': settings['new_wallpaper/weight'],
            'set_wallpaper': settings['new_wallpaper/set_wallpaper']
        }
        self.new_wallpaper_config = request_config.NewWallpaper(values, self)
        self.new_wallpaper_config.setDisabled(
            settings['new_wallpaper/ask_settings'])
        self.newWallpaperTab.layout().insertWidget(
            1, self.new_wallpaper_config)
        self.newWallpaperTab.setDisabled(settings['auth/anonymous'])

    @logger.log_exc
    def auth_changed(self, anonymous):
        self.random_wallpaper_config.auth_changed(anonymous)
        self.lastWallpaperTab.setDisabled(anonymous)
        self.newWallpaperTab.setDisabled(anonymous)

    @logger.log_exc
    def random_wallpaper_ask_toggled(self, checked):
        self.random_wallpaper_config.setDisabled(checked)

    @logger.log_exc
    def last_wallpaper_ask_toggled(self, checked):
        self.last_wallpaper_config.setDisabled(checked)

    @logger.log_exc
    def new_wallpaper_ask_toggled(self, checked):
        self.new_wallpaper_config.setDisabled(checked)

    def is_valid(self):
        if self.randomWallpaperAskCheck.isChecked():
            if not self.random_wallpaper_config.is_valid():
                self.tabWidget.setCurrentWidget(self.randomWallpaperTab)
        return True
    
    def export_settings(self):
        settings = {
            'random_wallpaper/ask_settings': \
                self.randomWallpaperAskCheck.isChecked(),
            'last_wallpaper/ask_settings': \
                self.lastWallpaperAskCheck.isChecked(),
            'new_wallpaper/ask_settings': \
                self.newWallpaperAskCheck.isChecked()
        }
        
        values = self.random_wallpaper_config.export_values()
        settings['random_wallpaper/count'] = values['count']
        settings['random_wallpaper/resolutions'] = values['resolutions']
        settings['random_wallpaper/tags'] = values['tags']
        settings['random_wallpaper/notags'] = values['notags']
        settings['random_wallpaper/useronly'] = values['useronly']
        settings['random_wallpaper/set_wallpaper'] = values['set_wallpaper']

        values = self.last_wallpaper_config.export_values()
        settings['last_wallpaper/count'] = values['count']
        settings['last_wallpaper/set_wallpaper'] = values['set_wallpaper']

        values = self.new_wallpaper_config.export_values()
        settings['new_wallpaper/count'] = values['count']
        settings['new_wallpaper/weight'] = values['weight']
        settings['new_wallpaper/set_wallpaper'] = values['set_wallpaper']
        
        return settings

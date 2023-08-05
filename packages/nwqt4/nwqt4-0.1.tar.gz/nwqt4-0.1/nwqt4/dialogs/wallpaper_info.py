#  wallpaper_info.py
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

from nwqt4 import logger
from nwqt4 import widgets

from nwqt4.dialogs.wallpaper_info_ui import Ui_Dialog

class WallpaperInfo(QtGui.QDialog, Ui_Dialog):
    def __init__(self, app, result, parent=None, flags=Qt.WindowFlags()):
        super(WallpaperInfo, self).__init__(parent, flags)
        self.setupUi(self)

        self.app = app
        self.result = result

        values = {
            'anonymous': self.app.settings['auth/anonymous']
        }
        values.update(result)

        self.wallpaper_info = widgets.WallpaperInfo(values, self)
        self.verticalLayout.insertWidget(0, self.wallpaper_info)

    @logger.log_exc
    def accept(self):
        if not self.wallpaper_info.is_valid():
            return

        values = self.wallpaper_info.export_values()
        if (values['add_tags'] and values['tags']) or values['add_wallpaper']:
            if values['add_wallpaper'] or self.result['user']:
                self.app.request_add_wallpaper(
                    self.result['name'],
                    values['tags'] if values['add_tags'] else ''
                )
            else:
                self.app.request_add_tags(
                    self.result['name'],
                    values['tags']
                )

        if values['reject_wallpaper']:
            self.app.request_reject_wallpaper(self.result['name'])

        if values['set_wallpaper']:
            self.app.set_wallpaper(self.result)

        if values['send_bad_urls']:
            self.app.request_send_bad_urls(values['bad_urls'])

        super(WallpaperInfo, self).accept()

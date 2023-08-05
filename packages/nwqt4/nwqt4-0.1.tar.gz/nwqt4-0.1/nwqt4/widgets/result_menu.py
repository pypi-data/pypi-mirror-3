#  result_menu.py
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

from PyQt4 import QtGui

import nwqt4

from nwqt4 import logger

class ResultMenu(QtGui.QMenu):
    def __init__(self, app, result, parent=None):
        super(ResultMenu, self).__init__(parent)

        self.app = app
        self.result = result

        anonymous = app.settings['auth/anonymous']
        self.set_wallpaper_action = self.addAction(_('Set wallpaper'))
        self.set_wallpaper_action.triggered.connect(
            self.set_wallpaper_triggered)

        if not anonymous and not self.result['user']:
            self.add_to_my_wallpapers_action = self.addAction(
                _('Add to my wallpapers'))
            self.add_to_my_wallpapers_action.triggered.connect(
                self.add_to_my_wallpapers_triggered)

        if not anonymous and self.result['new']:
            self.reject_wallpaper_action = self.addAction(_('Reject wallpaper'))
            self.reject_wallpaper_action.triggered.connect(
                self.reject_wallpaper_triggered)

        if not anonymous:
            self.add_tags_action = self.addAction(_('Add tags'))
            self.add_tags_action.triggered.connect(self.add_tags_triggered)

    @logger.log_exc
    def set_wallpaper_triggered(self, checked=False):
        self.app.set_wallpaper(self.result)

    @logger.log_exc
    def add_tags_dialog_rejected(self):
        self.add_tags_dialog.deleteLater()

    @logger.log_exc
    def add_to_my_wallpapers_triggered(self, checked=False):
        values = {
            'tags': ', '.join(self.result['tags'])
        }

        self.add_tags_dialog = nwqt4.dialogs.AddTags(values)
        self.add_tags_dialog.accepted.connect(
            self.add_to_my_wallpapers_accepted)
        self.add_tags_dialog.rejected.connect(self.add_tags_dialog_rejected)
        self.add_tags_dialog.show()

    @logger.log_exc
    def add_to_my_wallpapers_accepted(self):
        values = self.add_tags_dialog.export_values()
        self.add_tags_dialog.deleteLater()

        self.app.request_add_wallpaper(self.result['name'], values['tags'])

    @logger.log_exc
    def reject_wallpaper_triggered(self, checked=False):
        self.app.request_reject_wallpaper(self.result['name'])

    @logger.log_exc
    def add_tags_triggered(self, checked=False):
        new_tags = self.result['user'] and [
            tag for tag in self.result['tags']
            if tag not in self.result['user_tags']
        ]
        values = {
            'tags': ', '.join(new_tags) if new_tags else ''
        }

        self.add_tags_dialog = nwqt4.dialogs.AddTags(values)
        self.add_tags_dialog.accepted.connect(self.add_tags_accepted)
        self.add_tags_dialog.rejected.connect(self.add_tags_dialog_rejected)
        self.add_tags_dialog.show()

    @logger.log_exc
    def add_tags_accepted(self):
        values = self.add_tags_dialog.export_values()
        self.add_tags_dialog.deleteLater()

        if not values['tags']:
            return

        self.app.request_add_tags(self.result['name'], values['tags'])

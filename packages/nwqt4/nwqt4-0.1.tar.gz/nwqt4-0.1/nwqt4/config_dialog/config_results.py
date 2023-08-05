#       config_results.py
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

from config_results_ui import Ui_Form

class ConfigResults(QtGui.QWidget, Ui_Form):
    def __init__(self, settings, parent=None, flags=Qt.WindowFlags()):
        super(ConfigResults, self).__init__(parent, flags)
        self.setupUi(self)

        self.userOpacitySpin.setValue(settings['results/user_opacity'])
        self.userColorCheck.setChecked(settings['results/user_frame'])
        self.userColorButton.setColor(
            QtGui.QColor(settings['results/user_color']))

        self.newOpacitySpin.setValue(settings['results/new_opacity'])
        self.newColorCheck.setChecked(settings['results/new_frame'])
        self.newColorButton.setColor(
            QtGui.QColor(settings['results/new_color']))

        self.badUrlsOpacitySpin.setValue(settings['results/bad_urls_opacity'])
        self.badUrlsColorCheck.setChecked(settings['results/bad_urls_frame'])
        self.badUrlsColorButton.setColor(
            QtGui.QColor(settings['results/bad_urls_color']))

        self.cachedOpacitySpin.setValue(settings['results/cached_opacity'])
        self.cachedColorCheck.setChecked(settings['results/cached_frame'])
        self.cachedColorButton.setColor(
            QtGui.QColor(settings['results/cached_color']))
   
    def export_settings(self):
        return {
            'results/user_opacity': self.userOpacitySpin.value(),
            'results/user_frame': self.userColorCheck.isChecked(),
            'results/user_color': self.userColorButton.color().name(),
            'results/new_opacity': self.newOpacitySpin.value(),
            'results/new_frame': self.newColorCheck.isChecked(),
            'results/new_color': self.newColorButton.color().name(),
            'results/bad_urls_opacity': self.badUrlsOpacitySpin.value(),
            'results/bad_urls_frame': self.badUrlsColorCheck.isChecked(),
            'results/bad_urls_color': self.badUrlsColorButton.color().name(),
            'results/cached_opacity': self.cachedOpacitySpin.value(),
            'results/cached_frame': self.cachedColorCheck.isChecked(),
            'results/cached_color': self.cachedColorButton.color().name()
        }

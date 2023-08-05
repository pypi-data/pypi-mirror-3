#       config_duplicates.py
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

import gettext

from config_duplicates_ui import Ui_Form

class ConfigDuplicates(QtGui.QWidget, Ui_Form):
    def __init__(self, settings, parent=None, flags=Qt.WindowFlags()):
        super(ConfigDuplicates, self).__init__(parent, flags)
        self.setupUi(self)

        self.searchDuplicatesCheck.setChecked(
            settings['search_for_duplicates/enabled'])
        self.searchDuplicatesSpin.setValue(
            settings['search_for_duplicates/interval'])
        self.searchDuplicatesSpin.setSuffix(ngettext(
            ' minute',
            ' minutes',
            settings['search_for_duplicates/interval']
        ))
        self.searchDuplicatesSpin.valueChanged.connect(
            self.search_duplicates_spin_changed)

        self.pairsLimitCheck.setChecked(
            settings['search_for_duplicates/limited'])
        self.pairsLimitSpin.setValue(settings['search_for_duplicates/limit'])

        self.meanSpin.setValue(settings['search_for_duplicates/mean'])
        self.stddevSpin.setValue(settings['search_for_duplicates/stddev'])

        self.sendCheck.setChecked(settings['search_for_duplicates/send'])

    def search_duplicates_spin_changed(self, value):
        self.searchDuplicatesSpin.setSuffix(ngettext(
            ' minute',
            ' minutes',
            value
        ))

    def export_settings(self):
        return {
            'search_for_duplicates/enabled': self.searchDuplicatesCheck.isChecked(),
            'search_for_duplicates/interval': self.searchDuplicatesSpin.value(),
            'search_for_duplicates/limited': self.pairsLimitCheck.isChecked(),
            'search_for_duplicates/limit': self.pairsLimitSpin.value(),
            'search_for_duplicates/mean': self.meanSpin.value(),
            'search_for_duplicates/stddev': self.stddevSpin.value(),
            'search_for_duplicates/send': self.sendCheck.isChecked()
        }

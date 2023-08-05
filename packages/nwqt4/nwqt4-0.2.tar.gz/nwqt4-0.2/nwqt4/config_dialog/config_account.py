#       config_auth.py
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

from config_account_ui import Ui_Form

class ConfigAccount(QtGui.QWidget, Ui_Form):
    auth_changed = QtCore.pyqtSignal(bool)
    
    def __init__(self, settings, parent=None, flags=Qt.WindowFlags()):
        super(ConfigAccount, self).__init__(parent, flags)
        self.setupUi(self)
        
        self.anonCheck.toggled.connect(self.anon_check_toggled)
        self.anonCheck.setChecked(settings['auth/anonymous'])
        self.useridEdit.setText(settings['auth/userid'])
        self.passwordEdit.setText(settings['auth/password'])
        self.useSslCheck.setChecked(settings['auth/use_ssl'])
    
    @logger.log_exc
    def anon_check_toggled(self, checked):
        self.useridEdit.setEnabled(not checked)
        self.passwordEdit.setEnabled(not checked)
        self.useSslCheck.setEnabled(not checked)
        self.auth_changed.emit(checked)
    
    def export_settings(self):
        return {
            'auth/anonymous': self.anonCheck.isChecked(),
            'auth/userid': unicode(self.useridEdit.text()).strip(),
            'auth/password': unicode(self.passwordEdit.text()),
            'auth/use_ssl': self.useSslCheck.isChecked()
        }

#       config_dialog.py
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

from config_dialog_ui import Ui_Dialog

from config_scripts import ConfigScripts
from config_account import ConfigAccount
from config_requests import ConfigRequests
from config_schedule import ConfigSchedule
from config_icon import ConfigIcon
from config_results import ConfigResults
from config_duplicates import ConfigDuplicates

class ConfigDialog(QtGui.QDialog, Ui_Dialog):
    def __init__(self, settings, scripts=[], duplicates=True, parent=None,
        flags=Qt.WindowFlags()):

        super(ConfigDialog, self).__init__(parent, flags)
        self.setupUi(self)
        self.duplicates = duplicates

        self.config_scripts = ConfigScripts(settings, scripts, self)
        self.tabWidget.addTab(self.config_scripts, _('Scripts'))

        self.config_account = ConfigAccount(settings, self)
        self.tabWidget.addTab(self.config_account, _('Account'))

        self.config_requests = ConfigRequests(settings, self)
        self.tabWidget.addTab(self.config_requests, _('Requests'))

        self.config_schedule = ConfigSchedule(settings, self)
        self.tabWidget.addTab(self.config_schedule, _('Schedule'))

        self.config_icon = ConfigIcon(settings, self)
        self.tabWidget.addTab(self.config_icon, _('Icon'))

        self.config_results = ConfigResults(settings, self)
        self.tabWidget.addTab(self.config_results, _('Results'))

        if self.duplicates:
            self.config_duplicates = ConfigDuplicates(settings, self)
        else:
            self.config_duplicates = QtGui.QLabel(_(
                'To search for duplicates' \
                ' you need python with sqlite support' \
                ' and python-imaging installed'
            ))
            self.config_duplicates.setAlignment(
                Qt.AlignHCenter | Qt.AlignVCenter)
            self.config_duplicates.setWordWrap(True)
        self.tabWidget.addTab(self.config_duplicates, _('Duplicates'))

        self.config_account.auth_changed.connect(
            self.config_requests.auth_changed)
        self.config_account.auth_changed.connect(
            self.config_schedule.auth_changed)
        self.config_account.auth_changed.connect(
            self.config_icon.auth_changed)

    @logger.log_exc
    def accept(self):
        if not self.config_requests.is_valid():
            self.setCurrentWidget(self.config_requests)
            return

        if not self.config_schedule.is_valid():
            self.setCurrentWidget(self.config_schedule)
            return

        super(ConfigDialog, self).accept()

    def export_settings(self):
        settings = {}
        settings.update(self.config_scripts.export_settings())
        settings.update(self.config_account.export_settings())
        settings.update(self.config_requests.export_settings())
        settings.update(self.config_schedule.export_settings())
        settings.update(self.config_icon.export_settings())
        settings.update(self.config_results.export_settings())
        if self.duplicates:
            settings.update(self.config_duplicates.export_settings())
        return settings

#  send_bad_urls.py
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

from send_bad_urls_ui import Ui_Dialog

class SendBadUrls(QtGui.QDialog, Ui_Dialog):
    def __init__(self, values, parent=None, flags=Qt.WindowFlags()):
        super(SendBadUrls, self).__init__(parent, flags)
        self.setupUi(self)

        self.urlChecks = []
        self.urls = values['urls']

        for url in self.urls:
            urlLabel = QtGui.QLabel('<a href="%s">%s</a>' % (url, url))
            urlLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
            urlLabel.setOpenExternalLinks(True)
            urlCheck = QtGui.QCheckBox()
            urlCheck.setChecked(True)
            self.urlChecks.append(urlCheck)
            self.urlsContents.layout().addRow(urlCheck, urlLabel)

    def export_values(self):
        return {
            'urls': [
                self.urls[ind] for ind, urlCheck
                in enumerate(self.urlChecks) if urlCheck.isChecked()
            ]
        }

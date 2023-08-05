#  add_url.py
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

from nwqt4.dialogs.add_url_ui import Ui_Dialog

from nwqt4 import validators

class AddUrl(QtGui.QDialog, Ui_Dialog):
    def __init__(self, values, parent=None, flags=Qt.WindowFlags()):
        super(AddUrl, self).__init__(parent, flags)
        self.setupUi(self)

        clipboard = QtGui.QApplication.clipboard()
        text = clipboard.text(clipboard.Selection)
        if not text:
            text = clipboard.text(clipboard.Clipboard)
            
        if text and text[:7] == 'http://':
            self.urlEdit.setText(text)
            self.tagsEdit.setFocus()

        self.tagsEdit.setValidator(validators.TagsValidator(5))

        self.sendXmppCheck.setChecked(values['xmpp'])

    @logger.log_exc
    def accept(self):
        if unicode(self.urlEdit.text())[:7] != 'http://':
            return self.urlEdit.setFocus()

        if not validators.validate_widget(self.tagsEdit):
            return

        super(AddUrl, self).accept()

    def export_values(self):
        return {
            'url': unicode(self.urlEdit.text()),
            'tags': unicode(self.tagsEdit.text()),
            'xmpp': self.sendXmppCheck.isChecked()
        }

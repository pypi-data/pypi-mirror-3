#       results.py
#       
#       Copyright 2011 Alexey Zotov <alexey.zotov@gmail.com>
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

from nwqt4 import widgets

from nwqt4.dialogs.results_ui import Ui_Dialog

from wallpaper_info import WallpaperInfo

class Results(QtGui.QDialog, Ui_Dialog):
    def __init__(self, app, params, results, parent=None, flags=Qt.CustomizeWindowHint):
        super(Results, self).__init__(parent, flags)
        self.setupUi(self)

        self.params = params
        
        self.setWindowTitle(params['title'])

        self.closeButton.setIcon(QtGui.QIcon.fromTheme('window-close'))

        self.refreshButton.setIcon(QtGui.QIcon.fromTheme('view-refresh'))
        self.refreshButton.clicked.connect(self.refresh_clicked)

        self.captionLabel.setText('<b>%s</b>' % params['title'])

        results_layout = widgets.ResultsLayout(len(results))
        self.layout().addLayout(results_layout, 1)

        self.result_widgets = []
        for result in results:
            result_widget = widgets.Result(app, result, self)
            self.result_widgets.append(result_widget)
            results_layout.addWidget(result_widget)

    def resizeEvent(self, event):
        super(Results, self).resizeEvent(event)
        
        desktop = QtGui.QApplication.desktop()
        screen_number = desktop.screenNumber(self)
        screen_geometry = desktop.screenGeometry(screen_number)
        self.move(
            screen_geometry.width()/2 - self.width()/2,
            screen_geometry.height()/2 - self.height()/2
        )

    def refresh_clicked(self):
        self.params['method'](*self.params['args'])

    def update_result(self, result):
        for result_widget in self.result_widgets:
            if result_widget.result['name'] != result['name']:
                continue

            result_widget.update_result(result)
            break

#       result_widget.py
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

import os

from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui

import nwqt4

from nwqt4 import common
from nwqt4 import logger

class Result(QtGui.QWidget):
    def __init__(self, app, result, parent=None):
        super(Result, self).__init__(parent)

        self.app = app
        self.result = result
        self.setMinimumSize(170, 100)

        self.busy_timer = None
        self.frames = common.get_animation_frames()

        self.thumb = QtGui.QLabel(parent = self)
        self.resetPalette = self.thumb.palette()
        self.set_appearance()

        layout = QtGui.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.result['thumbpath'] = os.path.join(app.thumbsdir,
            self.result['name'])
        if os.path.isfile(self.result['thumbpath']):
            self.set_up_thumb()
        else:
            self.set_busy(True)
            
            common.download_url(
                self.result['thumb'],
                self.result['thumbpath'],
                self.download_thumb_callback
            )

    def set_busy(self, busy):
        if bool(self.busy_timer) == busy:
            return
            
        if busy:
            self.current_frame = 0
            self.busy_timer = self.startTimer(25)
        else:
            self.killTimer(self.busy_timer)
            self.busy_timer = None

    @logger.log_exc
    def timerEvent(self, event):        
        if event.timerId() == self.busy_timer:
            self.current_frame = (self.current_frame + 1) % 40
            self.update()
        else:
            super(Result, self).timerEvent(event)

    @logger.log_exc
    def paintEvent(self, event):
        super(Result, self).paintEvent(event)

        if not self.busy_timer:
            return

        painter = QtGui.QPainter()
        painter.begin(self)

        frame = self.frames[self.current_frame]

        dx = (self.width() - frame.rect().width()) // 2
        dy = (self.height() - frame.rect().height()) // 2

        painter.drawPixmap(dx, dy, frame)

        painter.end()

    def set_effect(self, setting):
        effect = QtGui.QGraphicsOpacityEffect()
        effect.setOpacity(
            self.app.settings['results/%s_opacity' % setting]/100.0)
        self.thumb.setGraphicsEffect(effect)
        if self.app.settings['results/%s_frame' % setting]:
            palette = QtGui.QPalette(self.thumb.palette())
            palette.setColor(
                QtGui.QPalette.WindowText,
                QtGui.QColor(self.app.settings['results/%s_color' % setting])
            )
            self.thumb.setPalette(palette)

    def set_appearance(self):
        self.thumb.setGraphicsEffect(None)
        self.thumb.setPalette(self.resetPalette)
        
        if not self.result['useronly'] and self.result['user']:
            self.set_effect('user')
        if self.result['new']:
            self.set_effect('new')
        if not self.result['urls']:
            if self.result['cached']:
                self.set_effect('cached')
            else:
                self.set_effect('bad_urls')

    def update_result(self, result):
        if result['name'] != self.result['name']:
            return

        self.result.update(result)
        self.set_appearance()
        self.set_tooltip()

    @logger.log_exc
    def download_thumb_callback(self, filename):
        self.set_busy(False)
        
        if not filename:
            return self.app.notify_error(_('Thumb downloading error'))

        self.set_up_thumb()

    def set_up_thumb(self):
        self.thumb.setMinimumSize(170, 100)
        self.thumb.setText('<img src="%s">' % self.result['thumbpath'])
        self.thumb.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.thumb.setFrameStyle(QtGui.QFrame.Box)
        self.thumb.setCursor(QtGui.QCursor(Qt.PointingHandCursor))
        self.layout().addWidget(self.thumb)
        self.set_tooltip()

    def set_tooltip(self):
        markup = '''
            <table><tr>
                <td>
                    <img width="80" height="45" src="%(thumb)s">
                </td>
                <td>
                    <p><b>%(resolution)s</b></p>
                    <p>%(tags)s</p>
                </td>
            </tr></table>
        '''

        params = {
            'thumb': self.result['thumbpath'],
            'resolution': self.result['name'].split('_')[1],
            'tags': ', '.join(self.result['tags'])
        }
        
        self.setToolTip(markup % params)

    @logger.log_exc
    def showEvent(self, event):
        self.initial_pos = self.pos()

    @logger.log_exc
    def enterEvent(self, event):
        self.resize(180, 110)
        self.move(self.initial_pos - QtCore.QPoint(5, 5))

    @logger.log_exc
    def leaveEvent(self, event):
        self.resize(170, 100)
        self.move(self.initial_pos)

    @logger.log_exc
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.result_dialog = nwqt4.dialogs.WallpaperInfo(
                self.app, self.result)
            self.result_dialog.accepted.connect(self.result_dialog_closed)
            self.result_dialog.rejected.connect(self.result_dialog_closed)
            self.result_dialog.show()
        elif event.button() == Qt.RightButton:
            self.result_menu = nwqt4.widgets.ResultMenu(self.app, self.result)
            self.result_menu.popup(event.globalPos())

    @logger.log_exc
    def result_dialog_closed(self):
        self.result_dialog.deleteLater()

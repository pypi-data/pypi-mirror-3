#       common.py
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

import os

from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from PyQt4 import QtNetwork

from nwqt4 import logger

class UrlDownloader(object):
    def __init__(self, url, filename):
        self.url = QtCore.QUrl(url)
        self.filename = filename

    def download(self, callback):
        try:
            self.file = open(self.filename, 'w')
        except IOError:
            return callback('')
        
        self.callback = callback
        self.reply = nmanager.get(QtNetwork.QNetworkRequest(self.url))
        self.reply.readyRead.connect(self.readyRead)
        self.reply.finished.connect(self.finished)

    @logger.log_exc
    def readyRead(self):
        try:
            self.file.write(str(self.reply.readAll()))
        except IOError:
            self.reply.abort()

    @logger.log_exc
    def finished(self):
        self.file.close()

        del url_downloaders[hash(self)]

        if self.reply.error():
            return self.callback('')

        self.callback(self.filename)

def get_data_file(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)

def get_i18n_dir():
    return get_data_file('i18n')

def get_pixmap(filename):
    return get_data_file(os.path.join('pixmaps', filename))

def get_animation_frames():
    pixmap = QtGui.QPixmap(get_pixmap('animation.svg'))
    
    frames = []
    for angle in xrange(40):
        rotated_pixmap = pixmap.transformed(
            QtGui.QMatrix().rotate(angle * 9),
            Qt.SmoothTransformation
        )
        rect = pixmap.rect()
        rect.moveCenter(rotated_pixmap.rect().center())
        clipped_pixmap = rotated_pixmap.copy(rect)
        frames.append(clipped_pixmap)

    return frames

def download_url(url, filename, callback):
    downloader = UrlDownloader(url, filename)
    url_downloaders[hash(downloader)] = downloader
    downloader.download(callback)

nmanager = QtNetwork.QNetworkAccessManager()
url_downloaders = {}

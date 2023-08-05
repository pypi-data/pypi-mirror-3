#  wallpaper_info.py
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
from nwqt4 import validators

from wallpaper_info_ui import Ui_Form

class WallpaperInfo(QtGui.QWidget, Ui_Form):
    def __init__(self, values, parent=None, flags=Qt.WindowFlags()):
        super(WallpaperInfo, self).__init__(parent, flags)
        self.setupUi(self)

        self.wallpaperNameLabel.setText(values['name'])

        if values['user']:
            self.thumb.setText('<a href="%s"><img src="%s"></a>' % (
                'http://new-wallpaper.org/wallpapers/%s/' % values['name'],
                values['thumbpath']
            ))
        else:
            self.thumb.setText('<img src="%s">' % values['thumbpath'])

        name_parts = values['name'].split('_')
        if values['user']:
            self.resolutionLabel.setText('<b>%s</b> <a href="%s">%s</a>' % (
                _('Resolution:'),
                'http://new-wallpaper.org' \
                    '/wallpapers/resolutions/%s/' % name_parts[1],
                name_parts[1]
            ))
        else:
            self.resolutionLabel.setText('<b>%s</b> %s' % (
                _('Resolution:'),
                name_parts[1]
            ))

        if values['user']:
            self.topTagsLabel.setText('<b>%s</b> %s' % (
                _('Top tags:'),
                ', '.join([
                    '<a href="%s">%s</a>' % (
                        'http://new-wallpaper.org' \
                            '/wallpapers/tags/%s' % tag,
                        Qt.escape(tag)
                    ) for tag in values['user_tags']
                ])
            ))
        else:
            self.topTagsLabel.setText('<b>%s</b> %s' % (
                _('Top tags:'),
                Qt.escape(', '.join(values['tags']))
            ))

        self.sizeLabel.setText('<b>%s</b> %s' % (
            _('Size:'),
            name_parts[2]
        ))

        if values['user']:
            self.myWallpaperUrl.setText(
                '<a href="http://new-wallpaper.org' \
                        '/wallpapers/%s/">%s</a>' % (
                    values['name'],
                    _('Page on new-wallpaper.org')
                )
            )
            self.myWallpaperUrl.setTextInteractionFlags(
                Qt.TextBrowserInteraction)
        else:
            self.myWallpaperUrl.setVisible(False)

        if values['anonymous']:
            self.sendBadUrlsCheck.setEnabled(False)
        else:
            self.sendBadUrlsCheck.toggled.connect(self.send_bad_urls_toggled)

        self.urlChecks = []
        self.urls = values['urls']
        for url in self.urls:
            urlLabel = QtGui.QLabel('<a href="%s">%s</a>' % (url, url))
            urlLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
            urlLabel.setOpenExternalLinks(True)
            urlCheck = QtGui.QCheckBox()
            urlCheck.setEnabled(False)
            self.urlChecks.append(urlCheck)
            self.urlsContents.layout().addRow(urlCheck, urlLabel)

        if values['anonymous']:
            self.addToMyWallpapersCheck.setEnabled(False)
            self.addTagsCheck.setEnabled(False)
            self.addTagsEdit.setEnabled(False)
        else:
            if values['user']:
                self.addToMyWallpapersCheck.setVisible(False)

                new_tags = [
                    tag for tag in values['tags']
                    if tag not in values['user_tags']
                ]
                self.addTagsEdit.setText(', '.join(new_tags[:5]))
            else:
                self.addToMyWallpapersCheck.toggled.connect(
                    self.add_to_my_wallpapers_toggled)
                self.addTagsEdit.setText(', '.join(values['tags'][:5]))

        self.rejectWallpaperCheck.setVisible(values['new'])
        self.rejectWallpaperCheck.toggled.connect(
            self.reject_wallpaper_toggled)

        self.addTagsEdit.setValidator(validators.TagsValidator(5))

    @logger.log_exc
    def send_bad_urls_toggled(self, checked):
        for urlCheck in self.urlChecks:
            urlCheck.setEnabled(checked)

    @logger.log_exc
    def add_to_my_wallpapers_toggled(self, checked):
        if checked:
            self.rejectWallpaperCheck.setChecked(False)

    @logger.log_exc
    def reject_wallpaper_toggled(self, checked):
        if checked:
            self.addToMyWallpapersCheck.setChecked(False)

    def is_valid(self):
        return validators.validate_widget(self.addTagsEdit)

    def export_values(self):
        return {
            'set_wallpaper': self.setWallpaperCheck.isChecked(),
            'add_tags': self.addTagsCheck.isChecked(),
            'tags': unicode(self.addTagsEdit.text()),
            'add_wallpaper': self.addToMyWallpapersCheck.isChecked(),
            'reject_wallpaper': self.rejectWallpaperCheck.isChecked(),
            'send_bad_urls': self.sendBadUrlsCheck.isChecked(),
            'bad_urls': [
                self.urls[ind] for ind, urlCheck
                in enumerate(self.urlChecks) if urlCheck.isChecked()
            ]
        }

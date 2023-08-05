#       config_schedule.py
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

from nwqt4 import logger

from config_schedule_ui import Ui_Form

from nwqt4 import request_config

class ConfigSchedule(QtGui.QWidget, Ui_Form):
    REQUESTS = [
        'random_wallpaper',
        'last_wallpaper',
        'new_wallpaper'
    ]
    
    def __init__(self, settings, parent=None, flags=Qt.WindowFlags()):
        super(ConfigSchedule, self).__init__(parent, flags)
        self.setupUi(self)

        self.scheduleCheck.setChecked(settings['schedule/enabled'])
        self.scheduleSpin.setValue(settings['schedule/schedule'])
        self.scheduleSpin.setSuffix(ngettext(
            ' hour',
            ' hours',
            settings['schedule/schedule']
        ))
        self.scheduleSpin.valueChanged.connect(self.schedule_spin_changed)

        self.set_up_request_combo(settings['auth/anonymous'])

        try:
            request_index = self.REQUESTS.index(settings['schedule/request'])
        except ValueError:
            request_index = 0
        self.requestCombo.setCurrentIndex(request_index)

        values = {
            'anonymous': settings['auth/anonymous'],
            'count': settings['scheduled_random_wallpaper/count'],
            'resolutions': settings['scheduled_random_wallpaper/resolutions'],
            'tags': settings['scheduled_random_wallpaper/tags'],
            'notags': settings['scheduled_random_wallpaper/notags'],
            'useronly': settings['scheduled_random_wallpaper/useronly'],
            'set_wallpaper': \
                settings['scheduled_random_wallpaper/set_wallpaper']
        }
        self.random_wallpaper_config = request_config.RandomWallpaper(
            values, self)
        self.requestRandom.layout().insertWidget(
            0, self.random_wallpaper_config)

        values = {
            'count': settings['scheduled_last_wallpaper/count'],
            'set_wallpaper': settings['scheduled_last_wallpaper/set_wallpaper']
        }
        self.last_wallpaper_config = request_config.LastWallpaper(values, self)
        self.requestLast.layout().insertWidget(0, self.last_wallpaper_config)
        self.requestLast.setDisabled(settings['auth/anonymous'])

        values = {
            'count': settings['scheduled_new_wallpaper/count'],
            'weight': settings['scheduled_new_wallpaper/weight'],
            'set_wallpaper': settings['scheduled_new_wallpaper/set_wallpaper']
        }
        self.new_wallpaper_config = request_config.NewWallpaper(values, self)
        self.requestNew.layout().insertWidget(0, self.new_wallpaper_config)
        self.requestNew.setDisabled(settings['auth/anonymous'])

    def schedule_spin_changed(self, value):
        self.scheduleSpin.setSuffix(ngettext(
            ' hour',
            ' hours',
            value
        ))

    def set_up_request_combo(self, anonymous):
        self.requestCombo.clear()
        if anonymous:
            self.requestCombo.addItems([
                _('Random wallpaper')
            ])
        else:
            self.requestCombo.addItems([
                _('Random wallpaper'),
                _('Last wallpaper'),
                _('New wallpaper')
            ])
    
    @logger.log_exc
    def auth_changed(self, anonymous):
        self.set_up_request_combo(anonymous)
        self.random_wallpaper_config.auth_changed(anonymous)

    def is_valid(self):
        if self.scheduleCheck.isChecked():
            if self.requestCombo.currentIndex() == 0:
                return self.random_wallpaper_config.is_valid()
        return True
    
    def export_settings(self):
        settings = {
            'schedule/enabled': self.scheduleCheck.isChecked(),
            'schedule/schedule': self.scheduleSpin.value(),
            'schedule/request': self.REQUESTS[self.requestCombo.currentIndex()]
        }
        
        values = self.random_wallpaper_config.export_values()
        settings['scheduled_random_wallpaper/count'] = values['count']
        settings['scheduled_random_wallpaper/resolutions'] = \
            values['resolutions']
        settings['scheduled_random_wallpaper/tags'] = values['tags']
        settings['scheduled_random_wallpaper/notags'] = values['notags']
        settings['scheduled_random_wallpaper/useronly'] = values['useronly']
        settings['scheduled_random_wallpaper/set_wallpaper'] = \
            values['set_wallpaper']

        values = self.last_wallpaper_config.export_values()
        settings['scheduled_last_wallpaper/count'] = values['count']
        settings['scheduled_last_wallpaper/set_wallpaper'] = \
            values['set_wallpaper']

        values = self.new_wallpaper_config.export_values()
        settings['scheduled_new_wallpaper/count'] = values['count']
        settings['scheduled_new_wallpaper/weight'] = values['weight']
        settings['scheduled_new_wallpaper/set_wallpaper'] = \
            values['set_wallpaper']
        
        return settings

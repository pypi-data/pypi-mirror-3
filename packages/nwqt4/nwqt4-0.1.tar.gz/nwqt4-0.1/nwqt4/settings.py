#       settings.py
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

class Settings(QtCore.QObject):
    def __init__(self, config):
        super(Settings, self).__init__()

        self.config = config
        self.settings = {}
        self.read_settings()

    def read_settings(self):

        def read_bool(key, default=False):
            self.settings[key] = self.config.read_bool(key, default)

        def read_int(key, default=0):
            self.settings[key] = self.config.read_int(key, default)

        def read_float(key, default=0.0):
            self.settings[key] = self.config.read_float(key, default)

        def read_string(key, default=''):
            self.settings[key] = self.config.read_string(key, default)

        read_string('script/path', '')

        read_bool('auth/anonymous', True)
        read_string('auth/userid')
        read_string('auth/password')
        read_bool('auth/use_ssl')

        read_bool('random_wallpaper/ask_settings', True)
        read_int('random_wallpaper/count', 1)
        read_string('random_wallpaper/resolutions')
        read_string('random_wallpaper/tags')
        read_string('random_wallpaper/notags')
        read_bool('random_wallpaper/useronly')
        read_bool('random_wallpaper/set_wallpaper', True)

        read_bool('last_wallpaper/ask_settings', True)
        read_int('last_wallpaper/count', 1)
        read_bool('last_wallpaper/set_wallpaper', True)

        read_bool('new_wallpaper/ask_settings', True)
        read_int('new_wallpaper/count', 1)
        read_float('new_wallpaper/weight', 1.0)
        read_bool('new_wallpaper/set_wallpaper', True)

        read_bool('schedule/enabled')
        read_int('schedule/schedule', 24)
        read_string('schedule/request', 'random_wallpaper')

        read_int('scheduled_random_wallpaper/count', 1)
        read_string('scheduled_random_wallpaper/resolutions')
        read_string('scheduled_random_wallpaper/tags')
        read_string('scheduled_random_wallpaper/notags')
        read_bool('scheduled_random_wallpaper/useronly')
        read_bool('scheduled_random_wallpaper/set_wallpaper', True)

        read_int('scheduled_last_wallpaper/count', 1)
        read_bool('scheduled_last_wallpaper/set_wallpaper', True)

        read_int('scheduled_new_wallpaper/count', 1)
        read_float('scheduled_new_wallpaper/weight', 1.0)
        read_bool('scheduled_new_wallpaper/set_wallpaper', True)

        read_string('icon/action', 'do_nothing')

        read_int('results/user_opacity', 80)
        read_bool('results/user_frame')
        read_string('results/user_color', '#000000')

        read_int('results/new_opacity', 100)
        read_bool('results/new_frame', True)
        read_string('results/new_color', '#00FF00')

        read_int('results/bad_urls_opacity', 100)
        read_bool('results/bad_urls_frame', True)
        read_string('results/bad_urls_color', '#FF0000')

        read_int('results/cached_opacity', 100)
        read_bool('results/cached_frame', True)
        read_string('results/cached_color', '#FFFF00')

        read_bool('search_for_duplicates/enabled', True)
        read_int('search_for_duplicates/interval', 10)
        read_bool('search_for_duplicates/limited', True)
        read_int('search_for_duplicates/limit', 100)
        read_float('search_for_duplicates/mean', 10.0)
        read_float('search_for_duplicates/stddev', 10.0)
        read_bool('search_for_duplicates/send', True)

    def update(self, settings):
        self.settings.update(settings)

    def save(self):
        for k, v in self.settings.items():
            self.config.write(k, v)
        self.config.sync()

    def __getitem__(self, key):
        return self.settings[key]

    def __setitem__(self, key, value):
        self.settings[key] = value

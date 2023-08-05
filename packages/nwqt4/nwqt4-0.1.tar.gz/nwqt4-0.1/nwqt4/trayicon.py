#       trayicon.py
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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import logger

import common

try:
    import notify
except ImportError:
    NOTIFICATIONS = False
else:
    NOTIFICATIONS = True

class TrayIcon(QtCore.QObject):
    wallpapers_random_triggered = QtCore.pyqtSignal()
    wallpapers_last_triggered = QtCore.pyqtSignal()
    wallpapers_new_triggered = QtCore.pyqtSignal()
    add_url_triggered = QtCore.pyqtSignal()
    force_scheduled_triggered = QtCore.pyqtSignal()
    last_set_wallpaper_triggered = QtCore.pyqtSignal()
    send_bad_urls_triggered = QtCore.pyqtSignal()
    show_duplicates_triggered = QtCore.pyqtSignal()
    settings_triggered = QtCore.pyqtSignal()
    quit_triggered = QtCore.pyqtSignal()
    
    def __init__(self, icon_action, anonymous):
        super(TrayIcon, self).__init__()

        self.icon_action = icon_action
        self.anonymous = anonymous

        self.icon = QtGui.QIcon(common.get_pixmap('new-wallpaper.svg'))
        self.tray_icon = QtGui.QSystemTrayIcon(self.icon)
        self.tray_icon.activated.connect(self.icon_activated)

        self.icon_broken = QtGui.QIcon(common.get_pixmap(
            'new-wallpaper-broken.svg'))
        self.icon_duplicate = QtGui.QIcon(common.get_pixmap(
            'new-wallpaper-duplicate.svg'))

        self.menu = QtGui.QMenu()

        self.requests_menu = QtGui.QMenu(_('Requests'))
        self.menu.addMenu(self.requests_menu)

        self.action_wallpapers_random = QtGui.QAction(
            _('Random wallpaper'), self.requests_menu)
        self.action_wallpapers_random.triggered.connect(
            self.wallpapers_random_triggered.emit)
        self.requests_menu.addAction(self.action_wallpapers_random)

        self.action_wallpapers_last = QtGui.QAction(
            _('Last wallpaper'), self.requests_menu)
        self.action_wallpapers_last.setDisabled(anonymous)
        self.action_wallpapers_last.triggered.connect(
            self.wallpapers_last_triggered.emit)
        self.requests_menu.addAction(self.action_wallpapers_last)

        self.action_wallpapers_new = QtGui.QAction(
            _('New wallpaper'), self.requests_menu)
        self.action_wallpapers_new.setDisabled(anonymous)
        self.action_wallpapers_new.triggered.connect(
            self.wallpapers_new_triggered.emit)
        self.requests_menu.addAction(self.action_wallpapers_new)

        self.action_add_url = QtGui.QAction(_('Add url'), self.menu)
        self.action_add_url.setDisabled(anonymous)
        self.action_add_url.triggered.connect(self.add_url_triggered.emit)
        self.menu.addAction(self.action_add_url)

        self.action_force_scheduled = QtGui.QAction(
            _('Force scheduled request'), self.menu)
        self.action_force_scheduled.setEnabled(False)
        self.action_force_scheduled.triggered.connect(
            self.force_scheduled_triggered.emit)
        self.menu.addAction(self.action_force_scheduled)

        self.action_last_set_wallpaper = QtGui.QAction(
            _('The last set wallpaper'), self.menu)
        self.action_last_set_wallpaper.setEnabled(False)
        self.action_last_set_wallpaper.triggered.connect(
            self.last_set_wallpaper_triggered.emit)
        self.menu.addAction(self.action_last_set_wallpaper)

        self.action_send_bad_urls = QtGui.QAction(
            _('Send bad urls'), self.menu)
        self.action_send_bad_urls.setEnabled(False)
        self.action_send_bad_urls.triggered.connect(
            self.send_bad_urls_triggered.emit)
        self.menu.addAction(self.action_send_bad_urls)

        self.action_show_duplicates = QtGui.QAction(
            _('Show duplicates'), self.menu)
        self.action_show_duplicates.setEnabled(False)
        self.action_show_duplicates.triggered.connect(
            self.show_duplicates_triggered.emit)
        self.menu.addAction(self.action_show_duplicates)

        self.action_settings = QtGui.QAction(_('Settings'), self.menu)
        self.action_settings.triggered.connect(self.settings_triggered.emit)
        self.menu.addAction(self.action_settings)
        
        self.action_quit = QtGui.QAction(_('Quit'), self.menu)
        self.action_quit.triggered.connect(self.quit_triggered.emit)
        self.menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(self.menu)

        self.icon_actions = {
            'request_random_wallpaper': self.action_wallpapers_random,
            'request_last_wallpaper': self.action_wallpapers_last,
            'request_new_wallpaper': self.action_wallpapers_new,
            'add_url': self.action_add_url,
            'force_scheduled_request': self.action_force_scheduled
        }

        self.animation_timer = None
        self.frames = map(QtGui.QIcon, common.get_animation_frames())

        self.icon_state = set()

        self.NOTIFICATIONS = NOTIFICATIONS and notify.init()

        if self.NOTIFICATIONS:
            self.notification = notify.Notification(
                'New Wallpaper', '', 'new-wallpaper')

            self.notification_duplicates = notify.Notification(
                'New Wallpaper', _('Found duplicates'), 'new-wallpaper')
            self.notification_duplicates.set_timeout(notify.EXPIRES_NEVER)
            self.notification_duplicates.add_action('duplicates',
                _('Show duplicates'), self.notification_callback)

            self.notification_bad_urls = notify.Notification(
                'New Wallpaper', _('Found bad urls'), 'new-wallpaper')
            self.notification_bad_urls.set_timeout(notify.EXPIRES_NEVER)
            self.notification_bad_urls.add_action('bad_urls',
                _('Send bad urls'), self.notification_callback)

    def update_icon(self):
        if 'duplicates' in self.icon_state:
            self.tray_icon.setIcon(self.icon_duplicate)
        elif not self.anonymous and 'bad_urls' in self.icon_state:
            self.tray_icon.setIcon(self.icon_broken)
        else:
            self.tray_icon.setIcon(self.icon)

    def start_animation(self):
        if self.animation_timer:
            return

        self.tray_icon.setContextMenu(None)
        
        self.current_frame = 0
        self.animation_timer = self.startTimer(25)

    def stop_animation(self):
        if not self.animation_timer:
            return

        self.killTimer(self.animation_timer)
        self.animation_timer = None

        self.tray_icon.setContextMenu(self.menu)
        self.update_icon()

    @logger.log_exc
    def timerEvent(self, event):
        if event.timerId() == self.animation_timer:
            self.tray_icon.setIcon(self.frames[self.current_frame])
            self.current_frame = (self.current_frame + 1) % 40
        else:
            super(TrayIcon, self).timerEvent(event)

    @logger.log_exc
    def icon_activated(self, reason):
        if self.animation_timer:
            return
        
        if reason != QtGui.QSystemTrayIcon.Trigger:
            return
        
        action = None
        
        if 'duplicates' in self.icon_state:
            action = self.action_show_duplicates
        elif 'bad_urls' in self.icon_state:
            action = self.action_send_bad_urls
        elif self.icon_action in self.icon_actions:
            action = self.icon_actions[self.icon_action]

        if action and action.isEnabled():
            action.trigger()

    def show(self):
        self.tray_icon.show()

    def notify(self, title, message, error=False):
        if self.NOTIFICATIONS:
            self.notification.update(title, message, 'new-wallpaper')
            if error:
                self.notification.set_urgency(notify.URGENCY_CRITICAL)
            else:
                self.notification.set_urgency(notify.URGENCY_NORMAL)
            self.notification.show()
        else:
            if error:
                icon = QtGui.QSystemTrayIcon.Information
            else:
                icon = QtGui.QSystemTrayIcon.Critical
            self.tray_icon.showMessage(title, message, icon)

    def notification_callback(self, notification, action, user_data):
        qt_action = None
        
        if action == 'duplicates':
            qt_action = self.action_show_duplicates
        if action == 'bad_urls':
            qt_action = self.action_send_bad_urls

        if qt_action and qt_action.isEnabled():
            qt_action.trigger()

    def set_icon_action(self, icon_action):
        self.icon_action = icon_action

    def set_anonymous(self, value):
        self.anonymous = value
        
        self.action_wallpapers_last.setDisabled(value)
        self.action_wallpapers_new.setDisabled(value)
        self.action_add_url.setDisabled(value)

        if value:
            self.action_send_bad_urls.setEnabled(False)

    def set_force_scheduled(self, value):
        self.action_force_scheduled.setEnabled(value)

    def set_bad_urls(self, value):
        self.action_send_bad_urls.setEnabled(not self.anonymous and value)

        if self.NOTIFICATIONS:
            if not self.anonymous and value:
                self.notification_bad_urls.show()
            elif not value:
                self.notification_bad_urls.close()
        else:
            if value and not self.anonymous:
                self.icon_state.add('bad_urls')
            elif not value and 'bad_urls' in self.icon_state:
                self.icon_state.remove('bad_urls')

            self.update_icon()

    def set_duplicates(self, value):
        self.action_show_duplicates.setEnabled(value)

        if self.NOTIFICATIONS:
            if value:
                self.notification_duplicates.show()
            else:
                self.notification_duplicates.close()
        else:
            if value and 'duplicates' not in self.icon_state:
                self.icon_state.add('duplicates')
            elif not value and 'duplicates' in self.icon_state:
                self.icon_state.remove('duplicates')

            self.update_icon()

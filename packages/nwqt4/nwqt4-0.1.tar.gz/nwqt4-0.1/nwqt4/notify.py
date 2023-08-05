#  notify.py
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

import dbus
from dbus.mainloop.qt import DBusQtMainLoop

EXPIRES_DEFAULT = -1
EXPIRES_NEVER = 0

URGENCY_LOW = 0
URGENCY_NORMAL = 1
URGENCY_CRITICAL = 2

REASON_EXPIRED = 1
REASON_DISMISSED = 2
REASON_CLOSED = 3
REASON_UNDEFINED = 4

def init(app_name=''):
    if not isinstance(app_name, basestring):
        raise TypeError

    global _bus
    global _app_name

    try:        
        _bus = dbus.SessionBus(mainloop=DBusQtMainLoop(set_as_default=True))
        _proxy().GetServerInformation(dbus_interface=_BUS_NAME)

        try:
            _bus.add_signal_receiver(
                _notification_closed,
                'NotificationClosed',
                bus_name = _BUS_NAME,
                path = _PATH
            )
            _bus.add_signal_receiver(
                _action_invoked,
                'ActionInvoked',
                bus_name = _BUS_NAME,
                path = _PATH
            )
        except RuntimeError:
            return False
    except dbus.exceptions.DBusException:
        return False

    _app_name = app_name

    return True

def is_initted():
    return not _app_name is None

def uninit():
    global _app_name
    _app_name = None

def get_app_name():
    return _app_name

def get_server_caps():
    return map(unicode, _proxy().GetCapabilities(dbus_interface=_BUS_NAME))

def get_server_info():
    info = _proxy().GetServerInformation(dbus_interface=_BUS_NAME)
    return {
        'name': unicode(info[0]),
        'vendor': unicode(info[1]),
        'version': unicode(info[2]),
        'spec-version': unicode(info[3])
    }

class Notification(object):
    def __init__(self, summary, body, icon=''):
        self.id = dbus.UInt32(0)
        self.actions = {}
        self.hints = {}
        self.timeout = dbus.Int32(EXPIRES_DEFAULT)
        self.close_callback = None

        self.update(summary, body, icon)

    def update(self, summary, body, icon=''):
        if not isinstance(summary, basestring):
            raise TypeError('summary')
        if not isinstance(body, basestring):
            raise TypeError('body')
        if not isinstance(icon, basestring):
            raise TypeError('icon')

        self.summary = summary
        self.body = body
        self.icon = icon

    def add_action(self, action, label, callback, user_data=None):
        if not isinstance(action, basestring):
            raise TypeError('action')
        if not isinstance(label, basestring):
            raise TypeError('label')
        if not callable(callback):
            raise TypeError('callback')

        self.actions[action] = {
            'label': label,
            'callback': callback,
            'user_data': user_data
        }

    def clear_actions(self):
        self.actions = {}

    def set_hint(self, key, value):
        if not isinstance(key, basestring):
            raise TypeError('key')
        
        self.hints[key] = value

    def set_urgency(self, urgency):
        if urgency not in (URGENCY_LOW, URGENCY_NORMAL, URGENCY_CRITICAL):
            raise ValueError('urgency')
            
        self.hints['urgency'] = dbus.Byte(urgency)

    def set_category(self, category):
        if not isinstance(category, basestring):
            raise TypeError('category')

        self.hints['category'] = category

    def clear_hints(self):
        self.hints = {}

    def set_timeout(self, timeout):
        if not isinstance(timeout, int):
            raise TypeError('timeout')

        self.timeout = dbus.Int32(timeout)

    def show(self):
        actions = dbus.Array(signature='s')
        for key, value in self.actions.iteritems():
            actions.extend((key, value['label']))

        hints = dbus.Dictionary(signature='sv')
        for key, value in self.hints.iteritems():
            hints[key] = value

        self.id = _proxy().Notify(
            _app_name,
            self.id,
            self.icon,
            self.summary,
            self.body,
            actions,
            hints,
            self.timeout,
            dbus_interface=_BUS_NAME
        )

        _notifications[self.id] = self

    def close(self):
        try:
            _proxy().CloseNotification(self.id, dbus_interface=_BUS_NAME)
        except dbus.exceptions.DBusException:
            pass

    def set_close_callback(self, callback):
        if not callable(callback):
            raise TypeError('callback')
        
        self.close_callback = callback

    def _notification_closed(self, reason):
        if callable(self.close_callback):
            self.close_callback(reason)

        del _notifications[self.id]
        self.id = dbus.UInt32(0)

    def _action_invoked(self, action):
        if action not in self.actions:
            return

        self.actions[action]['callback'](
            self,
            action,
            self.actions[action]['user_data']
        )


_BUS_NAME = 'org.freedesktop.Notifications'
_PATH = '/org/freedesktop/Notifications'

_app_name = None
_notifications = {}

def _proxy():
    return _bus.get_object(_BUS_NAME, _PATH)

def _notification_closed(id, reason):
    _notifications[id]._notification_closed(reason)

def _action_invoked(id, action):
    _notifications[id]._action_invoked(action)

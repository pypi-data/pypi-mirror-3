#       nwapp.py
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

import datetime
import gettext
import hashlib
import logging
import os
import shutil
import subprocess

from PyQt4 import QtCore, QtGui

import logger

import api_v1
import config
import config_dialog
import common
import settings
import trayicon
import dialogs

try:
    import duplicates
except ImportError:
    DUPLICATES = False
else:
    DUPLICATES = True

class NWApp(QtGui.QApplication):
    def __init__(self, argv):
        super(NWApp, self).__init__(argv)

        homedir = os.path.expanduser('~')
        xdg_config = os.getenv(
            'XDG_CONFIG_HOME',
            os.path.join(homedir, '.config')
        )
        self.appdir = os.path.join(xdg_config, 'new-wallpaper')
        self.wallsdir = os.path.join(self.appdir, 'wallpapers')
        self.thumbsdir = os.path.join(self.appdir, 'thumbs')
        self.scriptsdir = os.path.join(self.appdir, 'scripts')

        for path in (
                xdg_config,
                self.appdir,
                self.wallsdir,
                self.thumbsdir,
                self.scriptsdir
            ):
                if not os.path.isdir(path):
                    os.mkdir(path)

        self.log_file = os.path.join(self.appdir, 'nwqt4.log')
        logging.basicConfig(
            filename = self.log_file,
            level = logging.DEBUG,
            format = '%(asctime)s %(levelname)s %(message)s'
        )

        self.install_scripts()

        self.config = config.Config(self.appdir)

        self.settings = settings.Settings(self.config)

        self.tray_icon = trayicon.TrayIcon(
            self.settings['icon/action'], self.settings['auth/anonymous'])
        self.tray_icon.set_force_scheduled(self.settings['schedule/enabled'])
        self.tray_icon.show()

        self.tray_icon.wallpapers_random_triggered.connect(
            self.random_wallpaper_request)
        self.tray_icon.wallpapers_last_triggered.connect(
            self.last_wallpaper_request)
        self.tray_icon.wallpapers_new_triggered.connect(
            self.new_wallpaper_request)

        self.tray_icon.add_url_triggered.connect(
            self.add_url_request)

        self.tray_icon.force_scheduled_triggered.connect(
            self.force_scheduled_request)

        self.tray_icon.last_set_wallpaper_triggered.connect(
            self.last_set_wallpaper_triggered)

        self.tray_icon.send_bad_urls_triggered.connect(
            self.send_bad_urls_triggered)

        self.tray_icon.show_duplicates_triggered.connect(
            self.show_duplicates_triggered)
            
        self.tray_icon.settings_triggered.connect(self.show_settings)

        self.tray_icon.quit_triggered.connect(self.exit)

        self.setWindowIcon(QtGui.QIcon(common.get_pixmap('new-wallpaper.svg')))
        self.setQuitOnLastWindowClosed(False)

        self.last_set_wallpaper = None
        self.bad_urls = []
        self.duplicates = []
        self.busy_counter = 0
        self.choice_duplicates_dialog = None

        self.last_scheduled = self.config.read_date('last_scheduled/request')
        if self.settings['schedule/enabled']:
            self.scheduler_check()

        if DUPLICATES:
            self.get_potentials()

        self.timer_id = self.startTimer(60000)

    def install_scripts(self):
        scripts_dir = common.get_data_file('scripts')
        for filename in os.listdir(scripts_dir):
            filepath = os.path.join(self.scriptsdir, filename)
            shutil.copy2(
                os.path.join(scripts_dir, filename),
                filepath
            )
            os.chmod(filepath, 0o755)

    def get_userid_and_password(self):
        if self.settings['auth/anonymous']:
            return None, '', False
        
        return (
            self.settings['auth/userid'],
            self.settings['auth/password'],
            self.settings['auth/use_ssl']
        )

    @logger.log_exc
    def error_callback(self, error):
        self.set_busy(False)
        self.notify_error(unicode(error))

    def update_last_set_wallpaper(self, result):
        if not self.last_set_wallpaper:
            return

        if self.last_set_wallpaper['name'] != result['name']:
            return

        self.last_set_wallpaper.update(result)

    def set_busy(self, is_busy):
        if is_busy:
            if self.busy_counter == 0:
                self.tray_icon.start_animation()
            self.busy_counter += 1
        else:
            if self.busy_counter == 1:
                self.tray_icon.stop_animation()
            self.busy_counter -= 1

    def notify_info(self, message):
        self.tray_icon.notify('New Wallpaper', message)

    def notify_error(self, message):
        self.tray_icon.notify(
            'New Wallpaper',
            message,
            error = True
        )

    def set_wallpaper(self, result):
        @logger.log_exc
        def copy_callback(filename):
            if filename and self.check_sha1(filename):
                self.set_busy(False)

                if result['bad_urls']:
                    self.bad_urls.extend(result['bad_urls'])
                    self.tray_icon.set_bad_urls(True)

                
                return self.run_script(filename)

            result['bad_urls'].append(result['urls'][result['url_index']])
            result['url_index'] += 1

            if result['url_index'] < len(result['urls']):
                return common.download_url(result['urls'][result['url_index']],
                    result['copypath'], copy_callback)

            self.set_busy(False)

            self.bad_urls.extend(result['bad_urls'])
            self.tray_icon.set_bad_urls(True)
            self.notify_error(_('All urls failed to download'))

        result['copypath'] = os.path.join(self.wallsdir, result['name'])
        if self.check_sha1(result['copypath']):
            return self.run_script(result['copypath'])

        if not result['urls']:
            return self.notify_error(_('There are no urls for this wallpaper'))
        
        result['url_index'] = 0
        result['bad_urls'] = []

        common.download_url(result['urls'][0], result['copypath'],
            copy_callback)

        self.set_busy(True)

    def check_sha1(self, filename):
        if not os.path.isfile(filename):
            return False
        
        parts = os.path.basename(filename).split('_')
        if not parts:
            return False

        content = open(filename, 'r').read()
        sha1 = hashlib.sha1(content).hexdigest()

        return parts[0] == sha1

    def run_script(self, wallpaper_path):
        if not self.settings['script/path']:
            return self.notify_error(_('You must configure script'))
        
        try:
            subprocess.Popen([self.settings['script/path'], wallpaper_path])
        except OSError, exc:
            self.notify_error(
                _('Script error: ') + exc.strerror.decode('utf8', 'replace'))

    def process_results(self, response, params, set_wallpaper=True,
        useronly=True, check_duplicates=True):

        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)

            self.process_results(
                response,
                params,
                set_wallpaper,
                useronly,
                check_duplicates=False
            )

        results = response['results']
        if not results:
            self.notify_info(_('Not returned any result'))
            return

        if DUPLICATES and check_duplicates:
            wallpapers = [result['name'] for result in results]

            originals = duplicates.get_originals(
                self.appdir,
                wallpapers,
                self.settings['search_for_duplicates/mean'],
                self.settings['search_for_duplicates/stddev']
            )

            if originals:
                to_delete = []

                for copy, original in originals.iteritems():
                    wallpapers.remove(copy)

                    if not original in wallpapers:
                        wallpapers.append(original)
                    else:
                        to_delete.append(copy)

                for copy in to_delete:
                    del originals[copy]

            if originals:
                userid, password, secure = self.get_userid_and_password()

                request = api_v1.WallpapersInfo(wallpapers, useronly,
                    userid, password, secure)
                request.success.connect(success_callback)
                request.error.connect(self.error_callback)

                return self.set_busy(True)
            else:
                results = [
                    result for result in results
                    if result['name'] in wallpapers
                ]

            if DUPLICATES and 'nulls' in response:
                for wallpaper in response['nulls']:
                    try:
                        os.unlink(os.path.join(self.thumbsdir, wallpaper))
                        duplicates.delete_status(self.appdir, wallpaper)
                    except:
                        duplicates.set_invalid_status(self.appdir, wallpaper)

        if set_wallpaper:
            self.set_wallpaper(results[0])
        else:
            for result in results:
                result['cached'] = os.path.isfile(
                    os.path.join(self.wallsdir, result['name']))
            
            self.results_dialog = dialogs.Results(self, params, results)
            self.results_dialog.finished.connect(self.results_dialog_closed)
            self.results_dialog.show()

    @logger.log_exc
    def results_dialog_closed(self, result):
        self.results_dialog.deleteLater()

    @logger.log_exc
    def random_wallpaper_request(self, checked=False):
        if self.settings['random_wallpaper/ask_settings']:
            values = {
                'anonymous': self.settings['auth/anonymous'],
                'count': self.config.read_int(
                    'last_random_wallpaper/count', 1),
                'resolutions': self.config.read_string(
                    'last_random_wallpaper/resolutions'),
                'tags': self.config.read_string(
                    'last_random_wallpaper/tags'),
                'notags': self.config.read_string(
                    'last_random_wallpaper/notags'),
                'useronly': self.config.read_bool(
                    'last_random_wallpaper/useronly'),
                'set_wallpaper': self.config.read_bool(
                    'last_random_wallpaper/set_wallpaper', True)
            }

            self.random_wallpaper_dialog = dialogs.request.RandomWallpaper(
                values)
            self.random_wallpaper_dialog.accepted.connect(
                self.random_wallpaper_dialog_accepted)
            self.random_wallpaper_dialog.rejected.connect(
                self.random_wallpaper_dialog_rejected)
            self.random_wallpaper_dialog.show()
        else:
            self.request_random_wallpaper(
                self.settings['random_wallpaper/count'],
                self.settings['random_wallpaper/resolutions'],
                self.settings['random_wallpaper/tags'],
                self.settings['random_wallpaper/notags'],
                self.settings['random_wallpaper/useronly'],
                self.settings['random_wallpaper/set_wallpaper']
            )

    @logger.log_exc
    def random_wallpaper_dialog_accepted(self):
        values = self.random_wallpaper_dialog.export_values()
        self.config.write('last_random_wallpaper/count', values['count'])
        self.config.write('last_random_wallpaper/resolutions',
            values['resolutions'])
        self.config.write('last_random_wallpaper/tags', values['tags'])
        self.config.write('last_random_wallpaper/notags', values['notags'])
        self.config.write('last_random_wallpaper/useronly', values['useronly'])
        self.config.write('last_random_wallpaper/set_wallpaper',
            values['set_wallpaper'])
        self.config.sync()
        self.random_wallpaper_dialog.deleteLater()
        self.request_random_wallpaper(**values)

    @logger.log_exc
    def random_wallpaper_dialog_rejected(self):
        self.random_wallpaper_dialog.deleteLater()

    def request_random_wallpaper(self, count=1, resolutions=None, tags=None,
        notags=None, useronly=False, set_wallpaper=True):

        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)

            self.process_results(
                response,
                {
                    'title': _('Random wallpaper'),
                    'method': self.request_random_wallpaper,
                    'args': [count, resolutions, tags, notags, useronly,
                        set_wallpaper]
                },
                set_wallpaper,
                useronly
            )

        userid, password, secure = self.get_userid_and_password()

        request = api_v1.WallpapersRandom(count, resolutions, tags, notags,
            useronly, userid, password, secure)
        request.success.connect(success_callback)
        request.error.connect(self.error_callback)

        self.set_busy(True)

    @logger.log_exc
    def last_wallpaper_request(self, checked=False):
        if self.settings['last_wallpaper/ask_settings']:
            values = {
                'count': self.config.read_int(
                    'last_last_wallpaper/count', 1),
                'set_wallpaper': self.config.read_bool(
                    'last_last_wallpaper/set_wallpaper', True)
            }

            self.last_wallpaper_dialog = dialogs.request.LastWallpaper(
                values)
            self.last_wallpaper_dialog.accepted.connect(
                self.last_wallpaper_dialog_accepted)
            self.last_wallpaper_dialog.rejected.connect(
                self.last_wallpaper_dialog_rejected)
            self.last_wallpaper_dialog.show()
        else:
            self.request_last_wallpaper(
                self.settings['last_wallpaper/count'],
                self.settings['last_wallpaper/set_wallpaper']
            )

    @logger.log_exc
    def last_wallpaper_dialog_accepted(self):
        values = self.last_wallpaper_dialog.export_values()
        self.config.write('last_last_wallpaper/count', values['count'])
        self.config.write('last_last_wallpaper/set_wallpaper',
            values['set_wallpaper'])
        self.config.sync()
        self.last_wallpaper_dialog.deleteLater()
        self.request_last_wallpaper(**values)

    @logger.log_exc
    def last_wallpaper_dialog_rejected(self):
        self.last_wallpaper_dialog.deleteLater()

    def request_last_wallpaper(self, count=1, set_wallpaper=True):
        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)
            
            self.process_results(
                response,
                {
                    'title': _('Last wallpaper'),
                    'method': self.request_last_wallpaper,
                    'args': [count, set_wallpaper]
                },
                set_wallpaper
            )

        userid, password, secure = self.get_userid_and_password()

        request = api_v1.WallpapersLast(count, userid, password, secure)
        request.success.connect(success_callback)
        request.error.connect(self.error_callback)

        self.set_busy(True)

    @logger.log_exc
    def new_wallpaper_request(self, checked=False):
        if self.settings['new_wallpaper/ask_settings']:
            values = {
                'count': self.config.read_int(
                    'last_new_wallpaper/count', 1),
                'weight': self.config.read_float(
                    'last_new_wallpaper/weight', 1.0),
                'set_wallpaper': self.config.read_bool(
                    'last_new_wallpaper/set_wallpaper', True)
            }

            self.new_wallpaper_dialog = dialogs.request.NewWallpaper(
                values)
            self.new_wallpaper_dialog.accepted.connect(
                self.new_wallpaper_dialog_accepted)
            self.new_wallpaper_dialog.rejected.connect(
                self.new_wallpaper_dialog_rejected)
            self.new_wallpaper_dialog.show()
        else:
            self.request_new_wallpaper(
                self.settings['new_wallpaper/count'],
                self.settings['new_wallpaper/weight'],
                self.settings['new_wallpaper/set_wallpaper']
            )

    @logger.log_exc
    def new_wallpaper_dialog_accepted(self):
        values = self.new_wallpaper_dialog.export_values()
        self.config.write('last_new_wallpaper/count', values['count'])
        self.config.write('last_new_wallpaper/weight', values['weight'])
        self.config.write('last_new_wallpaper/set_wallpaper',
            values['set_wallpaper'])
        self.config.sync()
        self.new_wallpaper_dialog.deleteLater()
        self.request_new_wallpaper(**values)

    @logger.log_exc
    def new_wallpaper_dialog_rejected(self):
        self.new_wallpaper_dialog.deleteLater()

    def request_new_wallpaper(self, count=1, weight=1.0, set_wallpaper=True):
        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)

            self.process_results(
                response,
                {
                    'title': _('New wallpaper'),
                    'method': self.request_new_wallpaper,
                    'args': [count, weight, set_wallpaper]
                },
                set_wallpaper,
                useronly=False
            )

        userid, password, secure = self.get_userid_and_password()

        request = api_v1.WallpapersNew(count, weight, userid, password, secure)
        request.success.connect(success_callback)
        request.error.connect(self.error_callback)

        self.set_busy(True)

    @logger.log_exc
    def add_url_request(self, checked=False):
        values = {
            'xmpp': self.config.read_bool('last_add_url/xmpp')
        }

        self.add_url_dialog = dialogs.AddUrl(values)
        self.add_url_dialog.accepted.connect(self.add_url_dialog_accepted)
        self.add_url_dialog.rejected.connect(self.add_url_dialog_rejected)
        self.add_url_dialog.show()

    @logger.log_exc
    def add_url_dialog_accepted(self):
        values = self.add_url_dialog.export_values()

        self.config.write('last_add_url/xmpp', values['xmpp'])
        self.config.sync()
        self.add_url_dialog.deleteLater()
        self.request_add_url(**values)

    @logger.log_exc
    def add_url_dialog_rejected(self):
        self.add_url_dialog.deleteLater()

    def request_add_url(self, url, tags=None, xmpp=None):
        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)
            
            if 'result' not in response:
                return self.notify_error(_('Bad response'))

            self.notify_info(response['result'])

        userid, password, secure = self.get_userid_and_password()

        request = api_v1.AddUrl(url, userid, password, tags, xmpp, secure)
        request.success.connect(success_callback)
        request.error.connect(self.error_callback)

        self.set_busy(True)

    def request_add_wallpaper(self, wallpaper, tags):
        self.request_add(wallpaper, tags)

    def request_add_tags(self, wallpaper, tags):
        self.request_add(wallpaper, tags, tags_only=True)

    def request_add(self, wallpaper, tags, tags_only=False):
        Request = (api_v1.AddWallpaper, api_v1.AddTags)[tags_only]
        
        userid, password, secure = self.get_userid_and_password()
        
        request = Request(wallpaper, tags, userid, password, secure)
        request.success.connect(self.add_wallpaper_tags_callback)
        request.error.connect(self.error_callback)

        self.set_busy(True)

    @logger.log_exc
    def add_wallpaper_tags_callback(self, response):
        self.set_busy(False)

        if 'result' not in response:
            return self.notify_error(_('Bad response'))

        result = response['result']
        self.results_dialog.update_result(result)
        self.update_last_set_wallpaper(result)

        tags = result['user_tags'] if result['user'] else result['tags']
        message = '%s\n%s %s' % (
            result['name'],
            _('Top tags:'),
            ', '.join(tags)
        )
        self.notify_info(message)

    def request_reject_wallpaper(self, wallpaper):
        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)

            if 'result' not in response:
                return self.notify_error(_('Bad response'))

            self.results_dialog.update_result(response['result'])
            self.update_last_set_wallpaper(response['result'])

        userid, password, secure = self.get_userid_and_password()

        request = api_v1.RejectWallpaper(wallpaper, userid, password, secure)
        request.success.connect(success_callback)
        request.error.connect(self.error_callback)

        self.set_busy(True)

    @logger.log_exc
    def force_scheduled_request(self, checked=False):
        self.scheduler_check(force=True)

    @logger.log_exc
    def last_set_wallpaper_triggered(self, checked=False):
        self.last_set_wallpaper['thumbpath'] = os.path.join(
            self.thumbsdir, self.last_set_wallpaper['name'])

        if os.path.isfile(self.last_set_wallpaper['thumbpath']):
            return self.show_last_set_wallpaper()

        common.download_url(
            self.last_set_wallpaper['thumb'],
            self.last_set_wallpaper['thumbpath'],
            self.download_thumb_callback
        )

        self.set_busy(True)

    @logger.log_exc
    def download_thumb_callback(self, filename):
        self.set_busy(False)

        if not filename:
            return self.notify_error(_('Thumb downloading error'))

        self.show_last_set_wallpaper()

    def show_last_set_wallpaper(self):
        self.wallpaper_info_dialog = dialogs.WallpaperInfo(
            self, self.last_set_wallpaper)
        self.wallpaper_info_dialog.finished.connect(
            self.wallpaper_info_dialog_closed)
        self.wallpaper_info_dialog.show()

    @logger.log_exc
    def wallpaper_info_dialog_closed(self, result):
        self.wallpaper_info_dialog.deleteLater()

    @logger.log_exc
    def send_bad_urls_triggered(self, checked=False):
        self.tray_icon.set_bad_urls(False)

        urls_to_send = self.bad_urls[:5]
        self.bad_urls[:5] = []
        values = {
            'urls': urls_to_send
        }

        self.send_bad_urls_dialog = dialogs.SendBadUrls(values)
        self.send_bad_urls_dialog.accepted.connect(
            self.send_bad_urls_dialog_accepted)
        self.send_bad_urls_dialog.rejected.connect(
            self.send_bad_urls_dialog_rejected)
        self.send_bad_urls_dialog.show()

    @logger.log_exc
    def send_bad_urls_dialog_accepted(self):
        values = self.send_bad_urls_dialog.export_values()
        if values['urls']:
            self.request_send_bad_urls(**values)

        if self.bad_urls:
            self.tray_icon.set_bad_urls(True)

        self.send_bad_urls_dialog.deleteLater()

    @logger.log_exc
    def send_bad_urls_dialog_rejected(self):
        self.send_bad_urls_dialog.deleteLater()

    def request_send_bad_urls(self, urls):
        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)

            if 'result' not in response:
                return self.notify_error(_('Bad response'))

            self.notify_info(ngettext(
                '%d url accepted',
                '%d urls accepted',
                response['result']) % response['result'])

        userid, password, secure = self.get_userid_and_password()

        response = api_v1.SendBadUrls(urls, userid, password, secure)
        response.success.connect(success_callback)
        response.error.connect(self.error_callback)

        self.set_busy(True)

    @logger.log_exc
    def show_duplicates_triggered(self, checked=False):
        self.tray_icon.set_duplicates(False)

        duplicates = self.duplicates[:5]
        self.duplicates[:5] = []
        values = {
            'duplicates': duplicates
        }

        self.choice_duplicates_dialog = dialogs.ChoiceDuplicates(
            self.thumbsdir, values)
        self.choice_duplicates_dialog.accepted.connect(
            self.choice_duplicates_dialog_accepted)
        self.choice_duplicates_dialog.rejected.connect(
            self.choice_duplicates_dialog_finished)
        self.choice_duplicates_dialog.show()

    @logger.log_exc
    def choice_duplicates_dialog_accepted(self):
        @logger.log_exc
        def success_callback(response):
            self.set_busy(False)
            
            self.notify_info(_('Duplicate has been sent'))
        
        choices = self.choice_duplicates_dialog.get_choices()

        duplicates.save_choices(self.appdir, choices)

        send_duplicates = not self.settings['auth/anonymous'] \
            and self.settings['search_for_duplicates/send']
        if send_duplicates:
            userid, password, secure = self.get_userid_and_password()

            for choice in choices:
                if not choice[4]:
                    continue

                original = choice[0] if choice[4] == 1 else choice[1]
                copy     = choice[1] if choice[4] == 1 else choice[0]

                request = api_v1.SendDuplicate(original, copy,
                    userid, password, secure)
                request.success.connect(success_callback)
                request.error.connect(self.error_callback)

                self.set_busy(True)

        self.choice_duplicates_dialog_finished()

    @logger.log_exc
    def choice_duplicates_dialog_rejected(self):
        self.choice_duplicates_dialog_finished()
        
    def choice_duplicates_dialog_finished(self):
        self.choice_duplicates_dialog.deleteLater()
        self.choice_duplicates_dialog = None

        self.get_potentials()

    @logger.log_exc
    def show_settings(self):
        scripts = self.scan_scripts()
        self.config_dialog = config_dialog.ConfigDialog(self.settings,
            scripts, duplicates=DUPLICATES)
        self.config_dialog.accepted.connect(self.settings_accepted)
        self.config_dialog.show()

    def scan_scripts(self):
        scripts = []
            
        for filename in sorted(os.listdir(self.scriptsdir)):
            filepath = os.path.join(self.scriptsdir, filename)
            if os.access(filepath, os.X_OK):
                scripts.append((filename, filepath))

        return scripts

    @logger.log_exc
    def settings_accepted(self):
        settings = self.config_dialog.export_settings()
        self.settings.update(settings)
        self.settings.save()

        self.tray_icon.set_icon_action(self.settings['icon/action'])
        self.tray_icon.set_anonymous(self.settings['auth/anonymous'])
        self.tray_icon.set_force_scheduled(self.settings['schedule/enabled'])

    @logger.log_exc
    def timerEvent(self, event):
        super(NWApp, self).timerEvent(event)

        if event.timerId() != self.timer_id:
            return

        if self.settings['schedule/enabled']:
            self.scheduler_check()

        if DUPLICATES and self.settings['search_for_duplicates/enabled']:
            self.search_duplicates_check()


    def scheduler_check(self, force=False):
        now = datetime.datetime.utcnow()
        scheduler_delta = datetime.timedelta(
            hours=self.settings['schedule/schedule'])
        delta = now - self.last_scheduled

        if force or delta > scheduler_delta:
            self.scheduler_request()

            if force:
                self.last_scheduled = now
            else:
                while self.last_scheduled < now:
                    self.last_scheduled += scheduler_delta

                self.last_scheduled -= scheduler_delta

            self.config.write_date('last_scheduled/request',
                self.last_scheduled)
            self.config.sync()

    def scheduler_request(self):
        if self.settings['schedule/request'] == 'random_wallpaper':
            self.request_random_wallpaper(
                self.settings['scheduled_random_wallpaper/count'],
                self.settings['scheduled_random_wallpaper/resolutions'],
                self.settings['scheduled_random_wallpaper/tags'],
                self.settings['scheduled_random_wallpaper/notags'],
                self.settings['scheduled_random_wallpaper/useronly'],
                self.settings['scheduled_random_wallpaper/set_wallpaper']
            )
        elif self.settings['schedule/request'] == 'last_wallpaper':
            self.request_last_wallpaper(
                self.settings['scheduled_last_wallpaper/count'],
                self.settings['scheduled_last_wallpaper/set_wallpaper']
            )
        elif self.settings['schedule/request'] == 'new_wallpaper':
            self.request_new_wallpaper(
                self.settings['scheduled_new_wallpaper/count'],
                self.settings['scheduled_new_wallpaper/weight'],
                self.settings['scheduled_new_wallpaper/set_wallpaper']
            )

    def get_potentials(self):
        if self.choice_duplicates_dialog:
            return
        
        potentials = duplicates.get_potentials(
            self.appdir,
            self.settings['search_for_duplicates/mean'],
            self.settings['search_for_duplicates/stddev']
        )

        self.duplicates = list(set(self.duplicates + potentials))
        if self.duplicates:
            self.tray_icon.set_duplicates(True)

    def search_duplicates_check(self):
        now = datetime.datetime.utcnow()
        search_duplicates_delta = datetime.timedelta(
            minutes=self.settings['search_for_duplicates/interval'])
        last_scheduled = self.config.read_date(
            'last_scheduled/search_for_duplicates')
        delta = now - last_scheduled

        if delta > search_duplicates_delta:
            self.search_duplicates()

            while last_scheduled < now:
                last_scheduled += search_duplicates_delta
            last_scheduled -= search_duplicates_delta

            self.config.write_date('last_scheduled/search_for_duplicates',
                last_scheduled)
            self.config.sync()

    def search_duplicates(self):
        last_image1 = self.config.read_string(
            'search_for_duplicates/last_image1')
        last_image2 = self.config.read_string(
            'search_for_duplicates/last_image2')
        limit = self.settings['search_for_duplicates/limited'] \
            and self.settings['search_for_duplicates/limit']

        last_pair = duplicates.find_potentials(
            self.appdir,
            self.settings['search_for_duplicates/mean'],
            self.settings['search_for_duplicates/stddev'],
            limit,
            last_image1,
            last_image2,
            QtCore.QCoreApplication.processEvents
        )

        self.config.write('search_for_duplicates/last_image1', last_pair[0])
        self.config.write('search_for_duplicates/last_image2', last_pair[1])
        self.config.sync()

        self.get_potentials()

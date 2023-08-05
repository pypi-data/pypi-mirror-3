#       api_v1.py
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

import json

from PyQt4 import QtCore
from PyQt4 import QtNetwork

import logger
import common

certificate = QtNetwork.QSslCertificate.fromPath(
    common.get_data_file('cert/new-wallpaper.org.pem'))

ssl_config = QtNetwork.QSslConfiguration()
ssl_config.setCaCertificates(certificate)

manager = QtNetwork.QNetworkAccessManager()

def strings_to_translate():
    _('Authentication failed')
    _('Invalid HTTP method')
    _('Wallpapers not sent')
    _('Processing of url completed')
    _('Url queued for processing')
    _('Invalid action')
    _('Invalid wallpaper')
    _('Tags not sent')
    _('Urls not sent')
    _('Invalid original or copy')
    _('Duplicate already sent')

class Request(QtCore.QObject):
    BASE_URL = 'new-wallpaper.org/api/v1/'

    success = QtCore.pyqtSignal(dict)
    error = QtCore.pyqtSignal(unicode)

    def __init__(self, path='', params={}, userid=None, password='',
        secure=False):

        super(Request, self).__init__(manager)

        self.path = path
        self.params = params
        self.userid = userid
        self.password = password
        self.secure = secure

        self.get_response()

    def get_response(self):
        proto = ('http://', 'https://')[self.secure]
        url = QtCore.QUrl(proto + self.BASE_URL + self.path)

        if self.userid:
            if type(self.params).__name__ == 'dict':
                self.params['userid'] = self.userid
                self.params['password'] = self.password
            elif type(self.params).__name__ == 'list':
                self.params.append(('userid', self.userid))
                self.params.append(('password', self.password))
            else:
                self.params = {
                    'userid': self.userid,
                    'password': self.password
                }

        query = QtCore.QUrl(url)
        if type(self.params).__name__ == 'dict':
            iterparams = self.params.iteritems()
        else:
            iterparams = iter(self.params)
        for k, v in iterparams:
            query.addQueryItem(k, v)

        if self.userid:
            request = QtNetwork.QNetworkRequest(url)
            request.setSslConfiguration(ssl_config)
            self.reply = manager.post(request, query.encodedQuery())
        else:
            request = QtNetwork.QNetworkRequest(query)
            request.setSslConfiguration(ssl_config)
            self.reply = manager.get(request)

        self.reply.finished.connect(self.finished)

    @logger.log_exc
    def finished(self):
        if self.reply.error():
            self.error.emit(_('No response'))
            return

        try:
            response = json.loads(unicode(self.reply.readAll()))
        except:
            self.error.emit(_('Bad response'))
            return

        if type(response).__name__ != 'dict' or 'success' not in response:
            self.error.emit(_('Bad response'))
            return

        if not response['success']:
            if 'error' in response:
                self.error.emit(_(response['error']))
            else:
                self.error.emit(_('Bad response'))
            return

        self.success.emit(response)

class WallpapersInfo(Request):
    def __init__(self, wallpapers, useronly=False, userid=None, password='',
        secure=False):

        params = [('wallpaper', wallpaper) for wallpaper in wallpapers]
        if useronly:
            params.append(('useronly', '1'))

        super(WallpapersInfo, self).__init__('wallpapers/info/',
            params, userid, password, secure)

class WallpapersRandom(Request):
    def __init__(self, count=1, resolutions=None, tags=None, notags=None,
        useronly=False, userid=None, password='', secure=False):

        params = {
            'count': str(count)
        }
        if resolutions:
            params['resolutions'] = resolutions
        if tags:
            params['tags'] = tags
        if notags:
            params['notags'] = notags
        if useronly:
            params['useronly'] = '1'

        super(WallpapersRandom, self).__init__('wallpapers/random/',
            params, userid, password, secure)

class WallpapersLast(Request):
    def __init__(self, count, userid, password, secure=False):
        params = {
            'count': str(count)
        }

        super(WallpapersLast, self).__init__('wallpapers/last/',
            params, userid, password, secure)

class WallpapersNew(Request):
    def __init__(self, count, weight, userid, password, secure=False):
        params = {
            'count': str(count),
            'weight': str(weight)
        }

        super(WallpapersNew, self).__init__('wallpapers/new/',
            params, userid, password, secure)

class AddUrl(Request):
    def __init__(self, url, userid, password, tags=None, xmpp=False,
        secure=False):

        params = {
            'url': url
        }
        if tags:
            params['tags'] = tags
        if xmpp:
            params['xmpp'] = '1'

        super(AddUrl, self).__init__('add/url/',
            params, userid, password, secure)

class Add(Request):
    def __init__(self, action, wallpaper, tags, userid, password,
        secure=False):

        params = {
            'tags': tags or ''
        }

        super(Add, self).__init__('add/%s/%s/' % (action, wallpaper),
            params, userid, password, secure)

class AddWallpaper(Add):
    def __init__(self, wallpaper, tags, userid, password, secure=False):
        super(AddWallpaper, self).__init__('wallpaper', wallpaper, tags,
            userid, password, secure)

class AddTags(Add):
    def __init__(self, wallpaper, tags, userid, password, secure=False):
        super(AddTags, self).__init__('tags', wallpaper, tags,
            userid, password, secure)

class RejectWallpaper(Request):
    def __init__(self, wallpaper, userid, password, secure=False):
        params = None
        
        super(RejectWallpaper, self).__init__(
            'reject/wallpaper/%s/' % wallpaper,
            params,
            userid,
            password,
            secure
        )

class SendBadUrls(Request):
    def __init__(self, urls, userid, password, secure=False):
        params = [('url', url) for url in urls]

        super(SendBadUrls, self).__init__('send/bad/urls/',
            params, userid, password, secure)

class SendDuplicate(Request):
    def __init__(self, original, copy, userid, password, secure=False):
        params = {
            'original': original,
            'copy': copy
        }

        super(SendDuplicate, self).__init__('send/duplicate/',
            params, userid, password, secure)

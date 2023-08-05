# -*- coding: utf-8 -*-

import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

VERSION = '0.1'
    
setup(
    name = 'nwqt4',
    version = VERSION,
    author = 'Alexey Zotov',
    author_email = 'alexey.zotov@gmail.com',
    url = 'http://code.google.com/p/nwqt4/',
    description = 'A new-wallpaper.org client',
    license = 'GPLv2',
    packages = [
        'nwqt4',
        'nwqt4.config_dialog',
        'nwqt4.dialogs',
        'nwqt4.dialogs.request',
        'nwqt4.request_config',
        'nwqt4.widgets'
    ],
    long_description = read('README'),
    download_url = 'http://nwqt4.googlecode.com/files/nwqt4-%s.tar.gz' % VERSION,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Topic :: Desktop Environment'
    ],
    requires = [
        'PyQt4 (>=4.2)',
        'dbus (>=0.80)',
        'PIL'
    ],
    data_files = [
        (
            'bin',
            ['nwqt4/data/bin/nwqt4']
        ),
        (
            'share/applications',
            ['nwqt4/data/share/applications/new-wallpaper.desktop']
        ),
        (
            'share/icons/scalable/apps',
            ['nwqt4/data/icons/scalable/apps/new-wallpaper.svg']
        ),
        (
            'share/pixmaps',
            ['nwqt4/data/pixmaps/new-wallpaper.png']
        )
    ],
    package_data = {
        'nwqt4': [
            'data/cert/new-wallpaper.org.pem',
            'data/scripts/*',
            'data/pixmaps/*.svg',
            'data/i18n/ru/LC_MESSAGES/*.mo'
        ]
    },
    scripts = ['nwqt4/data/bin/nwqt4']
)

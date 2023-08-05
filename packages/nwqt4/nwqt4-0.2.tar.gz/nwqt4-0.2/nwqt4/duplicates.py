#       duplicates.py
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

# -*- coding: utf8 -*-

import os

from PIL import Image, ImageChops, ImageStat

import sqlite3

CREATE_STATUS = '''
CREATE TABLE IF NOT EXISTS status (
    wallpaper1 TEXT, wallpaper2 TEXT, mean REAL, stddev REAL, status INT,
    PRIMARY KEY (wallpaper1, wallpaper2)
)
'''

CREATE_STATUS_WALLPAPER1_INDEX = '''
CREATE INDEX IF NOT EXISTS status_wallpaper1 ON status (
    wallpaper1, mean, stddev, status
)
'''

CREATE_STATUS_WALLPAPER2_INDEX = '''
CREATE INDEX IF NOT EXISTS status_wallpaper2 ON status (
    wallpaper2, mean, stddev, status
)
'''

CREATE_POTENTIAL = '''
CREATE TABLE IF NOT EXISTS potential (
    wallpaper1 TEXT, wallpaper2 TEXT, mean REAL, stddev REAL,
    PRIMARY KEY (wallpaper1, wallpaper2)
)
'''

def init_db(cursor):
    cursor.execute(CREATE_STATUS)
    cursor.execute(CREATE_STATUS_WALLPAPER1_INDEX)
    cursor.execute(CREATE_STATUS_WALLPAPER2_INDEX)
    cursor.execute(CREATE_POTENTIAL)


def db_connect(appdir):
    conn = sqlite3.connect(os.path.join(appdir, 'duplicates.sqlite'))
    cursor = conn.cursor()
    init_db(cursor)
    return conn, cursor

def pair_exists(cursor, wallpaper1, wallpaper2, mean, stddev):
    cursor.execute('''
        SELECT * FROM status
        WHERE wallpaper1 = ? AND wallpaper2 = ? AND (
            (status IN (1, 2) AND mean <= ? AND stddev <= ?)
            OR
            (status = 0 AND mean >= ? AND stddev >= ?)
        )
    ''', (wallpaper1, wallpaper2, mean, stddev, mean, stddev))
    status = cursor.fetchone()
    if status:
        return True
    cursor.execute('''
        SELECT * FROM potential
        WHERE wallpaper1 = ? AND wallpaper2 = ? AND mean <= ? AND stddev <= ?
    ''', (wallpaper1, wallpaper2, mean, stddev))
    potential = cursor.fetchone()
    if potential:
        return True
    return False

def save_potential(cursor, wallpaper1, wallpaper2, mean, stddev):
    cursor.execute('''
        INSERT OR REPLACE INTO potential
        VALUES (?, ?, ?, ?)
    ''', (wallpaper1, wallpaper2, mean, stddev))

def save_not_duplicates(cursor, wallpaper1, wallpaper2, mean, stddev):
    cursor.execute('''
        INSERT OR REPLACE INTO status
        VALUES (?, ?, ?, ?, 0)
    ''', (wallpaper1, wallpaper2, mean, stddev))

def get_name_parts(name):
    name_parts = name.split('_')
    if len(name_parts) != 3: return None
    if len(name_parts[0]) != 40: return None
    for char in name_parts[0]:
        if not char in '0123456789abcdef': return None
    size = name_parts[1].split('x')
    if len(size) != 2: return None
    try:
        width = int(size[0])
        height = int(size[1])
        filesize = int(name_parts[2])
    except:
        return None
    return name_parts

def get_pairs(thumbsdir, limit=None, last_image1=None, last_image2=None):
    result = []
    listing = sorted(os.listdir(thumbsdir))
    first_iteration = True
    for file1 in listing:
        if not os.path.isfile(os.path.join(thumbsdir, file1)):
            continue
        if last_image1 and file1 < last_image1:
            continue
        if not last_image2 and file1 == last_image1:
            continue
        name1_parts = get_name_parts(file1)
        if not name1_parts:
            continue
        for file2 in listing[listing.index(file1):]:
            if file1 == file2:
                continue
            if not os.path.isfile(os.path.join(thumbsdir, file2)):
                continue
            if last_image2 and first_iteration and file2 <= last_image2:
                continue
            name2_parts = get_name_parts(file2)
            if not name2_parts or name1_parts[1] != name2_parts[1]:
                continue
            result.append((file1, file2))
            if limit and len(result) == limit: return result
        first_iteration = False
    return result

def get_diff_stats(path1, path2):
    try:
        image1 = Image.open(path1)
        image2 = Image.open(path2)
    except:
        return None
    if image1.size != image2.size:
        return None
    try:
        stats = ImageStat.Stat(ImageChops.difference(image1, image2))
    except:
        return None
    return max(stats.mean), max(stats.stddev)

def find_potentials(appdir, mean_max, stddev_max, limit=None, last_image1=None,
    last_image2=None, callback=None):

    thumbsdir = os.path.join(appdir, 'thumbs')
    pairs = get_pairs(thumbsdir, limit, last_image1, last_image2)
    if not pairs:
        return ('', '')
    conn, cursor = db_connect(appdir)
    for ind, pair in enumerate(pairs):
        if callback and ind % 10 == 0:
            callback()
        if pair_exists(cursor, pair[0], pair[1], mean_max, stddev_max):
            continue
        stats = get_diff_stats(
            os.path.join(thumbsdir, pair[0]),
            os.path.join(thumbsdir, pair[1])
        )
        if not stats:
            continue
        if stats[0] < mean_max and stats[1] < stddev_max:
            save_potential(cursor, pair[0], pair[1], mean_max, stddev_max)
        else:
            save_not_duplicates(cursor, pair[0], pair[1], mean_max, stddev_max)
    conn.commit()
    conn.close()
    if len(pairs) == limit:
        return pairs[-1]
    return ('', '')

def get_potentials(appdir, mean_max, stddev_max):
    conn, cursor = db_connect(appdir)
    cursor.execute('''
        SELECT * FROM potential
        WHERE mean <= ? AND stddev <= ?
    ''', (mean_max, stddev_max))
    result = cursor.fetchall()
    conn.close()
    return result

def save_choices(appdir, choices):
    conn, cursor = db_connect(appdir)
    for choice in choices:
        cursor.execute('''
            INSERT OR REPLACE INTO status
            VALUES (?, ?, ?, ?, ?)
        ''', choice)
        cursor.execute('''
            DELETE FROM potential
            WHERE wallpaper1 = ? AND wallpaper2 = ?
        ''', choice[:2])
    conn.commit()
    conn.close()

def get_originals(appdir, wallpapers, mean_max, stddev_max):
    conn, cursor = db_connect(appdir)
    result = {}
    for wallpaper in wallpapers:
        cursor.execute('''
            SELECT * FROM status
            WHERE
                mean <= ? AND stddev <= ? AND (
                    (wallpaper1 = ? AND status = 2)
                    OR
                    (wallpaper2 = ? AND status = 1)
                )
        ''', (mean_max, stddev_max, wallpaper, wallpaper))
        status = cursor.fetchone()
        if not status:
            continue
        result[wallpaper] = status[4] == 1 and status[0] or status[1]
    conn.close()
    return result

def delete_status(appdir, wallpaper):
    conn, cursor = db_connect(appdir)
    cursor.execute('''
        DELETE FROM status
        WHERE wallpaper1 = ? OR wallpaper2 = ?
    ''', (wallpaper, wallpaper))
    conn.commit()
    conn.close()

def set_invalid_status(appdir, wallpaper):
    conn, cursor = db_connect(appdir)
    cursor.execute('''
        UPDATE status
        SET status = 3
        WHERE wallpaper1 = ? OR wallpaper2 = ?
    ''', (wallpaper, wallpaper))

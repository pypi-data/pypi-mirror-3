#       config.py
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
import os

from PyQt4 import QtCore

class Config(QtCore.QObject):
    DATE_FMT = '%Y-%m-%d %H:%M:%S'
    
    def __init__(self, appdir):
        super(Config, self).__init__()

        self.conf = QtCore.QSettings(
            os.path.join(appdir, 'softraid-monitor.conf'),
            QtCore.QSettings.IniFormat
        )

    def read_bool(self, key, default=False):
        return self.conf.value(key, default).toBool()

    def read_int(self, key, default=0):
        return self.conf.value(key, default).toInt()[0]

    def read_float(self, key, default=0.0):
        return self.conf.value(key, default).toFloat()[0]

    def read_string(self, key, default=''):
        return unicode(self.conf.value(key, default).toString())

    def read_date(self, key, default='1970-01-01 00:00:00'):
        try:
            return datetime.datetime.strptime(
                unicode(self.conf.value(key, default).toString()),
                self.DATE_FMT
            )
        except ValueError:
            try:
                return datetime.datetime.strptime(default, self.DATE_FMT)
            except ValueError:
                return datetime.datetime.utcfromtimestamp(0)

    def write(self, key, value):
        self.conf.setValue(key, value)

    def write_date(self, key, value):
        self.write(key, value.strftime(self.DATE_FMT))

    def sync(self):
        self.conf.sync()

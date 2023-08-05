#  trayicon.py
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

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import Qt

import os

class TrayIcon(QtCore.QObject):
    settings_triggered = QtCore.pyqtSignal()
    quit_triggered = QtCore.pyqtSignal()
    
    def __init__(self):
        super(TrayIcon, self).__init__()

        self.make_icons()

        self.tray_icon = QtGui.QSystemTrayIcon(self.raid_icon)

        self.menu = QtGui.QMenu()

        self.action_settings = QtGui.QAction('Settings', self.menu)
        self.action_settings.triggered.connect(self.settings_triggered.emit)
        self.menu.addAction(self.action_settings)

        self.action_quit = QtGui.QAction('Quit', self.menu)
        self.action_quit.triggered.connect(self.quit_triggered.emit)
        self.menu.addAction(self.action_quit)

        self.tray_icon.setContextMenu(self.menu)

    def make_icons(self):
        self.hdd_icon = QtGui.QIcon.fromTheme('drive-harddisk')
        self.error_icon = QtGui.QIcon.fromTheme('dialog-error')
        self.warning_icon = QtGui.QIcon.fromTheme('dialog-warning')

        hdd_icon_size = max(self.hdd_icon.availableSizes(),
            key=lambda x: x.width())
        error_icon_size = max(self.error_icon.availableSizes(),
            key=lambda x: x.width())
        warning_icon_size = max(self.warning_icon.availableSizes(),
            key=lambda x: x.width())

        size = min((hdd_icon_size, error_icon_size, warning_icon_size),
            key=lambda x: x.width())

        hdd_pixmap = self.hdd_icon.pixmap(size)
        error_pixmap = self.error_icon.pixmap(size)
        warning_pixmap = self.warning_icon.pixmap(size)

        fill_color = QtGui.QColor(255, 255, 255, 0)
        rect = QtCore.QRect(QtCore.QPoint(), size)
        overlay_rect = QtCore.QRect(rect.center() * 2 / 3, size * 2 / 3)
        painter = QtGui.QPainter()
        pixmap = QtGui.QPixmap(size)
        
        raid_pixmap = QtGui.QPixmap(size)
        raid_pixmap.fill(fill_color)
        icon_offset = size.height() // 10
        painter.begin(raid_pixmap)
        painter.drawPixmap(rect.translated(0, icon_offset), hdd_pixmap)
        painter.drawPixmap(rect.translated(0, -icon_offset), hdd_pixmap)
        painter.end()
        self.raid_icon = QtGui.QIcon(raid_pixmap)

        pixmap.fill(fill_color)
        painter.begin(pixmap)
        painter.drawPixmap(rect, raid_pixmap)
        painter.drawPixmap(overlay_rect, error_pixmap)
        painter.end()
        self.raid_error_icon = QtGui.QIcon(pixmap)

        pixmap.fill(fill_color)
        painter.begin(pixmap)
        painter.drawPixmap(rect, raid_pixmap)
        painter.drawPixmap(overlay_rect, warning_pixmap)
        painter.end()
        self.raid_warning_icon = QtGui.QIcon(pixmap)

        pixmap.fill(fill_color)
        painter.begin(pixmap)
        painter.setOpacity(0.5)
        painter.drawPixmap(rect, raid_pixmap)
        painter.end()
        self.raid_inactive_icon = QtGui.QIcon(pixmap)

        pixmap.fill(fill_color)
        painter.begin(pixmap)
        painter.drawPixmap(rect, hdd_pixmap)
        painter.drawPixmap(overlay_rect, error_pixmap)
        painter.end()
        self.hdd_error_icon = QtGui.QIcon(pixmap)

        pixmap.fill(fill_color)
        painter.begin(pixmap)
        painter.setOpacity(0.5)
        painter.drawPixmap(rect, hdd_pixmap)
        painter.end()
        self.hdd_inactive_icon = QtGui.QIcon(pixmap)

    def save_icons(self, appdir):
        size = self.tray_icon.geometry().size() * 2

        self.save_icon(appdir, self.raid_icon.pixmap(size), 'raid.png')
        self.save_icon(appdir, self.raid_error_icon.pixmap(size),
            'raid-error.png')
        self.save_icon(appdir, self.raid_warning_icon.pixmap(size),
            'raid-warning.png')
        self.save_icon(appdir, self.raid_inactive_icon.pixmap(size),
            'raid-inactive.png')
        self.save_icon(appdir, self.hdd_icon.pixmap(size), 'hdd.png')
        self.save_icon(appdir, self.hdd_error_icon.pixmap(size),
            'hdd-error.png')
        self.save_icon(appdir, self.hdd_inactive_icon.pixmap(size),
            'hdd-inactive.png')

    def save_icon(self, appdir, pixmap, filename):
        pixmap.save(os.path.join(appdir, filename), 'PNG')

    def set_need_config(self):
        self.tray_icon.setIcon(self.warning_icon)
        self.tray_icon.setToolTip('Need to configure')

    def show(self):
        self.tray_icon.show()

    def set_device_not_found(self, device):
        self.tray_icon.setIcon(self.error_icon)
        self.tray_icon.setToolTip(
            'Device <b>%s</b> not found in /proc/mdstat' % device)

    def set_device_resync(self):
        self.tray_icon.setIcon(self.raid_warning_icon)

    def set_device_failed(self):
        self.tray_icon.setIcon(self.raid_error_icon)

    def set_device_active(self, active):
        if active:
            self.tray_icon.setIcon(self.raid_icon)
        else:
            self.tray_icon.setIcon(self.raid_inactive_icon)

    def get_size(self):
        return self.tray_icon.geometry().size()

    def set_tooltip(self, text):
        self.tray_icon.setToolTip(text)


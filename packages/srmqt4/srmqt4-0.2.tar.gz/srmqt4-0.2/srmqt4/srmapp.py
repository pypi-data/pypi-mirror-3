#  srmapp.py
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

import os

from PyQt4 import QtCore, QtGui

import config
import mdstat
import trayicon

import config_dialog

class SRMApp(QtGui.QApplication):
    def __init__(self, argv):
        super(SRMApp, self).__init__(argv)

        homedir = os.path.expanduser('~')
        xdg_config = os.getenv(
            'XDG_CONFIG_HOME',
            os.path.join(homedir, '.config')
        )
        self.appdir = os.path.join(xdg_config, 'softraid-monitor')

        for path in (xdg_config, self.appdir):
            if not os.path.isdir(path):
                os.mkdir(path)

        self.config = config.Config(self.appdir)
        self.read_config()

        self.tray_icon = trayicon.TrayIcon()
        self.tray_icon.settings_triggered.connect(self.show_settings)
        self.tray_icon.quit_triggered.connect(self.exit)

        if not self.device:
            self.tray_icon.set_need_config()
        
        self.tray_icon.show()

        self.tray_icon.save_icons(self.appdir)

        self.setQuitOnLastWindowClosed(False)

        self.raid_status = None

        self.polling_timer = self.startTimer(5000)
        self.update_status()

    def read_config(self):
        self.device = self.config.read_string('device', '')

        self.color_active = QtGui.QColor(self.config.read_string(
            'color_active', '#008000'))
        self.color_resync = QtGui.QColor(self.config.read_string(
            'color_resync', '#808000'))
        self.color_failed = QtGui.QColor(self.config.read_string(
            'color_failed', '#800000'))
        self.color_inactive = QtGui.QColor(self.config.read_string(
            'color_inactive', '#808080'))

    def show_settings(self):
        self.config_dialog = config_dialog.ConfigDialog()
        self.config_dialog.accepted.connect(self.config_dialog_accepted)

        status = mdstat.get_status()
        for device in sorted(status['devices']):
            self.config_dialog.deviceComboBox.addItem(device)

        self.config_dialog.deviceComboBox.setCurrentIndex(
            self.config_dialog.deviceComboBox.findText(self.device))

        self.config_dialog.colorActiveButton.setColor(self.color_active)
        self.config_dialog.colorResyncButton.setColor(self.color_resync)
        self.config_dialog.colorFailedButton.setColor(self.color_failed)
        self.config_dialog.colorInactiveButton.setColor(self.color_inactive)

        self.config_dialog.show()

    def config_dialog_accepted(self):
        self.device = str(self.config_dialog.deviceComboBox.currentText())
        self.config.write('device', self.device)

        if not self.device:
            self.tray_icon.set_need_config()

        self.colorActive = self.config_dialog.colorActiveButton.color()
        self.colorResync = self.config_dialog.colorResyncButton.color()
        self.colorFailed = self.config_dialog.colorFailedButton.color()
        self.colorInactive = self.config_dialog.colorInactiveButton.color()

        self.config.write('color_active', str(self.color_active.name()))
        self.config.write('color_resync', str(self.color_resync.name()))
        self.config.write('color_failed', str(self.color_failed.name()))
        self.config.write('color_inactive', str(self.color_inactive.name()))

        self.config.sync()

        self.update_status()

    def timerEvent(self, event):
        super(SRMApp, self).timerEvent(event)

        if event.timerId() == self.polling_timer:
            self.update_status()

    def update_status(self):
        self.raid_status = None

        if not self.device:
            return

        status = mdstat.get_status()

        if self.device not in status['devices']:
            return self.tray_icon.set_device_not_found(self.device)

        self.raid_status = status['devices'][self.device]

        if self.raid_status['pers'] and self.raid_status['raid']['degraded'] > 0:
            if self.raid_status['resync']['type']:
                self.tray_icon.set_device_resync()
            else:
                self.tray_icon.set_device_failed()
        else:
            self.tray_icon.set_device_active(self.raid_status['active'])

        self.update_tooltip()

    def update_tooltip(self):
        raid_icon = 'raid.png'
        if self.raid_status['active']:
            status_color = self.color_active
            pers = self.raid_status['pers']
            if self.raid_status['raid']['degraded'] > 0:
                if self.raid_status['resync']['type']:
                    raid_icon = 'raid-warning.png'
                    status_color = self.color_resync
                else:
                    raid_icon = 'raid-error.png'
                    status_color = self.color_failed
        else:
            status_color = self.color_inactive
            raid_icon = 'raid-inactive.png'
            pers = 'inactive'

        raid_icon = os.path.join(self.appdir, raid_icon)

        device_text = '<b>%s:&nbsp;<font color="%s">%s</font></b>' % (
            self.device, str(status_color.name()), pers)

        status_text = '&nbsp;'
        if self.raid_status['active']:
            status_text = '[%s/%s] [%s]' % (
                self.raid_status['raid']['total'],
                self.raid_status['raid']['nondegraded'],
                self.raid_status['raid']['status']
            )

        size = self.tray_icon.get_size() * 2

        disk_rows = []
        
        for disk_number in sorted(self.raid_status['disks']):
            hdd_icon = 'hdd.png'
            disk_status = ''
            status_color = self.color_active
            disk_type = self.raid_status['disks'][disk_number]['type']

            if disk_type.startswith('(W)'):
                disk_status = 'w.m. '
                disk_type = disk_type[3:]

            if disk_type == '(S)':
                hdd_icon = 'hdd-inactive.png'
                disk_status += 'spare'
                status_color = self.color_inactive
            elif disk_type == '(F)':
                hdd_icon = 'hdd-error.png'
                disk_status += 'failed'
                status_color = self.color_failed
            else:
                disk_status += 'active'

            hdd_icon = os.path.join(self.appdir, hdd_icon)

            disk_name = self.raid_status['disks'][disk_number]['name']

            disk_line = '%s: <font color="%s">%s</font>' % (
                disk_name,
                str(status_color.name()),
                disk_status
            )

            disk_row = '''<tr>
                <td align="right" align="center" valign="middle">
                    <img width="%(width)d" height="%(height)d" src="%(hdd_icon)s">
                </td>
                <td align="center" valign="middle">%(disk_line)s</td>
            </tr>'''

            params = {
                'width': 3 * size.width() // 4,
                'height': 3 * size.height() // 4,
                'hdd_icon': hdd_icon,
                'disk_line': disk_line
            }

            disk_rows.append(disk_row % params)

        resync_type = self.raid_status['resync']['type']
        if resync_type:
            lines = []
            
            percent = self.raid_status['resync'].get('percent', -1)
            if percent >= 1:
                percent_text = '''<tr><td colspan="2">
                    <table cellspacing="0" cellpadding="0" border="1" style="border-style: solid;" width="100%%"><tr><td>
                    <table cellspacing="0"><tr><td bgcolor="%(color)s" width="%(percent)d%%">
                        &nbsp;
                    </td></tr></table>
                    </td></tr></table>
                </td></tr>''' % {
                    'color': str(self.color_resync.name()),
                    'percent': percent
                }
                lines.append(percent_text)

            row_template = '<tr><td align="center" colspan="2">%s</td></tr>'

            finish_text = 'finish: %s' % self.raid_status['resync']['finish']
            lines.append(row_template % finish_text)

            speed = self.raid_status['resync'].get('speed')
            if speed:
                speed_text = 'speed: %s' % speed
                lines.append(row_template % speed_text)

            
            resync_text = ''.join(lines)
            

        tooltip = '''<table cellpadding="3" style="margin: 5 15 5 5;">
            <tr>
                <td rowspan="2" valign="middle">
                    <img width="%(width)d" height="%(height)d" src="%(raid_icon)s">
                </td>
                <td align="center" valign="middle">%(device)s</td>
            </tr>
            <tr>
                <td align="center">%(status)s</td>
            </tr>
            %(disks)s
            %(resync)s
        </table>
        '''

        params = {
            'width': size.width(),
            'height': size.height(),
            'raid_icon': raid_icon,
            'device': device_text,
            'status': status_text,
            'disks': ''.join(disk_rows),
            'resync': resync_type and resync_text
        }

        tooltip = tooltip % params

        self.tray_icon.set_tooltip(tooltip)

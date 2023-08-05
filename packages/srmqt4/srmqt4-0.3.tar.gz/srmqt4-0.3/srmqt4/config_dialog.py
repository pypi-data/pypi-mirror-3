#  config_dialog.py
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

import config_dialog_ui

import color_button

class ConfigDialog(QtGui.QDialog, config_dialog_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setupUi(self)

        self.colorActiveButton = color_button.ColorButton()
        self.colorActiveLayout.addWidget(self.colorActiveButton)

        self.colorResyncButton = color_button.ColorButton()
        self.colorResyncLayout.addWidget(self.colorResyncButton)

        self.colorFailedButton = color_button.ColorButton()
        self.colorFailedLayout.addWidget(self.colorFailedButton)

        self.colorInactiveButton = color_button.ColorButton()
        self.colorInactiveLayout.addWidget(self.colorInactiveButton)

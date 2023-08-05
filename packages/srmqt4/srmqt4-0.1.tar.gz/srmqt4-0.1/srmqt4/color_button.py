#       color_button.py
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

class ColorButton(QtGui.QPushButton):
    def __init__(self, parent=None):
        super(ColorButton, self).__init__(parent)
        self._color = QtGui.QColor()

    def color(self):
        return self._color

    def setColor(self, color):
        self._color = color
        self.update()

    def paintEvent(self, event):
        super(ColorButton, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.fillRect(
            event.rect().adjusted(5, 5, -5, -5),
            QtGui.QBrush(self._color)
        )

    def mouseReleaseEvent(self, event):
        super(ColorButton, self).mouseReleaseEvent(event)
        self._color_dialog = QtGui.QColorDialog(self._color)
        self._color_dialog.colorSelected.connect(self.setColor)
        self._color_dialog.exec_()

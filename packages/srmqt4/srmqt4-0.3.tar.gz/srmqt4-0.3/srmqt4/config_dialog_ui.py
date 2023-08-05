# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_dialog.ui'
#
# Created: Mon Nov 14 19:22:55 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(244, 264)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.deviceLayout = QtGui.QHBoxLayout()
        self.deviceLayout.setObjectName(_fromUtf8("deviceLayout"))
        self.deviceLabel = QtGui.QLabel(Dialog)
        self.deviceLabel.setText(QtGui.QApplication.translate("Dialog", "Device", None, QtGui.QApplication.UnicodeUTF8))
        self.deviceLabel.setObjectName(_fromUtf8("deviceLabel"))
        self.deviceLayout.addWidget(self.deviceLabel)
        self.deviceComboBox = QtGui.QComboBox(Dialog)
        self.deviceComboBox.setObjectName(_fromUtf8("deviceComboBox"))
        self.deviceLayout.addWidget(self.deviceComboBox)
        self.verticalLayout.addLayout(self.deviceLayout)
        self.pollingLayout = QtGui.QHBoxLayout()
        self.pollingLayout.setObjectName(_fromUtf8("pollingLayout"))
        self.pollingLabel = QtGui.QLabel(Dialog)
        self.pollingLabel.setText(QtGui.QApplication.translate("Dialog", "Polling interval", None, QtGui.QApplication.UnicodeUTF8))
        self.pollingLabel.setObjectName(_fromUtf8("pollingLabel"))
        self.pollingLayout.addWidget(self.pollingLabel)
        self.pollingSpinBox = QtGui.QSpinBox(Dialog)
        self.pollingSpinBox.setSuffix(QtGui.QApplication.translate("Dialog", " sec", None, QtGui.QApplication.UnicodeUTF8))
        self.pollingSpinBox.setMinimum(1)
        self.pollingSpinBox.setMaximum(60)
        self.pollingSpinBox.setProperty("value", 5)
        self.pollingSpinBox.setObjectName(_fromUtf8("pollingSpinBox"))
        self.pollingLayout.addWidget(self.pollingSpinBox)
        self.verticalLayout.addLayout(self.pollingLayout)
        self.colorActiveLayout = QtGui.QHBoxLayout()
        self.colorActiveLayout.setObjectName(_fromUtf8("colorActiveLayout"))
        self.colorActiveLabel = QtGui.QLabel(Dialog)
        self.colorActiveLabel.setText(QtGui.QApplication.translate("Dialog", "Active color", None, QtGui.QApplication.UnicodeUTF8))
        self.colorActiveLabel.setObjectName(_fromUtf8("colorActiveLabel"))
        self.colorActiveLayout.addWidget(self.colorActiveLabel)
        self.verticalLayout.addLayout(self.colorActiveLayout)
        self.colorResyncLayout = QtGui.QHBoxLayout()
        self.colorResyncLayout.setObjectName(_fromUtf8("colorResyncLayout"))
        self.colorResyncLabel = QtGui.QLabel(Dialog)
        self.colorResyncLabel.setText(QtGui.QApplication.translate("Dialog", "Resync color", None, QtGui.QApplication.UnicodeUTF8))
        self.colorResyncLabel.setObjectName(_fromUtf8("colorResyncLabel"))
        self.colorResyncLayout.addWidget(self.colorResyncLabel)
        self.verticalLayout.addLayout(self.colorResyncLayout)
        self.colorFailedLayout = QtGui.QHBoxLayout()
        self.colorFailedLayout.setObjectName(_fromUtf8("colorFailedLayout"))
        self.colorFailedLabel = QtGui.QLabel(Dialog)
        self.colorFailedLabel.setText(QtGui.QApplication.translate("Dialog", "Failed color", None, QtGui.QApplication.UnicodeUTF8))
        self.colorFailedLabel.setObjectName(_fromUtf8("colorFailedLabel"))
        self.colorFailedLayout.addWidget(self.colorFailedLabel)
        self.verticalLayout.addLayout(self.colorFailedLayout)
        self.colorInactiveLayout = QtGui.QHBoxLayout()
        self.colorInactiveLayout.setObjectName(_fromUtf8("colorInactiveLayout"))
        self.colorInactiveLabel = QtGui.QLabel(Dialog)
        self.colorInactiveLabel.setText(QtGui.QApplication.translate("Dialog", "Inactive color", None, QtGui.QApplication.UnicodeUTF8))
        self.colorInactiveLabel.setObjectName(_fromUtf8("colorInactiveLabel"))
        self.colorInactiveLayout.addWidget(self.colorInactiveLabel)
        self.verticalLayout.addLayout(self.colorInactiveLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass


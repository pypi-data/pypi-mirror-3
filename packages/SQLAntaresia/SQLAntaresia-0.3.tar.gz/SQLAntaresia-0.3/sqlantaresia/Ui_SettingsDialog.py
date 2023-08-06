# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sqlantaresia/SettingsDialog.ui'
#
# Created: Tue Mar 20 12:06:34 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        SettingsDialog.setObjectName(_fromUtf8("SettingsDialog"))
        SettingsDialog.resize(400, 298)
        self.verticalLayout = QtGui.QVBoxLayout(SettingsDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(SettingsDialog)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        self.tab.setObjectName(_fromUtf8("tab"))
        self.formLayout = QtGui.QFormLayout(self.tab)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFont = QtGui.QLabel(self.tab)
        self.lblFont.setObjectName(_fromUtf8("lblFont"))
        self.horizontalLayout.addWidget(self.lblFont)
        self.lblSelectedFont = QtGui.QLabel(self.tab)
        self.lblSelectedFont.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblSelectedFont.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblSelectedFont.setObjectName(_fromUtf8("lblSelectedFont"))
        self.horizontalLayout.addWidget(self.lblSelectedFont)
        self.btnFont = QtGui.QToolButton(self.tab)
        self.btnFont.setObjectName(_fromUtf8("btnFont"))
        self.horizontalLayout.addWidget(self.btnFont)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)
        self.buttonBox = QtGui.QDialogButtonBox(SettingsDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)
        self.lblSelectedFont.setBuddy(self.btnFont)

        self.retranslateUi(SettingsDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SettingsDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SettingsDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsDialog)
        SettingsDialog.setTabOrder(self.tabWidget, self.btnFont)
        SettingsDialog.setTabOrder(self.btnFont, self.buttonBox)

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QtGui.QApplication.translate("SettingsDialog", "Settings", None, QtGui.QApplication.UnicodeUTF8))
        self.lblFont.setText(QtGui.QApplication.translate("SettingsDialog", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.lblSelectedFont.setText(QtGui.QApplication.translate("SettingsDialog", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.btnFont.setText(QtGui.QApplication.translate("SettingsDialog", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("SettingsDialog", "Query Editor", None, QtGui.QApplication.UnicodeUTF8))


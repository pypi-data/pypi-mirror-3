# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Tab.ui'
#
# Created: Fri May 20 18:24:01 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Tab(object):
    def setupUi(self, Tab):
        Tab.setObjectName(_fromUtf8("Tab"))
        Tab.resize(700, 326)
        self.verticalLayout = QtGui.QVBoxLayout(Tab)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.layoutConnectionBar = QtGui.QHBoxLayout()
        self.layoutConnectionBar.setSpacing(0)
        self.layoutConnectionBar.setObjectName(_fromUtf8("layoutConnectionBar"))
        self.lblConnection = QtGui.QLabel(Tab)
        self.lblConnection.setObjectName(_fromUtf8("lblConnection"))
        self.layoutConnectionBar.addWidget(self.lblConnection)
        self.cmbConnection = QtGui.QComboBox(Tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cmbConnection.sizePolicy().hasHeightForWidth())
        self.cmbConnection.setSizePolicy(sizePolicy)
        self.cmbConnection.setEditable(True)
        self.cmbConnection.setObjectName(_fromUtf8("cmbConnection"))
        self.layoutConnectionBar.addWidget(self.cmbConnection)
        self.btnGo = QtGui.QToolButton(Tab)
        self.btnGo.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/16/icons/system-run.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnGo.setIcon(icon)
        self.btnGo.setAutoRaise(True)
        self.btnGo.setObjectName(_fromUtf8("btnGo"))
        self.layoutConnectionBar.addWidget(self.btnGo)
        self.verticalLayout.addLayout(self.layoutConnectionBar)
        self.frmTabContent = QtGui.QFrame(Tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmTabContent.sizePolicy().hasHeightForWidth())
        self.frmTabContent.setSizePolicy(sizePolicy)
        self.frmTabContent.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmTabContent.setFrameShadow(QtGui.QFrame.Raised)
        self.frmTabContent.setObjectName(_fromUtf8("frmTabContent"))
        self.verticalLayout.addWidget(self.frmTabContent)
        self.lblConnection.setBuddy(self.cmbConnection)

        self.retranslateUi(Tab)
        QtCore.QMetaObject.connectSlotsByName(Tab)

    def retranslateUi(self, Tab):
        Tab.setWindowTitle(QtGui.QApplication.translate("Tab", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.lblConnection.setText(QtGui.QApplication.translate("Tab", "Connection string:", None, QtGui.QApplication.UnicodeUTF8))
        self.cmbConnection.setStatusTip(QtGui.QApplication.translate("Tab", "Connection string: Can be either a connection name or an URI of the type \"username:password@hostname[:port]\"", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc

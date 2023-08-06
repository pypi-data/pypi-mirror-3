# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sqlantaresia/ConnectionsDialog.ui'
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

class Ui_ConnectionsDialog(object):
    def setupUi(self, ConnectionsDialog):
        ConnectionsDialog.setObjectName(_fromUtf8("ConnectionsDialog"))
        ConnectionsDialog.resize(372, 355)
        self.gridLayout = QtGui.QGridLayout(ConnectionsDialog)
        self.gridLayout.setContentsMargins(4, 4, 3, 3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.listConnections = QtGui.QListView(ConnectionsDialog)
        self.listConnections.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.listConnections.setObjectName(_fromUtf8("listConnections"))
        self.gridLayout.addWidget(self.listConnections, 0, 0, 5, 1)
        self.btnAdd = QtGui.QPushButton(ConnectionsDialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/16/icons/list-add.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAdd.setIcon(icon)
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.gridLayout.addWidget(self.btnAdd, 0, 1, 1, 1)
        self.btnProps = QtGui.QPushButton(ConnectionsDialog)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/16/icons/document-properties.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnProps.setIcon(icon1)
        self.btnProps.setObjectName(_fromUtf8("btnProps"))
        self.gridLayout.addWidget(self.btnProps, 1, 1, 1, 1)
        self.btnDel = QtGui.QPushButton(ConnectionsDialog)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/16/icons/list-remove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnDel.setIcon(icon2)
        self.btnDel.setObjectName(_fromUtf8("btnDel"))
        self.gridLayout.addWidget(self.btnDel, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(23, 230, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.btnClose = QtGui.QPushButton(ConnectionsDialog)
        self.btnClose.setObjectName(_fromUtf8("btnClose"))
        self.gridLayout.addWidget(self.btnClose, 4, 1, 1, 1)

        self.retranslateUi(ConnectionsDialog)
        QtCore.QObject.connect(self.btnClose, QtCore.SIGNAL(_fromUtf8("clicked()")), ConnectionsDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ConnectionsDialog)
        ConnectionsDialog.setTabOrder(self.listConnections, self.btnAdd)
        ConnectionsDialog.setTabOrder(self.btnAdd, self.btnProps)
        ConnectionsDialog.setTabOrder(self.btnProps, self.btnDel)

    def retranslateUi(self, ConnectionsDialog):
        ConnectionsDialog.setWindowTitle(QtGui.QApplication.translate("ConnectionsDialog", "Connections", None, QtGui.QApplication.UnicodeUTF8))
        self.btnAdd.setText(QtGui.QApplication.translate("ConnectionsDialog", "&Add", None, QtGui.QApplication.UnicodeUTF8))
        self.btnProps.setText(QtGui.QApplication.translate("ConnectionsDialog", "&Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.btnDel.setText(QtGui.QApplication.translate("ConnectionsDialog", "&Remove", None, QtGui.QApplication.UnicodeUTF8))
        self.btnClose.setText(QtGui.QApplication.translate("ConnectionsDialog", "&Close", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc

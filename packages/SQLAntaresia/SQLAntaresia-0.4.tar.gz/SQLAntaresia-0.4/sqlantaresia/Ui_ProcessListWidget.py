# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sqlantaresia/ProcessListWidget.ui'
#
# Created: Mon Apr  2 11:56:42 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_ProcessListWidget(object):
    def setupUi(self, ProcessListWidget):
        ProcessListWidget.setObjectName(_fromUtf8("ProcessListWidget"))
        ProcessListWidget.resize(513, 449)
        self.verticalLayout = QtGui.QVBoxLayout(ProcessListWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.chkAutoRefresh = QtGui.QCheckBox(ProcessListWidget)
        self.chkAutoRefresh.setObjectName(_fromUtf8("chkAutoRefresh"))
        self.horizontalLayout.addWidget(self.chkAutoRefresh)
        self.spinSeconds = QtGui.QSpinBox(ProcessListWidget)
        self.spinSeconds.setMinimum(1)
        self.spinSeconds.setProperty("value", 2)
        self.spinSeconds.setObjectName(_fromUtf8("spinSeconds"))
        self.horizontalLayout.addWidget(self.spinSeconds)
        self.lblRefreshUnit = QtGui.QLabel(ProcessListWidget)
        self.lblRefreshUnit.setObjectName(_fromUtf8("lblRefreshUnit"))
        self.horizontalLayout.addWidget(self.lblRefreshUnit)
        spacerItem = QtGui.QSpacerItem(288, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnRefresh = QtGui.QPushButton(ProcessListWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/16/icons/view-refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRefresh.setIcon(icon)
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.horizontalLayout.addWidget(self.btnRefresh)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableProcessList = QtGui.QTableView(ProcessListWidget)
        self.tableProcessList.setObjectName(_fromUtf8("tableProcessList"))
        self.verticalLayout.addWidget(self.tableProcessList)

        self.retranslateUi(ProcessListWidget)
        QtCore.QMetaObject.connectSlotsByName(ProcessListWidget)

    def retranslateUi(self, ProcessListWidget):
        ProcessListWidget.setWindowTitle(QtGui.QApplication.translate("ProcessListWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAutoRefresh.setText(QtGui.QApplication.translate("ProcessListWidget", "Auto refresh every", None, QtGui.QApplication.UnicodeUTF8))
        self.lblRefreshUnit.setText(QtGui.QApplication.translate("ProcessListWidget", "seconds", None, QtGui.QApplication.UnicodeUTF8))
        self.btnRefresh.setText(QtGui.QApplication.translate("ProcessListWidget", "&Refresh", None, QtGui.QApplication.UnicodeUTF8))

import icons_rc

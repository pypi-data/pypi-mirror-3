# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'DBTabContainer.ui'
#
# Created: Fri May 20 18:24:00 2011
#      by: PyQt4 UI code generator 4.8.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_DBTabContainer(object):
    def setupUi(self, DBTabContainer):
        DBTabContainer.setObjectName(_fromUtf8("DBTabContainer"))
        DBTabContainer.resize(863, 500)
        self.gridLayout = QtGui.QGridLayout(DBTabContainer)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.splitter = QtGui.QSplitter(DBTabContainer)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.grpDatabases = QtGui.QGroupBox(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.grpDatabases.sizePolicy().hasHeightForWidth())
        self.grpDatabases.setSizePolicy(sizePolicy)
        self.grpDatabases.setMaximumSize(QtCore.QSize(500, 16777215))
        self.grpDatabases.setObjectName(_fromUtf8("grpDatabases"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.grpDatabases)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.treeView_2 = QtGui.QTreeView(self.grpDatabases)
        self.treeView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_2.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.treeView_2.setRootIsDecorated(False)
        self.treeView_2.setHeaderHidden(True)
        self.treeView_2.setObjectName(_fromUtf8("treeView_2"))
        self.verticalLayout_2.addWidget(self.treeView_2)
        self.frmContent = QtGui.QFrame(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frmContent.sizePolicy().hasHeightForWidth())
        self.frmContent.setSizePolicy(sizePolicy)
        self.frmContent.setFrameShape(QtGui.QFrame.NoFrame)
        self.frmContent.setFrameShadow(QtGui.QFrame.Raised)
        self.frmContent.setObjectName(_fromUtf8("frmContent"))
        self.gridLayout.addWidget(self.splitter, 0, 0, 1, 1)

        self.retranslateUi(DBTabContainer)
        QtCore.QMetaObject.connectSlotsByName(DBTabContainer)

    def retranslateUi(self, DBTabContainer):
        DBTabContainer.setWindowTitle(QtGui.QApplication.translate("DBTabContainer", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.grpDatabases.setTitle(QtGui.QApplication.translate("DBTabContainer", "Databases", None, QtGui.QApplication.UnicodeUTF8))


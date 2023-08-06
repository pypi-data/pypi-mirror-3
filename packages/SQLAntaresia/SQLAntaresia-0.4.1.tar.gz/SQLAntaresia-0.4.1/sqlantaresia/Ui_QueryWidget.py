# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sqlantaresia/QueryWidget.ui'
#
# Created: Mon Apr  2 15:36:41 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_QueryWidget(object):
    def setupUi(self, QueryWidget):
        QueryWidget.setObjectName(_fromUtf8("QueryWidget"))
        QueryWidget.resize(513, 449)
        self.verticalLayout_2 = QtGui.QVBoxLayout(QueryWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitter = QtGui.QSplitter(QueryWidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layoutWidget = QtGui.QWidget(self.splitter)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.txtQuery = Qsci.QsciScintilla(self.layoutWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtQuery.sizePolicy().hasHeightForWidth())
        self.txtQuery.setSizePolicy(sizePolicy)
        self.txtQuery.setMinimumSize(QtCore.QSize(0, 100))
        self.txtQuery.setBaseSize(QtCore.QSize(0, 100))
        self.txtQuery.setToolTip(_fromUtf8(""))
        self.txtQuery.setWhatsThis(_fromUtf8(""))
        self.txtQuery.setObjectName(_fromUtf8("txtQuery"))
        self.verticalLayout.addWidget(self.txtQuery)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.labelQueryError = QtGui.QLabel(self.layoutWidget)
        self.labelQueryError.setText(_fromUtf8(""))
        self.labelQueryError.setObjectName(_fromUtf8("labelQueryError"))
        self.horizontalLayout.addWidget(self.labelQueryError)
        spacerItem = QtGui.QSpacerItem(288, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.labelQueryTime = QtGui.QLabel(self.layoutWidget)
        self.labelQueryTime.setText(_fromUtf8(""))
        self.labelQueryTime.setObjectName(_fromUtf8("labelQueryTime"))
        self.horizontalLayout.addWidget(self.labelQueryTime)
        self.btnExecuteQuery = QtGui.QPushButton(self.layoutWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/16/icons/system-run.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnExecuteQuery.setIcon(icon)
        self.btnExecuteQuery.setObjectName(_fromUtf8("btnExecuteQuery"))
        self.horizontalLayout.addWidget(self.btnExecuteQuery)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.tableQueryResult = QtGui.QTableView(self.splitter)
        self.tableQueryResult.setObjectName(_fromUtf8("tableQueryResult"))
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(QueryWidget)
        QtCore.QMetaObject.connectSlotsByName(QueryWidget)

    def retranslateUi(self, QueryWidget):
        QueryWidget.setWindowTitle(QtGui.QApplication.translate("QueryWidget", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.btnExecuteQuery.setText(QtGui.QApplication.translate("QueryWidget", "&Execute", None, QtGui.QApplication.UnicodeUTF8))

from PyQt4 import Qsci
import icons_rc

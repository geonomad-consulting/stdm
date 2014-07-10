# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_content_auth.ui'
#
# Created: Thu Jul 10 14:50:57 2014
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_frmContentAuth(object):
    def setupUi(self, frmContentAuth):
        frmContentAuth.setObjectName(_fromUtf8("frmContentAuth"))
        frmContentAuth.resize(644, 437)
        self.gridLayout_3 = QtGui.QGridLayout(frmContentAuth)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.label = QtGui.QLabel(frmContentAuth)
        self.label.setWordWrap(True)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 2)
        self.groupBox = QtGui.QGroupBox(frmContentAuth)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.tbContentItems = QtGui.QTabWidget(self.groupBox)
        self.tbContentItems.setObjectName(_fromUtf8("tbContentItems"))
        self.gridLayout_2.addWidget(self.tbContentItems, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox, 1, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(frmContentAuth)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lstRoles = QtGui.QListView(self.groupBox_2)
        self.lstRoles.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstRoles.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.lstRoles.setObjectName(_fromUtf8("lstRoles"))
        self.gridLayout.addWidget(self.lstRoles, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.groupBox_2, 1, 1, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(frmContentAuth)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout_3.addWidget(self.buttonBox, 2, 1, 1, 1)

        self.retranslateUi(frmContentAuth)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), frmContentAuth.reject)
        QtCore.QMetaObject.connectSlotsByName(frmContentAuth)

    def retranslateUi(self, frmContentAuth):
        frmContentAuth.setWindowTitle(_translate("frmContentAuth", "Content Authorization", None))
        self.label.setText(_translate("frmContentAuth", "<html><head/><body><p>Click on a content item in the table on the left-hand side and check/uncheck to approve/disapprove the authorised roles on the table in the right-hand side below.</p></body></html>", None))
        self.groupBox.setTitle(_translate("frmContentAuth", "Content Items", None))
        self.groupBox_2.setTitle(_translate("frmContentAuth", "Roles", None))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_attribute_browser.ui'
#
# Created: Fri Jun 19 10:56:57 2015
#      by: PyQt4 UI code generator 4.11.1
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

class Ui_AttribBrowser(object):
    def setupUi(self, AttribBrowser):
        AttribBrowser.setObjectName(_fromUtf8("AttribBrowser"))
        AttribBrowser.resize(412, 40)
        AttribBrowser.setMaximumSize(QtCore.QSize(16777215, 40))
        self.gridLayout = QtGui.QGridLayout(AttribBrowser)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.txt_attribute = QtGui.QLineEdit(AttribBrowser)
        self.txt_attribute.setObjectName(_fromUtf8("txt_attribute"))
        self.horizontalLayout.addWidget(self.txt_attribute)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.btn_browse = QtGui.QPushButton(AttribBrowser)
        self.btn_browse.setMaximumSize(QtCore.QSize(30, 20))
        self.btn_browse.setText(_fromUtf8(""))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/stdm/images/icons/table.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btn_browse.setIcon(icon)
        self.btn_browse.setFlat(True)
        self.btn_browse.setObjectName(_fromUtf8("btn_browse"))
        self.gridLayout.addWidget(self.btn_browse, 0, 1, 1, 1)

        self.retranslateUi(AttribBrowser)
        QtCore.QMetaObject.connectSlotsByName(AttribBrowser)

    def retranslateUi(self, AttribBrowser):
        AttribBrowser.setWindowTitle(_translate("AttribBrowser", "Form", None))

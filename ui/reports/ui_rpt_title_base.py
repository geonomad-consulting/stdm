# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_rptTitleBase.ui'
#
# Created: Thu Sep 29 18:47:37 2011
#      by: PyQt4 UI code generator 4.7.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from qgis.gui import QgsColorButton

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_frmRptTitleBase(object):
    def setupUi(self, frmRptTitleBase):
        frmRptTitleBase.setObjectName(_fromUtf8("frmRptTitleBase"))
        frmRptTitleBase.resize(347, 495)
        self.gridLayout = QtGui.QGridLayout(frmRptTitleBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.scrollArea = QtGui.QScrollArea(frmRptTitleBase)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.scrollAreaWidgetContents = QtGui.QWidget(self.scrollArea)
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 327, 475))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.verticalLayout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label_10 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_10.setObjectName(_fromUtf8("label_10"))
        self.verticalLayout.addWidget(self.label_10)
        self.cboBorder = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.cboBorder.setObjectName(_fromUtf8("cboBorder"))
        self.cboBorder.addItem(_fromUtf8(""))
        self.cboBorder.addItem(_fromUtf8(""))
        self.cboBorder.addItem(_fromUtf8(""))
        self.cboBorder.addItem(_fromUtf8(""))
        self.cboBorder.addItem(_fromUtf8(""))
        self.cboBorder.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.cboBorder)
        self.label = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.btnTitleColor = QgsColorButton(self.scrollAreaWidgetContents)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnTitleColor.sizePolicy().hasHeightForWidth())
        self.btnTitleColor.setSizePolicy(sizePolicy)
        self.btnTitleColor.setMinimumSize(QtCore.QSize(32, 0))
        self.btnTitleColor.setMaximumSize(QtCore.QSize(1000, 16777215))
        self.btnTitleColor.setText(_fromUtf8(""))
        self.btnTitleColor.setObjectName(_fromUtf8("btnTitleColor"))
        self.verticalLayout.addWidget(self.btnTitleColor)
        self.label_2 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.verticalLayout.addWidget(self.label_2)
        self.btnTitleFont = QtGui.QPushButton(self.scrollAreaWidgetContents)
        self.btnTitleFont.setObjectName(_fromUtf8("btnTitleFont"))
        self.verticalLayout.addWidget(self.btnTitleFont)
        self.label_3 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout.addWidget(self.label_3)
        self.txtTitleHeight = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.txtTitleHeight.setObjectName(_fromUtf8("txtTitleHeight"))
        self.verticalLayout.addWidget(self.txtTitleHeight)
        self.label_4 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.verticalLayout.addWidget(self.label_4)
        self.cboTitleHAlign = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.cboTitleHAlign.setObjectName(_fromUtf8("cboTitleHAlign"))
        self.cboTitleHAlign.addItem(_fromUtf8(""))
        self.cboTitleHAlign.addItem(_fromUtf8(""))
        self.cboTitleHAlign.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.cboTitleHAlign)
        self.label_5 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.verticalLayout.addWidget(self.label_5)
        self.txtTitleLeft = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.txtTitleLeft.setObjectName(_fromUtf8("txtTitleLeft"))
        self.verticalLayout.addWidget(self.txtTitleLeft)
        self.label_6 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.verticalLayout.addWidget(self.label_6)
        self.txtTitleText = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.txtTitleText.setObjectName(_fromUtf8("txtTitleText"))
        self.verticalLayout.addWidget(self.txtTitleText)
        self.label_7 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.verticalLayout.addWidget(self.label_7)
        self.txtTitleTop = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.txtTitleTop.setObjectName(_fromUtf8("txtTitleTop"))
        self.verticalLayout.addWidget(self.txtTitleTop)
        self.label_8 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.verticalLayout.addWidget(self.label_8)
        self.cboTitleVAlign = QtGui.QComboBox(self.scrollAreaWidgetContents)
        self.cboTitleVAlign.setObjectName(_fromUtf8("cboTitleVAlign"))
        self.cboTitleVAlign.addItem(_fromUtf8(""))
        self.cboTitleVAlign.addItem(_fromUtf8(""))
        self.cboTitleVAlign.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.cboTitleVAlign)
        self.label_9 = QtGui.QLabel(self.scrollAreaWidgetContents)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.verticalLayout.addWidget(self.label_9)
        self.txtTitleWidth = QtGui.QLineEdit(self.scrollAreaWidgetContents)
        self.txtTitleWidth.setObjectName(_fromUtf8("txtTitleWidth"))
        self.verticalLayout.addWidget(self.txtTitleWidth)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.gridLayout.addWidget(self.scrollArea, 0, 0, 1, 1)

        self.retranslateUi(frmRptTitleBase)
        QtCore.QMetaObject.connectSlotsByName(frmRptTitleBase)

    def retranslateUi(self, frmRptTitleBase):
        frmRptTitleBase.setWindowTitle(QtGui.QApplication.translate("frmRptTitleBase", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_10.setText(QtGui.QApplication.translate("frmRptTitleBase", "Border", None, QtGui.QApplication.UnicodeUTF8))
        self.cboBorder.setItemText(0, QtGui.QApplication.translate("frmRptTitleBase", "None", None, QtGui.QApplication.UnicodeUTF8))
        self.cboBorder.setItemText(1, QtGui.QApplication.translate("frmRptTitleBase", "All", None, QtGui.QApplication.UnicodeUTF8))
        self.cboBorder.setItemText(2, QtGui.QApplication.translate("frmRptTitleBase", "Top", None, QtGui.QApplication.UnicodeUTF8))
        self.cboBorder.setItemText(3, QtGui.QApplication.translate("frmRptTitleBase", "Right", None, QtGui.QApplication.UnicodeUTF8))
        self.cboBorder.setItemText(4, QtGui.QApplication.translate("frmRptTitleBase", "Bottom", None, QtGui.QApplication.UnicodeUTF8))
        self.cboBorder.setItemText(5, QtGui.QApplication.translate("frmRptTitleBase", "Left", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("frmRptTitleBase", "Fore Color", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("frmRptTitleBase", "Font", None, QtGui.QApplication.UnicodeUTF8))
        self.btnTitleFont.setText(QtGui.QApplication.translate("frmRptTitleBase", "Select Font...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("frmRptTitleBase", "Height (cm)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("frmRptTitleBase", "Horizontal Alignment", None, QtGui.QApplication.UnicodeUTF8))
        self.cboTitleHAlign.setItemText(0, QtGui.QApplication.translate("frmRptTitleBase", "Left", None, QtGui.QApplication.UnicodeUTF8))
        self.cboTitleHAlign.setItemText(1, QtGui.QApplication.translate("frmRptTitleBase", "Right", None, QtGui.QApplication.UnicodeUTF8))
        self.cboTitleHAlign.setItemText(2, QtGui.QApplication.translate("frmRptTitleBase", "Center", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("frmRptTitleBase", "Left (cm)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("frmRptTitleBase", "Text", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("frmRptTitleBase", "Top (cm)", None, QtGui.QApplication.UnicodeUTF8))
        self.label_8.setText(QtGui.QApplication.translate("frmRptTitleBase", "Vertical Alignment", None, QtGui.QApplication.UnicodeUTF8))
        self.cboTitleVAlign.setItemText(0, QtGui.QApplication.translate("frmRptTitleBase", "Top", None, QtGui.QApplication.UnicodeUTF8))
        self.cboTitleVAlign.setItemText(1, QtGui.QApplication.translate("frmRptTitleBase", "Middle", None, QtGui.QApplication.UnicodeUTF8))
        self.cboTitleVAlign.setItemText(2, QtGui.QApplication.translate("frmRptTitleBase", "Bottom", None, QtGui.QApplication.UnicodeUTF8))
        self.label_9.setText(QtGui.QApplication.translate("frmRptTitleBase", "Width (cm)", None, QtGui.QApplication.UnicodeUTF8))



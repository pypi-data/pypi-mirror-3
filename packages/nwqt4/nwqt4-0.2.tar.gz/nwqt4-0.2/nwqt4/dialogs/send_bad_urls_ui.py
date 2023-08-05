# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/send_bad_urls.ui'
#
# Created: Sun Oct 30 15:40:37 2011
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
        Dialog.resize(550, 80)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Send bad urls", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.urls = QtGui.QScrollArea(Dialog)
        self.urls.setWidgetResizable(True)
        self.urls.setObjectName(_fromUtf8("urls"))
        self.urlsContents = QtGui.QWidget()
        self.urlsContents.setGeometry(QtCore.QRect(0, 0, 530, 26))
        self.urlsContents.setObjectName(_fromUtf8("urlsContents"))
        self.formLayout = QtGui.QFormLayout(self.urlsContents)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setHorizontalSpacing(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.urls.setWidget(self.urlsContents)
        self.verticalLayout.addWidget(self.urls)
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
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(_('OK'))
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setText(_('Cancel'))

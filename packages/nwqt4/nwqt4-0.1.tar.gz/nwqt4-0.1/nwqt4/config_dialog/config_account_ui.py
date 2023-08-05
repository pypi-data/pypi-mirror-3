# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_account.ui'
#
# Created: Sun Oct 10 15:47:10 2010
#      by: PyQt4 UI code generator 4.7.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(466, 168)
        Form.setMinimumSize(QtCore.QSize(300, 0))
        self.formGrid = QtGui.QGridLayout(Form)
        self.formGrid.setObjectName(_fromUtf8("formGrid"))
        self.useridLabel = QtGui.QLabel(Form)
        self.useridLabel.setObjectName(_fromUtf8("useridLabel"))
        self.formGrid.addWidget(self.useridLabel, 1, 0, 1, 1)
        self.useridEdit = QtGui.QLineEdit(Form)
        self.useridEdit.setObjectName(_fromUtf8("useridEdit"))
        self.formGrid.addWidget(self.useridEdit, 1, 1, 1, 1)
        self.passwordLabel = QtGui.QLabel(Form)
        self.passwordLabel.setObjectName(_fromUtf8("passwordLabel"))
        self.formGrid.addWidget(self.passwordLabel, 2, 0, 1, 1)
        self.passwordEdit = QtGui.QLineEdit(Form)
        self.passwordEdit.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordEdit.setObjectName(_fromUtf8("passwordEdit"))
        self.formGrid.addWidget(self.passwordEdit, 2, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formGrid.addItem(spacerItem, 5, 1, 1, 1)
        self.anonCheck = QtGui.QCheckBox(Form)
        self.anonCheck.setObjectName(_fromUtf8("anonCheck"))
        self.formGrid.addWidget(self.anonCheck, 0, 1, 1, 1)
        self.useSslCheck = QtGui.QCheckBox(Form)
        self.useSslCheck.setObjectName(_fromUtf8("useSslCheck"))
        self.formGrid.addWidget(self.useSslCheck, 3, 1, 1, 1)
        self.obtainLabel = QtGui.QLabel(Form)
        self.obtainLabel.setWordWrap(True)
        self.obtainLabel.setOpenExternalLinks(True)
        self.obtainLabel.setObjectName(_fromUtf8("obtainLabel"))
        self.formGrid.addWidget(self.obtainLabel, 4, 1, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.anonCheck, self.useridEdit)
        Form.setTabOrder(self.useridEdit, self.passwordEdit)

    def retranslateUi(self, Form):
        self.useridLabel.setText(_("User ID:"))
        self.passwordLabel.setText(_("Password:"))
        self.anonCheck.setText(_("Anonymous"))
        self.useSslCheck.setText(_("Use SSL"))
        self.obtainLabel.setText(_("To obtain User ID register at <a href=\"http://new-wallpaper.org\">new-wallpaper.org</a>"))

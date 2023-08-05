# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_scripts.ui'
#
# Created: Sat Nov 12 19:02:51 2011
#      by: PyQt4 UI code generator 4.8.5
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
        Form.resize(415, 300)
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scripts = QtGui.QScrollArea(Form)
        self.scripts.setWidgetResizable(True)
        self.scripts.setObjectName(_fromUtf8("scripts"))
        self.scriptsContents = QtGui.QWidget()
        self.scriptsContents.setGeometry(QtCore.QRect(0, 0, 395, 256))
        self.scriptsContents.setObjectName(_fromUtf8("scriptsContents"))
        self.formLayout = QtGui.QFormLayout(self.scriptsContents)
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.otherRadio = QtGui.QRadioButton(self.scriptsContents)
        self.otherRadio.setText(QtGui.QApplication.translate("Form", "Other", None, QtGui.QApplication.UnicodeUTF8))
        self.otherRadio.setObjectName(_fromUtf8("otherRadio"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.otherRadio)
        self.otherLayout = QtGui.QHBoxLayout()
        self.otherLayout.setObjectName(_fromUtf8("otherLayout"))
        self.otherEdit = QtGui.QLineEdit(self.scriptsContents)
        self.otherEdit.setObjectName(_fromUtf8("otherEdit"))
        self.otherLayout.addWidget(self.otherEdit)
        self.otherBrowseButton = QtGui.QPushButton(self.scriptsContents)
        self.otherBrowseButton.setText(QtGui.QApplication.translate("Form", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.otherBrowseButton.setObjectName(_fromUtf8("otherBrowseButton"))
        self.otherLayout.addWidget(self.otherBrowseButton)
        self.formLayout.setLayout(0, QtGui.QFormLayout.FieldRole, self.otherLayout)
        self.scripts.setWidget(self.scriptsContents)
        self.verticalLayout.addWidget(self.scripts)
        self.KDE4Label = QtGui.QLabel(Form)
        self.KDE4Label.setText(QtGui.QApplication.translate("Form", "To use KDE4 script you need <a href=\"http://code.google.com/p/ksetwallpaper/\">KSetWallpaper plasmoid</a> running", None, QtGui.QApplication.UnicodeUTF8))
        self.KDE4Label.setOpenExternalLinks(True)
        self.KDE4Label.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.KDE4Label.setObjectName(_fromUtf8("KDE4Label"))
        self.verticalLayout.addWidget(self.KDE4Label)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        self.otherRadio.setText(_("Other"))
        self.otherBrowseButton.setText(_("Browse"))
        self.KDE4Label.setText(_("To use KDE4 script you need <a href=\"http://code.google.com/p/ksetwallpaper/\">KSetWallpaper plasmoid</a> running"))

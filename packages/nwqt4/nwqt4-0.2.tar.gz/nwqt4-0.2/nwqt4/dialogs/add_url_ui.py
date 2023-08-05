# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/add_url.ui'
#
# Created: Sun Oct 30 14:18:36 2011
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
        Dialog.resize(400, 149)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Add url", None, QtGui.QApplication.UnicodeUTF8))
        self.formLayout = QtGui.QFormLayout(Dialog)
        self.formLayout.setVerticalSpacing(3)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.urlLabel = QtGui.QLabel(Dialog)
        self.urlLabel.setText(QtGui.QApplication.translate("Dialog", "Url:", None, QtGui.QApplication.UnicodeUTF8))
        self.urlLabel.setObjectName(_fromUtf8("urlLabel"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.urlLabel)
        self.urlEdit = QtGui.QLineEdit(Dialog)
        self.urlEdit.setObjectName(_fromUtf8("urlEdit"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.urlEdit)
        self.tagsLabel = QtGui.QLabel(Dialog)
        self.tagsLabel.setText(QtGui.QApplication.translate("Dialog", "Tags (max 5):", None, QtGui.QApplication.UnicodeUTF8))
        self.tagsLabel.setObjectName(_fromUtf8("tagsLabel"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.tagsLabel)
        self.tagsEdit = QtGui.QLineEdit(Dialog)
        self.tagsEdit.setObjectName(_fromUtf8("tagsEdit"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.tagsEdit)
        self.sendXmppCheck = QtGui.QCheckBox(Dialog)
        self.sendXmppCheck.setText(QtGui.QApplication.translate("Dialog", "Send jabber notifications", None, QtGui.QApplication.UnicodeUTF8))
        self.sendXmppCheck.setObjectName(_fromUtf8("sendXmppCheck"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.FieldRole, self.sendXmppCheck)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(8, QtGui.QFormLayout.FieldRole, self.buttonBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.formLayout.setItem(7, QtGui.QFormLayout.FieldRole, spacerItem)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        Dialog.setTabOrder(self.urlEdit, self.tagsEdit)
        Dialog.setTabOrder(self.tagsEdit, self.sendXmppCheck)
        Dialog.setTabOrder(self.sendXmppCheck, self.buttonBox)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_("Add url"))
        self.urlLabel.setText(_("Url:"))
        self.tagsLabel.setText(_("Tags (max 5):"))
        self.sendXmppCheck.setText(_("Send jabber notifications"))
        self.buttonBox.button(QtGui.QDialogButtonBox.Ok).setText(_('OK'))
        self.buttonBox.button(QtGui.QDialogButtonBox.Cancel).setText(_('Cancel'))


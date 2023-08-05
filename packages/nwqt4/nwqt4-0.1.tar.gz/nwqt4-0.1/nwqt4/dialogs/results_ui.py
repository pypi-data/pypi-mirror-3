# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/results.ui'
#
# Created: Thu Apr 21 14:47:59 2011
#      by: PyQt4 UI code generator 4.8.3
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
        Dialog.resize(160, 90)
        self.verticalLayout = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.refreshButton = QtGui.QToolButton(Dialog)
        self.refreshButton.setText(_fromUtf8(""))
        self.refreshButton.setAutoRaise(True)
        self.refreshButton.setObjectName(_fromUtf8("refreshButton"))
        self.horizontalLayout.addWidget(self.refreshButton)
        self.captionLabel = QtGui.QLabel(Dialog)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.captionLabel.sizePolicy().hasHeightForWidth())
        self.captionLabel.setSizePolicy(sizePolicy)
        self.captionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.captionLabel.setObjectName(_fromUtf8("captionLabel"))
        self.horizontalLayout.addWidget(self.captionLabel)
        self.closeButton = QtGui.QToolButton(Dialog)
        self.closeButton.setText(_fromUtf8(""))
        self.closeButton.setAutoRaise(True)
        self.closeButton.setObjectName(_fromUtf8("closeButton"))
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL(_fromUtf8("clicked()")), Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass


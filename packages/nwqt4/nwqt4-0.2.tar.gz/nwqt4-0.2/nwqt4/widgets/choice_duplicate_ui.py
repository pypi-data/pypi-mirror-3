# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/choice_duplicate.ui'
#
# Created: Sun Oct 30 17:20:54 2011
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
        Form.resize(496, 181)
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.wallpaper1Layout = QtGui.QVBoxLayout()
        self.wallpaper1Layout.setObjectName(_fromUtf8("wallpaper1Layout"))
        self.wallpaper1SizeLabel = QtGui.QLabel(Form)
        self.wallpaper1SizeLabel.setText(QtGui.QApplication.translate("Form", "Size:", None, QtGui.QApplication.UnicodeUTF8))
        self.wallpaper1SizeLabel.setObjectName(_fromUtf8("wallpaper1SizeLabel"))
        self.wallpaper1Layout.addWidget(self.wallpaper1SizeLabel)
        self.wallpaper1Label = QtGui.QLabel(Form)
        self.wallpaper1Label.setMinimumSize(QtCore.QSize(170, 100))
        self.wallpaper1Label.setMaximumSize(QtCore.QSize(170, 100))
        self.wallpaper1Label.setFrameShape(QtGui.QFrame.Box)
        self.wallpaper1Label.setFrameShadow(QtGui.QFrame.Sunken)
        self.wallpaper1Label.setText(_fromUtf8(""))
        self.wallpaper1Label.setAlignment(QtCore.Qt.AlignCenter)
        self.wallpaper1Label.setObjectName(_fromUtf8("wallpaper1Label"))
        self.wallpaper1Layout.addWidget(self.wallpaper1Label)
        self.original1Radio = QtGui.QRadioButton(Form)
        self.original1Radio.setText(QtGui.QApplication.translate("Form", "Original", None, QtGui.QApplication.UnicodeUTF8))
        self.original1Radio.setObjectName(_fromUtf8("original1Radio"))
        self.wallpaper1Layout.addWidget(self.original1Radio)
        self.horizontalLayout.addLayout(self.wallpaper1Layout)
        self.notDuplicatesRadio = QtGui.QRadioButton(Form)
        self.notDuplicatesRadio.setText(QtGui.QApplication.translate("Form", "Not duplicates", None, QtGui.QApplication.UnicodeUTF8))
        self.notDuplicatesRadio.setChecked(True)
        self.notDuplicatesRadio.setObjectName(_fromUtf8("notDuplicatesRadio"))
        self.horizontalLayout.addWidget(self.notDuplicatesRadio)
        self.wallpaper2Layout = QtGui.QVBoxLayout()
        self.wallpaper2Layout.setObjectName(_fromUtf8("wallpaper2Layout"))
        self.wallpaper2SizeLabel = QtGui.QLabel(Form)
        self.wallpaper2SizeLabel.setText(QtGui.QApplication.translate("Form", "Size:", None, QtGui.QApplication.UnicodeUTF8))
        self.wallpaper2SizeLabel.setObjectName(_fromUtf8("wallpaper2SizeLabel"))
        self.wallpaper2Layout.addWidget(self.wallpaper2SizeLabel)
        self.wallpaper2Label = QtGui.QLabel(Form)
        self.wallpaper2Label.setMinimumSize(QtCore.QSize(170, 100))
        self.wallpaper2Label.setMaximumSize(QtCore.QSize(170, 100))
        self.wallpaper2Label.setFrameShape(QtGui.QFrame.Box)
        self.wallpaper2Label.setFrameShadow(QtGui.QFrame.Sunken)
        self.wallpaper2Label.setText(_fromUtf8(""))
        self.wallpaper2Label.setAlignment(QtCore.Qt.AlignCenter)
        self.wallpaper2Label.setObjectName(_fromUtf8("wallpaper2Label"))
        self.wallpaper2Layout.addWidget(self.wallpaper2Label)
        self.original2Radio = QtGui.QRadioButton(Form)
        self.original2Radio.setText(QtGui.QApplication.translate("Form", "Original", None, QtGui.QApplication.UnicodeUTF8))
        self.original2Radio.setObjectName(_fromUtf8("original2Radio"))
        self.wallpaper2Layout.addWidget(self.original2Radio)
        self.horizontalLayout.addLayout(self.wallpaper2Layout)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        self.wallpaper1SizeLabel.setText(_("Size:"))
        self.original1Radio.setText(_("Original"))
        self.notDuplicatesRadio.setText(_("Not duplicates"))
        self.wallpaper2SizeLabel.setText(_("Size:"))
        self.original2Radio.setText(_("Original"))



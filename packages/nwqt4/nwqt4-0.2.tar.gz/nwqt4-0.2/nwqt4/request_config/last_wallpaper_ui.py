# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/last_wallpaper.ui'
#
# Created: Tue Nov 15 22:32:00 2011
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
        Form.resize(371, 83)
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.numberLayout = QtGui.QHBoxLayout()
        self.numberLayout.setObjectName(_fromUtf8("numberLayout"))
        self.numberLabel = QtGui.QLabel(Form)
        self.numberLabel.setText(QtGui.QApplication.translate("Form", "Number:", None, QtGui.QApplication.UnicodeUTF8))
        self.numberLabel.setObjectName(_fromUtf8("numberLabel"))
        self.numberLayout.addWidget(self.numberLabel)
        self.numberSpin = QtGui.QSpinBox(Form)
        self.numberSpin.setMinimum(1)
        self.numberSpin.setMaximum(9)
        self.numberSpin.setObjectName(_fromUtf8("numberSpin"))
        self.numberLayout.addWidget(self.numberSpin)
        self.numberSlider = QtGui.QSlider(Form)
        self.numberSlider.setMinimum(1)
        self.numberSlider.setMaximum(9)
        self.numberSlider.setPageStep(4)
        self.numberSlider.setSliderPosition(1)
        self.numberSlider.setOrientation(QtCore.Qt.Horizontal)
        self.numberSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.numberSlider.setTickInterval(1)
        self.numberSlider.setObjectName(_fromUtf8("numberSlider"))
        self.numberLayout.addWidget(self.numberSlider)
        self.verticalLayout.addLayout(self.numberLayout)
        self.actionCheck = QtGui.QCheckBox(Form)
        self.actionCheck.setText(QtGui.QApplication.translate("Form", "Set new wallpaper", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCheck.setObjectName(_fromUtf8("actionCheck"))
        self.verticalLayout.addWidget(self.actionCheck)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.numberSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.numberSpin.setValue)
        QtCore.QObject.connect(self.numberSpin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.numberSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.numberSpin, self.numberSlider)

    def retranslateUi(self, Form):
        self.numberLabel.setText(_("Number:"))
        self.actionCheck.setText(_("Set new wallpaper"))


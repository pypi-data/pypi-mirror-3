# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/new_wallpaper.ui'
#
# Created: Sun Oct 10 17:04:37 2010
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
        Form.resize(371, 119)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.countLayout = QtGui.QHBoxLayout()
        self.countLayout.setObjectName(_fromUtf8("countLayout"))
        self.countLabel = QtGui.QLabel(Form)
        self.countLabel.setObjectName(_fromUtf8("countLabel"))
        self.countLayout.addWidget(self.countLabel)
        self.countSpin = QtGui.QSpinBox(Form)
        self.countSpin.setMinimum(1)
        self.countSpin.setMaximum(9)
        self.countSpin.setObjectName(_fromUtf8("countSpin"))
        self.countLayout.addWidget(self.countSpin)
        self.countSlider = QtGui.QSlider(Form)
        self.countSlider.setMinimum(1)
        self.countSlider.setMaximum(9)
        self.countSlider.setPageStep(4)
        self.countSlider.setSliderPosition(1)
        self.countSlider.setOrientation(QtCore.Qt.Horizontal)
        self.countSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.countSlider.setTickInterval(1)
        self.countSlider.setObjectName(_fromUtf8("countSlider"))
        self.countLayout.addWidget(self.countSlider)
        self.verticalLayout.addLayout(self.countLayout)
        self.weightLayout = QtGui.QHBoxLayout()
        self.weightLayout.setObjectName(_fromUtf8("weightLayout"))
        self.weightLabel = QtGui.QLabel(Form)
        self.weightLabel.setObjectName(_fromUtf8("weightLabel"))
        self.weightLayout.addWidget(self.weightLabel)
        self.weightSpin = QtGui.QDoubleSpinBox(Form)
        self.weightSpin.setSingleStep(0.1)
        self.weightSpin.setProperty(_fromUtf8("value"), 1.0)
        self.weightSpin.setObjectName(_fromUtf8("weightSpin"))
        self.weightLayout.addWidget(self.weightSpin)
        self.verticalLayout.addLayout(self.weightLayout)
        self.actionCheck = QtGui.QCheckBox(Form)
        self.actionCheck.setObjectName(_fromUtf8("actionCheck"))
        self.verticalLayout.addWidget(self.actionCheck)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.countSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.countSpin.setValue)
        QtCore.QObject.connect(self.countSpin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.countSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.countSpin, self.countSlider)

    def retranslateUi(self, Form):
        self.countLabel.setText(_("Count:"))
        self.weightLabel.setText(_("Min weight:"))
        self.actionCheck.setText(_("Set new wallpaper"))


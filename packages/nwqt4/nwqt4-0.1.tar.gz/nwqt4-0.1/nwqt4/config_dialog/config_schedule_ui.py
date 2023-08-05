# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_schedule.ui'
#
# Created: Tue Oct 12 19:13:10 2010
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
        Form.resize(506, 271)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.scheduleLayout = QtGui.QHBoxLayout()
        self.scheduleLayout.setSpacing(0)
        self.scheduleLayout.setObjectName(_fromUtf8("scheduleLayout"))
        self.scheduleCheck = QtGui.QCheckBox(Form)
        self.scheduleCheck.setObjectName(_fromUtf8("scheduleCheck"))
        self.scheduleLayout.addWidget(self.scheduleCheck)
        self.scheduleSpin = QtGui.QSpinBox(Form)
        self.scheduleSpin.setMinimum(1)
        self.scheduleSpin.setMaximum(9999)
        self.scheduleSpin.setProperty(_fromUtf8("value"), 24)
        self.scheduleSpin.setObjectName(_fromUtf8("scheduleSpin"))
        self.scheduleLayout.addWidget(self.scheduleSpin)
        self.verticalLayout.addLayout(self.scheduleLayout)
        self.requestLayout = QtGui.QHBoxLayout()
        self.requestLayout.setObjectName(_fromUtf8("requestLayout"))
        self.requestLabel = QtGui.QLabel(Form)
        self.requestLabel.setObjectName(_fromUtf8("requestLabel"))
        self.requestLayout.addWidget(self.requestLabel)
        self.requestCombo = QtGui.QComboBox(Form)
        self.requestCombo.setObjectName(_fromUtf8("requestCombo"))
        self.requestLayout.addWidget(self.requestCombo)
        self.requestLayout.setStretch(1, 1)
        self.verticalLayout.addLayout(self.requestLayout)
        self.requestConfigs = QtGui.QStackedWidget(Form)
        self.requestConfigs.setObjectName(_fromUtf8("requestConfigs"))
        self.requestRandom = QtGui.QWidget()
        self.requestRandom.setObjectName(_fromUtf8("requestRandom"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.requestRandom)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.requestConfigs.addWidget(self.requestRandom)
        self.requestLast = QtGui.QWidget()
        self.requestLast.setObjectName(_fromUtf8("requestLast"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.requestLast)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        spacerItem1 = QtGui.QSpacerItem(20, 160, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.requestConfigs.addWidget(self.requestLast)
        self.requestNew = QtGui.QWidget()
        self.requestNew.setObjectName(_fromUtf8("requestNew"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.requestNew)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        spacerItem2 = QtGui.QSpacerItem(20, 160, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.requestConfigs.addWidget(self.requestNew)
        self.verticalLayout.addWidget(self.requestConfigs)

        self.retranslateUi(Form)
        self.requestConfigs.setCurrentIndex(0)
        QtCore.QObject.connect(self.requestCombo, QtCore.SIGNAL(_fromUtf8("currentIndexChanged(int)")), self.requestConfigs.setCurrentIndex)
        QtCore.QObject.connect(self.requestConfigs, QtCore.SIGNAL(_fromUtf8("currentChanged(int)")), self.requestCombo.setCurrentIndex)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.scheduleCheck, self.scheduleSpin)
        Form.setTabOrder(self.scheduleSpin, self.requestCombo)

    def retranslateUi(self, Form):
        self.scheduleCheck.setText(_("Enable schedule. Request every"))
        self.requestLabel.setText(_("Request"))


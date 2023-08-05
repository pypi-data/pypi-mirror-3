# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_duplicates.ui'
#
# Created: Thu Oct 14 19:50:19 2010
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
        Form.resize(437, 191)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.searchDuplicatesLayout = QtGui.QHBoxLayout()
        self.searchDuplicatesLayout.setObjectName(_fromUtf8("searchDuplicatesLayout"))
        self.searchDuplicatesCheck = QtGui.QCheckBox(Form)
        self.searchDuplicatesCheck.setObjectName(_fromUtf8("searchDuplicatesCheck"))
        self.searchDuplicatesLayout.addWidget(self.searchDuplicatesCheck)
        self.searchDuplicatesSpin = QtGui.QSpinBox(Form)
        self.searchDuplicatesSpin.setMinimum(1)
        self.searchDuplicatesSpin.setMaximum(9999)
        self.searchDuplicatesSpin.setProperty(_fromUtf8("value"), 10)
        self.searchDuplicatesSpin.setObjectName(_fromUtf8("searchDuplicatesSpin"))
        self.searchDuplicatesLayout.addWidget(self.searchDuplicatesSpin)
        self.verticalLayout.addLayout(self.searchDuplicatesLayout)
        self.pairsLimitLayout = QtGui.QHBoxLayout()
        self.pairsLimitLayout.setObjectName(_fromUtf8("pairsLimitLayout"))
        self.pairsLimitCheck = QtGui.QCheckBox(Form)
        self.pairsLimitCheck.setObjectName(_fromUtf8("pairsLimitCheck"))
        self.pairsLimitLayout.addWidget(self.pairsLimitCheck)
        self.pairsLimitSpin = QtGui.QSpinBox(Form)
        self.pairsLimitSpin.setMinimum(1)
        self.pairsLimitSpin.setMaximum(9999)
        self.pairsLimitSpin.setProperty(_fromUtf8("value"), 100)
        self.pairsLimitSpin.setObjectName(_fromUtf8("pairsLimitSpin"))
        self.pairsLimitLayout.addWidget(self.pairsLimitSpin)
        self.verticalLayout.addLayout(self.pairsLimitLayout)
        self.meanLayout = QtGui.QHBoxLayout()
        self.meanLayout.setObjectName(_fromUtf8("meanLayout"))
        self.meanLabel = QtGui.QLabel(Form)
        self.meanLabel.setObjectName(_fromUtf8("meanLabel"))
        self.meanLayout.addWidget(self.meanLabel)
        self.meanSpin = QtGui.QDoubleSpinBox(Form)
        self.meanSpin.setDecimals(1)
        self.meanSpin.setMaximum(255.0)
        self.meanSpin.setSingleStep(0.1)
        self.meanSpin.setProperty(_fromUtf8("value"), 10.0)
        self.meanSpin.setObjectName(_fromUtf8("meanSpin"))
        self.meanLayout.addWidget(self.meanSpin)
        self.verticalLayout.addLayout(self.meanLayout)
        self.stddevLayout = QtGui.QHBoxLayout()
        self.stddevLayout.setObjectName(_fromUtf8("stddevLayout"))
        self.stddevLabel = QtGui.QLabel(Form)
        self.stddevLabel.setObjectName(_fromUtf8("stddevLabel"))
        self.stddevLayout.addWidget(self.stddevLabel)
        self.stddevSpin = QtGui.QDoubleSpinBox(Form)
        self.stddevSpin.setDecimals(1)
        self.stddevSpin.setMaximum(255.0)
        self.stddevSpin.setSingleStep(0.1)
        self.stddevSpin.setProperty(_fromUtf8("value"), 10.0)
        self.stddevSpin.setObjectName(_fromUtf8("stddevSpin"))
        self.stddevLayout.addWidget(self.stddevSpin)
        self.verticalLayout.addLayout(self.stddevLayout)
        self.sendCheck = QtGui.QCheckBox(Form)
        self.sendCheck.setObjectName(_fromUtf8("sendCheck"))
        self.verticalLayout.addWidget(self.sendCheck)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        self.searchDuplicatesCheck.setText(_("Search for duplicates every"))
        self.pairsLimitCheck.setText(_("Pairs limit:"))
        self.meanLabel.setText(_("Max mean:"))
        self.stddevLabel.setText(_("Max stddev:",))
        self.sendCheck.setText(_("Send duplicates to new-wallpaper.org"))


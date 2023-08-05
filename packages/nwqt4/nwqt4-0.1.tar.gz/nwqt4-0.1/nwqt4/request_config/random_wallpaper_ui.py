# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/random_wallpaper.ui'
#
# Created: Sun Oct 10 17:04:46 2010
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
        Form.resize(371, 277)
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
        self.resolutionsLabel = QtGui.QLabel(Form)
        self.resolutionsLabel.setObjectName(_fromUtf8("resolutionsLabel"))
        self.verticalLayout.addWidget(self.resolutionsLabel)
        self.resolutionsEdit = QtGui.QLineEdit(Form)
        self.resolutionsEdit.setObjectName(_fromUtf8("resolutionsEdit"))
        self.verticalLayout.addWidget(self.resolutionsEdit)
        self.tagsLabel = QtGui.QLabel(Form)
        self.tagsLabel.setObjectName(_fromUtf8("tagsLabel"))
        self.verticalLayout.addWidget(self.tagsLabel)
        self.tagsEdit = QtGui.QLineEdit(Form)
        self.tagsEdit.setObjectName(_fromUtf8("tagsEdit"))
        self.verticalLayout.addWidget(self.tagsEdit)
        self.notagsLabel = QtGui.QLabel(Form)
        self.notagsLabel.setObjectName(_fromUtf8("notagsLabel"))
        self.verticalLayout.addWidget(self.notagsLabel)
        self.notagsEdit = QtGui.QLineEdit(Form)
        self.notagsEdit.setObjectName(_fromUtf8("notagsEdit"))
        self.verticalLayout.addWidget(self.notagsEdit)
        self.bottomLayout = QtGui.QHBoxLayout()
        self.bottomLayout.setObjectName(_fromUtf8("bottomLayout"))
        self.useronlyCheck = QtGui.QCheckBox(Form)
        self.useronlyCheck.setObjectName(_fromUtf8("useronlyCheck"))
        self.bottomLayout.addWidget(self.useronlyCheck)
        self.actionCheck = QtGui.QCheckBox(Form)
        self.actionCheck.setObjectName(_fromUtf8("actionCheck"))
        self.bottomLayout.addWidget(self.actionCheck)
        self.verticalLayout.addLayout(self.bottomLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.countSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.countSpin.setValue)
        QtCore.QObject.connect(self.countSpin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.countSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.countSpin, self.countSlider)
        Form.setTabOrder(self.countSlider, self.resolutionsEdit)
        Form.setTabOrder(self.resolutionsEdit, self.tagsEdit)
        Form.setTabOrder(self.tagsEdit, self.notagsEdit)
        Form.setTabOrder(self.notagsEdit, self.useronlyCheck)
        Form.setTabOrder(self.useronlyCheck, self.actionCheck)

    def retranslateUi(self, Form):
        self.countLabel.setText(_("Count:"))
        self.resolutionsLabel.setText(_("Comma separated list of resolutions (max 5),\n"
            "in preferred order, e.g. 1024x768, 1280x1024:"))
        self.tagsLabel.setText(_("Comma separated list of tags (max 5):"))
        self.notagsLabel.setText(_("Comma separated list of tags to exclude (max 5):"))
        self.useronlyCheck.setText(_("Only my wallpapers"))
        self.actionCheck.setText(_("Set new wallpaper"))


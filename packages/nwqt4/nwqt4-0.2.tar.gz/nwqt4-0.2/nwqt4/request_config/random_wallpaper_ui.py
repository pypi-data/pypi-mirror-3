# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/random_wallpaper.ui'
#
# Created: Tue Nov 15 21:13:01 2011
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
        Form.resize(640, 308)
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
        self.reslistLayout = QtGui.QHBoxLayout()
        self.reslistLayout.setObjectName(_fromUtf8("reslistLayout"))
        self.resListRadioButton = QtGui.QRadioButton(Form)
        self.resListRadioButton.setText(QtGui.QApplication.translate("Form", "List of resolutions", None, QtGui.QApplication.UnicodeUTF8))
        self.resListRadioButton.setChecked(True)
        self.resListRadioButton.setObjectName(_fromUtf8("resListRadioButton"))
        self.reslistLayout.addWidget(self.resListRadioButton)
        self.resMinMaxRadioButton = QtGui.QRadioButton(Form)
        self.resMinMaxRadioButton.setText(QtGui.QApplication.translate("Form", "Min and/or max resolution", None, QtGui.QApplication.UnicodeUTF8))
        self.resMinMaxRadioButton.setObjectName(_fromUtf8("resMinMaxRadioButton"))
        self.reslistLayout.addWidget(self.resMinMaxRadioButton)
        self.verticalLayout.addLayout(self.reslistLayout)
        self.resolutionsLabel = QtGui.QLabel(Form)
        self.resolutionsLabel.setText(QtGui.QApplication.translate("Form", "Comma separated list of resolutions (max 5), in preferred order,\n"
"e.g. 1024x768, 1280x1024:", None, QtGui.QApplication.UnicodeUTF8))
        self.resolutionsLabel.setObjectName(_fromUtf8("resolutionsLabel"))
        self.verticalLayout.addWidget(self.resolutionsLabel)
        self.resolutionsEdit = QtGui.QLineEdit(Form)
        self.resolutionsEdit.setObjectName(_fromUtf8("resolutionsEdit"))
        self.verticalLayout.addWidget(self.resolutionsEdit)
        self.tagsLabel = QtGui.QLabel(Form)
        self.tagsLabel.setText(QtGui.QApplication.translate("Form", "Comma separated list of tags (max 5):", None, QtGui.QApplication.UnicodeUTF8))
        self.tagsLabel.setObjectName(_fromUtf8("tagsLabel"))
        self.verticalLayout.addWidget(self.tagsLabel)
        self.tagsEdit = QtGui.QLineEdit(Form)
        self.tagsEdit.setObjectName(_fromUtf8("tagsEdit"))
        self.verticalLayout.addWidget(self.tagsEdit)
        self.notagsLabel = QtGui.QLabel(Form)
        self.notagsLabel.setText(QtGui.QApplication.translate("Form", "Comma separated list of tags to exclude (max 5):", None, QtGui.QApplication.UnicodeUTF8))
        self.notagsLabel.setObjectName(_fromUtf8("notagsLabel"))
        self.verticalLayout.addWidget(self.notagsLabel)
        self.notagsEdit = QtGui.QLineEdit(Form)
        self.notagsEdit.setObjectName(_fromUtf8("notagsEdit"))
        self.verticalLayout.addWidget(self.notagsEdit)
        self.bottomLayout = QtGui.QHBoxLayout()
        self.bottomLayout.setObjectName(_fromUtf8("bottomLayout"))
        self.useronlyCheck = QtGui.QCheckBox(Form)
        self.useronlyCheck.setText(QtGui.QApplication.translate("Form", "Only my wallpapers", None, QtGui.QApplication.UnicodeUTF8))
        self.useronlyCheck.setObjectName(_fromUtf8("useronlyCheck"))
        self.bottomLayout.addWidget(self.useronlyCheck)
        self.actionCheck = QtGui.QCheckBox(Form)
        self.actionCheck.setText(QtGui.QApplication.translate("Form", "Set new wallpaper", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCheck.setObjectName(_fromUtf8("actionCheck"))
        self.bottomLayout.addWidget(self.actionCheck)
        self.verticalLayout.addLayout(self.bottomLayout)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QObject.connect(self.numberSlider, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.numberSpin.setValue)
        QtCore.QObject.connect(self.numberSpin, QtCore.SIGNAL(_fromUtf8("valueChanged(int)")), self.numberSlider.setValue)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.numberSpin, self.numberSlider)
        Form.setTabOrder(self.numberSlider, self.resolutionsEdit)
        Form.setTabOrder(self.resolutionsEdit, self.tagsEdit)
        Form.setTabOrder(self.tagsEdit, self.notagsEdit)
        Form.setTabOrder(self.notagsEdit, self.useronlyCheck)
        Form.setTabOrder(self.useronlyCheck, self.actionCheck)

    def retranslateUi(self, Form):
        self.numberLabel.setText(_("Number:"))
        self.resListRadioButton.setText(_("List of resolutions"))
        self.resMinMaxRadioButton.setText(_("Min and/or max resolutions"))
        self.resolutionsLabel.setText(_("Comma separated list of resolutions (max 5), in preferred order,\n"
            "e.g. 1024x768, 1280x1024:"))
        self.tagsLabel.setText(_("Comma separated list of tags (max 5):"))
        self.notagsLabel.setText(_("Comma separated list of tags to exclude (max 5):"))
        self.useronlyCheck.setText(_("Only my wallpapers"))
        self.actionCheck.setText(_("Set new wallpaper"))

# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_icon.ui'
#
# Created: Tue Oct 12 22:35:17 2010
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
        Form.resize(400, 228)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.iconGroup = QtGui.QGroupBox(Form)
        self.iconGroup.setObjectName(_fromUtf8("iconGroup"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.iconGroup)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.doNothingRadio = QtGui.QRadioButton(self.iconGroup)
        self.doNothingRadio.setChecked(True)
        self.doNothingRadio.setObjectName(_fromUtf8("doNothingRadio"))
        self.verticalLayout_2.addWidget(self.doNothingRadio)
        self.requestRandomWallpaperRadio = QtGui.QRadioButton(self.iconGroup)
        self.requestRandomWallpaperRadio.setObjectName(_fromUtf8("requestRandomWallpaperRadio"))
        self.verticalLayout_2.addWidget(self.requestRandomWallpaperRadio)
        self.requestLastWallpaperRadio = QtGui.QRadioButton(self.iconGroup)
        self.requestLastWallpaperRadio.setObjectName(_fromUtf8("requestLastWallpaperRadio"))
        self.verticalLayout_2.addWidget(self.requestLastWallpaperRadio)
        self.requestNewWallpaperRadio = QtGui.QRadioButton(self.iconGroup)
        self.requestNewWallpaperRadio.setObjectName(_fromUtf8("requestNewWallpaperRadio"))
        self.verticalLayout_2.addWidget(self.requestNewWallpaperRadio)
        self.addUrlRadio = QtGui.QRadioButton(self.iconGroup)
        self.addUrlRadio.setObjectName(_fromUtf8("addUrlRadio"))
        self.verticalLayout_2.addWidget(self.addUrlRadio)
        self.forceScheduledRequestRadio = QtGui.QRadioButton(self.iconGroup)
        self.forceScheduledRequestRadio.setObjectName(_fromUtf8("forceScheduledRequestRadio"))
        self.verticalLayout_2.addWidget(self.forceScheduledRequestRadio)
        self.verticalLayout.addWidget(self.iconGroup)
        spacerItem = QtGui.QSpacerItem(20, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        self.iconGroup.setTitle(_("On icon click"))
        self.doNothingRadio.setText(_("Do nothing"))
        self.requestRandomWallpaperRadio.setText(_("Request random wallpaper"))
        self.requestLastWallpaperRadio.setText(_("Request last wallpaper"))
        self.requestNewWallpaperRadio.setText(_("Request new wallpaper"))
        self.addUrlRadio.setText(_("Add url"))
        self.forceScheduledRequestRadio.setText(_("Force scheduled request"))


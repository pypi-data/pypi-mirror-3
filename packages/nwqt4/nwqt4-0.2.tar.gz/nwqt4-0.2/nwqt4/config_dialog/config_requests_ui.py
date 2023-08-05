# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/config_requests.ui'
#
# Created: Sun Oct 10 16:44:42 2010
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
        Form.resize(464, 283)
        self.verticalLayout = QtGui.QVBoxLayout(Form)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.tabWidget = QtGui.QTabWidget(Form)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.randomWallpaperTab = QtGui.QWidget()
        self.randomWallpaperTab.setObjectName(_fromUtf8("randomWallpaperTab"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.randomWallpaperTab)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.randomWallpaperAskCheck = QtGui.QCheckBox(self.randomWallpaperTab)
        self.randomWallpaperAskCheck.setObjectName(_fromUtf8("randomWallpaperAskCheck"))
        self.verticalLayout_2.addWidget(self.randomWallpaperAskCheck)
        spacerItem = QtGui.QSpacerItem(20, 181, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabWidget.addTab(self.randomWallpaperTab, _fromUtf8(""))
        self.lastWallpaperTab = QtGui.QWidget()
        self.lastWallpaperTab.setObjectName(_fromUtf8("lastWallpaperTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.lastWallpaperTab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.lastWallpaperAskCheck = QtGui.QCheckBox(self.lastWallpaperTab)
        self.lastWallpaperAskCheck.setObjectName(_fromUtf8("lastWallpaperAskCheck"))
        self.verticalLayout_3.addWidget(self.lastWallpaperAskCheck)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.tabWidget.addTab(self.lastWallpaperTab, _fromUtf8(""))
        self.newWallpaperTab = QtGui.QWidget()
        self.newWallpaperTab.setObjectName(_fromUtf8("newWallpaperTab"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.newWallpaperTab)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.newWallpaperAskCheck = QtGui.QCheckBox(self.newWallpaperTab)
        self.newWallpaperAskCheck.setObjectName(_fromUtf8("newWallpaperAskCheck"))
        self.verticalLayout_4.addWidget(self.newWallpaperAskCheck)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.tabWidget.addTab(self.newWallpaperTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.tabWidget)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        self.randomWallpaperAskCheck.setText(_("Ask for settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.randomWallpaperTab), _("Random wallpaper"))
        self.lastWallpaperAskCheck.setText(_("Ask for settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.lastWallpaperTab), _("Last wallpaper"))
        self.newWallpaperAskCheck.setText(_("Ask for settings"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.newWallpaperTab), _("New wallpaper"))


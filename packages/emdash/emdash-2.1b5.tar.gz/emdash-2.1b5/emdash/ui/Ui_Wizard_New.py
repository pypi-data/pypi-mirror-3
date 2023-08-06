# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Wizard_New.ui'
#
# Created: Fri May 20 08:02:48 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Wizard_New(object):
    def setupUi(self, Wizard_New):
        Wizard_New.setObjectName("Wizard_New")
        Wizard_New.resize(329, 355)
        self.verticalLayout = QtGui.QVBoxLayout(Wizard_New)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_help = QtGui.QLabel(Wizard_New)
        self.label_help.setText("")
        self.label_help.setTextFormat(QtCore.Qt.RichText)
        self.label_help.setWordWrap(True)
        self.label_help.setOpenExternalLinks(True)
        self.label_help.setObjectName("label_help")
        self.verticalLayout.addWidget(self.label_help)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setObjectName("layout")
        self.verticalLayout.addLayout(self.layout)

        self.retranslateUi(Wizard_New)
        QtCore.QMetaObject.connectSlotsByName(Wizard_New)

    def retranslateUi(self, Wizard_New):
        Wizard_New.setWindowTitle(QtGui.QApplication.translate("Wizard_New", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))


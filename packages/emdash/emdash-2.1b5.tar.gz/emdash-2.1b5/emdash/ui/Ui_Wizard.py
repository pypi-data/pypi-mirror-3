# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Wizard.ui'
#
# Created: Fri May 20 08:02:48 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Wizard(object):
    def setupUi(self, Wizard):
        Wizard.setObjectName("Wizard")
        Wizard.resize(329, 355)
        self.verticalLayout = QtGui.QVBoxLayout(Wizard)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_help = QtGui.QLabel(Wizard)
        self.label_help.setText("")
        self.label_help.setTextFormat(QtCore.Qt.RichText)
        self.label_help.setWordWrap(True)
        self.label_help.setOpenExternalLinks(True)
        self.label_help.setObjectName("label_help")
        self.verticalLayout.addWidget(self.label_help)
        self.line = QtGui.QFrame(Wizard)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setObjectName("layout")
        self.verticalLayout.addLayout(self.layout)

        self.retranslateUi(Wizard)
        QtCore.QMetaObject.connectSlotsByName(Wizard)

    def retranslateUi(self, Wizard):
        Wizard.setWindowTitle(QtGui.QApplication.translate("Wizard", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))


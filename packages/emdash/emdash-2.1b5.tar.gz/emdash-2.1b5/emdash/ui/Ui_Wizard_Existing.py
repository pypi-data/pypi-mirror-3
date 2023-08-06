# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Wizard_Existing.ui'
#
# Created: Fri May 20 08:02:48 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Wizard_Existing(object):
    def setupUi(self, Wizard_Existing):
        Wizard_Existing.setObjectName("Wizard_Existing")
        Wizard_Existing.resize(329, 355)
        self.verticalLayout = QtGui.QVBoxLayout(Wizard_Existing)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_help = QtGui.QLabel(Wizard_Existing)
        self.label_help.setText("")
        self.label_help.setTextFormat(QtCore.Qt.RichText)
        self.label_help.setWordWrap(True)
        self.label_help.setOpenExternalLinks(True)
        self.label_help.setObjectName("label_help")
        self.verticalLayout.addWidget(self.label_help)
        self.line = QtGui.QFrame(Wizard_Existing)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setObjectName("layout")
        self.radio_existing = QtGui.QRadioButton(Wizard_Existing)
        self.radio_existing.setChecked(False)
        self.radio_existing.setObjectName("radio_existing")
        self.layout.addWidget(self.radio_existing)
        self.tree_records = QtGui.QTreeView(Wizard_Existing)
        self.tree_records.setObjectName("tree_records")
        self.layout.addWidget(self.tree_records)
        self.verticalLayout.addLayout(self.layout)

        self.retranslateUi(Wizard_Existing)
        QtCore.QMetaObject.connectSlotsByName(Wizard_Existing)

    def retranslateUi(self, Wizard_Existing):
        Wizard_Existing.setWindowTitle(QtGui.QApplication.translate("Wizard_Existing", "WizardPage", None, QtGui.QApplication.UnicodeUTF8))
        self.radio_existing.setText(QtGui.QApplication.translate("Wizard_Existing", "Select from list", None, QtGui.QApplication.UnicodeUTF8))


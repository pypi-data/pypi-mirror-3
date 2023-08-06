# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Warning.ui'
#
# Created: Fri May 20 08:02:48 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Warning(object):
    def setupUi(self, Warning):
        Warning.setObjectName("Warning")
        Warning.resize(428, 176)
        self.verticalLayout = QtGui.QVBoxLayout(Warning)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(Warning)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtGui.QLabel(Warning)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.label_6 = QtGui.QLabel(Warning)
        self.label_6.setObjectName("label_6")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_6)
        self.label_session = QtGui.QLabel(Warning)
        self.label_session.setOpenExternalLinks(True)
        self.label_session.setObjectName("label_session")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.label_session)
        self.label_user = QtGui.QLabel(Warning)
        self.label_user.setObjectName("label_user")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.label_user)
        self.verticalLayout.addLayout(self.formLayout)

        self.retranslateUi(Warning)
        QtCore.QMetaObject.connectSlotsByName(Warning)

    def retranslateUi(self, Warning):
        Warning.setWindowTitle(QtGui.QApplication.translate("Warning", "WARNING", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Warning", "There is currently a background process uploading data.\n"
"This window will close automatically when this task is finished.\n"
"Do NOT turn off this computer until this window has closed!", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Warning", "User", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("Warning", "Session", None, QtGui.QApplication.UnicodeUTF8))
        self.label_session.setText(QtGui.QApplication.translate("Warning", " ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_user.setText(QtGui.QApplication.translate("Warning", " ", None, QtGui.QApplication.UnicodeUTF8))


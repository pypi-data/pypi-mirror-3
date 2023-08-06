# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Login.ui'
#
# Created: Fri May 20 08:02:47 2011
#      by: PyQt4 UI code generator 4.7.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Login(object):
    def setupUi(self, Login):
        Login.setObjectName("Login")
        Login.resize(380, 176)
        self.verticalLayout = QtGui.QVBoxLayout(Login)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_login = QtGui.QLabel(Login)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_login.sizePolicy().hasHeightForWidth())
        self.label_login.setSizePolicy(sizePolicy)
        self.label_login.setAlignment(QtCore.Qt.AlignCenter)
        self.label_login.setObjectName("label_login")
        self.verticalLayout.addWidget(self.label_login)
        self.line = QtGui.QFrame(Login)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self.formLayout_2 = QtGui.QFormLayout()
        self.formLayout_2.setFieldGrowthPolicy(QtGui.QFormLayout.FieldsStayAtSizeHint)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label = QtGui.QLabel(Login)
        self.label.setObjectName("label")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.edit_name = QtGui.QLineEdit(Login)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_name.sizePolicy().hasHeightForWidth())
        self.edit_name.setSizePolicy(sizePolicy)
        self.edit_name.setObjectName("edit_name")
        self.formLayout_2.setWidget(0, QtGui.QFormLayout.FieldRole, self.edit_name)
        self.label_2 = QtGui.QLabel(Login)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.edit_password = QtGui.QLineEdit(Login)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.edit_password.sizePolicy().hasHeightForWidth())
        self.edit_password.setSizePolicy(sizePolicy)
        self.edit_password.setEchoMode(QtGui.QLineEdit.Password)
        self.edit_password.setObjectName("edit_password")
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.FieldRole, self.edit_password)
        self.verticalLayout.addLayout(self.formLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(Login)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.edit_name)
        self.label_2.setBuddy(self.edit_password)

        self.retranslateUi(Login)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), Login.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), Login.reject)
        QtCore.QMetaObject.connectSlotsByName(Login)

    def retranslateUi(self, Login):
        Login.setWindowTitle(QtGui.QApplication.translate("Login", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.label_login.setText(QtGui.QApplication.translate("Login", "Login", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Login", "Email", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Login", "Password", None, QtGui.QApplication.UnicodeUTF8))


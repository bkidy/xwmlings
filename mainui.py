# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainui.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1276, 1105)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        # MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.gridLayout_2.addLayout(self.verticalLayout, 1, 3, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.gridLayout_2.addWidget(self.comboBox, 1, 2, 1, 1)
        self.btn_discard = QtWidgets.QPushButton(self.centralwidget)
        self.btn_discard.setEnabled(True)
        self.btn_discard.setObjectName("btn_discard")
        self.gridLayout_2.addWidget(self.btn_discard, 4, 2, 1, 1)
        self.btn_exportAll = QtWidgets.QPushButton(self.centralwidget)
        self.btn_exportAll.setObjectName("btn_exportAll")
        self.gridLayout_2.addWidget(self.btn_exportAll, 5, 1, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.headerItem().setText(0, "1")
        self.gridLayout_2.addWidget(self.treeWidget, 2, 2, 2, 2)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 5, 2, 1, 2)
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setText("")
        self.lineEdit.setCursorPosition(0)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_2.addWidget(self.lineEdit, 3, 0, 1, 2)
        self.btn_q_role = QtWidgets.QPushButton(self.centralwidget)
        self.btn_q_role.setObjectName("btn_q_role")
        self.gridLayout_2.addWidget(self.btn_q_role, 4, 0, 1, 1)
        self.btn_send_email = QtWidgets.QPushButton(self.centralwidget)
        self.btn_send_email.setObjectName("btn_send_email")
        self.gridLayout_2.addWidget(self.btn_send_email, 5, 0, 1, 1)
        self.btn_preview = QtWidgets.QPushButton(self.centralwidget)
        self.btn_preview.setObjectName("btn_preview")
        self.gridLayout_2.addWidget(self.btn_preview, 4, 1, 1, 1)
        self.btn_save = QtWidgets.QPushButton(self.centralwidget)
        self.btn_save.setObjectName("btn_save")
        self.gridLayout_2.addWidget(self.btn_save, 4, 3, 1, 1)
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setObjectName("textBrowser")
        self.textBrowser.setText("??????????????????????????????????????????????????????????????????????????????\n")
        self.gridLayout_2.addWidget(self.textBrowser, 1, 0, 2, 2)
        self.treeWidget = QtWidgets.QTreeWidget(self.centralwidget)
        self.treeWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.treeWidget.setAllColumnsShowFocus(False)
        self.treeWidget.setWordWrap(False)
        self.treeWidget.setHeaderHidden(False)
        self.treeWidget.setColumnCount(2)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setCascadingSectionResizes(False)
        self.treeWidget.header().setDefaultSectionSize(222)
        self.gridLayout_2.addWidget(self.treeWidget, 2, 2, 2, 2)
        self.gridLayout.addLayout(self.gridLayout_2, 2, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1276, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btn_send_email.clicked.connect(MainWindow.btn_send_email)
        self.btn_preview.clicked.connect(MainWindow.pre_changed)
        self.btn_discard.clicked.connect(MainWindow.discard_changed)
        self.btn_save.clicked.connect(MainWindow.save_right_after)
        self.comboBox.currentIndexChanged.connect(MainWindow.select_role)
        self.btn_q_role.clicked.connect(MainWindow.update_role_data)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "??????????????????"))
        self.label_2.setText(_translate("MainWindow", "?????????"))
        self.btn_discard.setText(_translate("MainWindow", "????????????"))
        self.btn_exportAll.setText(_translate("MainWindow", "????????????"))
        self.label.setText(_translate("MainWindow", "????????????????????????????????????????????????"))
        self.lineEdit.setPlaceholderText(_translate("MainWindow", "?????????TOKEN???"))
        self.btn_q_role.setText(_translate("MainWindow", "????????????"))
        self.btn_send_email.setText(_translate("MainWindow", "????????????"))
        self.btn_preview.setText(_translate("MainWindow", "????????????"))
        self.btn_save.setText(_translate("MainWindow", "????????????"))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "??????"))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "??????"))


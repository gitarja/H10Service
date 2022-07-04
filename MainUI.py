from PyQt5 import QtCore, QtWidgets, QtGui


class Ui_MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.enableButtons()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(360, 145)
        self.startStopButton = QtWidgets.QPushButton(Dialog)
        self.startStopButton.setGeometry(QtCore.QRect(90, 40, 171, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.startStopButton.setFont(font)
        self.startStopButton.setObjectName("startStopButton")
        self.statusbar = QtWidgets.QStatusBar(Dialog)
        self.statusbar.setObjectName("statusbar")
        Dialog.setStatusBar(self.statusbar)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.startStopButton.setText(_translate("Dialog", "Start"))



    def enableButtons(self):
        self.startStopButton.setEnabled(False)

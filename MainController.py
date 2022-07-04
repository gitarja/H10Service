from PyQt5 import QtCore, QtWidgets
import sys
from MainUI import Ui_MainWindow
from Lib.Sensor import SensorScanner
from Lib.Utils import RecordingStatus
from Lib.Sender import SendReadUDP
from PyQt5.QtCore import QThread

class MainController:

    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.view = Ui_MainWindow()
        self.scanner = SensorScanner()
        self._recording_status = 0

        # controller
        self.view.startStopButton.clicked.connect(self.startStopRecording)

        self.scanner.status_update.connect(self.showStatus)

        self.scanner.sensor_client.recording_status.connect(self.updateRecordingStatus)

        self.scanner.sensor_client.status_update.connect(self.showStatus)

        # vicon
        self.udp_send_read = SendReadUDP()
        self.udp_send_read.is_started.connect(self.startStopRecording)
        self.udp_send_read.start(priority=QThread.HighestPriority)


    @property
    def recording_status(self):
        '''
        :return:
        0 = ready to scan
        1 = ready to record
        2 = recording
        '''
        return self._recording_status

    @recording_status.setter
    def recording_status(self, value):
        self._recording_status = value

    def run(self):
        self.view.show()
        self.scanner.scan()
        return self.app.exec_()

    def startStopRecording(self):

        if self.recording_status == 1:
            self.scanner.startRecording()
        elif self.recording_status == 2:
            self.scanner.stopRecording()
        else:
            self.scanner.scan()

    def showStatus(self, msg):
        self.view.statusbar.showMessage(msg)


    def updateRecordingStatus(self, status):
        if status==RecordingStatus.SEARCHING_SENSORS:
            self.view.startStopButton.setEnabled(False)
        elif status == RecordingStatus.RECORDING:
            self.view.startStopButton.setText("Stop")
            self.view.startStopButton.setEnabled(True)
            self.recording_status = 2
        elif status == RecordingStatus.READY or status == RecordingStatus.INITIALIZED:
            self.view.startStopButton.setText("Start Recording")
            self.view.startStopButton.setEnabled(True)
            self.recording_status = 1
        else:
            self.view.startStopButton.setText("Start")
            self.view.startStopButton.setEnabled(True)
            self.recording_status = 0

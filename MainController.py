from PyQt5 import QtCore, QtWidgets
import sys
from MainUI import Ui_MainWindow
from Lib.Sensor import SensorScanner
from Lib.Conf import RECORDING_STATUS, TTL
from Lib.Sender import SendReadUDP, TTLSender
import serial
from PyQt5.QtCore import QThread
import RPi.GPIO as GPIO
import time

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

        # ttl sender

        self.ttl_sender = TTLSender()
        # set serial for TTL sender
        self.ser = serial.Serial(
            port=TTL.PORT,  # please make sure the port name is correct
            baudrate=115200,  # maximum baud rate 115200
            bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
            stopbits=serial.STOPBITS_ONE,
            timeout=0
        )
        self.ttl_sender.setSerial(self.ser)


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
            self.ttl_sender.start(priority=QThread.HighestPriority)  # send ttl
            self.ttl_sender.stop()  # stop
            self.playNotification()

        elif self.recording_status == 2:
            self.scanner.stopRecording()
        else:
            self.scanner.scan()

    def showStatus(self, msg):
        self.view.statusbar.showMessage(msg)


    def updateRecordingStatus(self, status):
        if status==RECORDING_STATUS.SEARCHING_SENSORS:
            self.view.startStopButton.setEnabled(False)
        elif status == RECORDING_STATUS.RECORDING:
            self.view.startStopButton.setText("Stop")
            self.view.startStopButton.setEnabled(True)
            self.recording_status = 2
        elif status == RECORDING_STATUS.READY or status == RECORDING_STATUS.INITIALIZED:
            self.view.startStopButton.setText("Start Recording")
            self.view.startStopButton.setEnabled(True)
            self.recording_status = 1
        else:
            self.view.startStopButton.setText("Start")
            self.view.startStopButton.setEnabled(True)
            self.recording_status = 0

    def playNotification():
        BuzzerPin = 23

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BuzzerPin, GPIO.OUT, initial=GPIO.LOW)

        GPIO.output(BuzzerPin, GPIO.HIGH)
        time.sleep(0.5)
        print("Beep")
        GPIO.output(BuzzerPin, GPIO.LOW)
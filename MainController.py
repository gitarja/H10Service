from PyQt5 import QtCore, QtWidgets
import sys
from MainUI import Ui_MainWindow
from Lib.Sensor import SensorScanner
from Lib.Conf import ECG, TTL, BUZZER, VICON
from Lib.Sender import UDPReceiver, TTLSender, TCPSender
import serial
from PyQt5.QtCore import QThread
import RPi.GPIO as GPIO
import time


class MainController:

    def __init__(self, is_ttl: bool = False, is_ECG: bool = False):
        self.app = QtWidgets.QApplication(sys.argv)
        self.view = Ui_MainWindow()


        self.is_ttl = is_ttl
        self.is_ECG = is_ECG
        self.ECG_recording = False

        # set status for Vicon and ECG
        self.ecg_status = ECG.STATUS.SEARCHING_SENSORS
        self.vicon_status = VICON.STATUS.READY
        if self.is_ttl:
            self.updateRecordingStatus()
        # view controller
        self.view.startStopButton.clicked.connect(self.startStopRecording)

        # ECG
        if self.is_ECG:
            self.scanner = SensorScanner()
            self.scanner.status_update.connect(self.showStatus)
            self.scanner.sensor_client.recording_status.connect(self.updateECG)
            self.scanner.sensor_client.status_update.connect(self.showStatus)
            self.scanner.sensor_client.rr_value.connect(self.updateStatusBar)


        # vicon
        self.udp_send_read = UDPReceiver()
        self.udp_send_read.is_started.connect(self.updateVicon)
        self.udp_send_read.start(priority=QThread.HighestPriority)

        if self.is_ttl:
            # ttl sender
            self.ttl_sender = TTLSender()
            # set serial for TTL sender
            self.ser = serial.Serial(
                port=TTL.PORT,  # please make sure the port name is correct
                baudrate=115200,  # maximum baud rate 115200
                bytesize=serial.EIGHTBITS,  # set this to the amount of data you want to send
                stopbits=serial.STOPBITS_ONE,
            )

        # TCP sender

        self.tcp_sender = TCPSender()





    @property
    def ecg_status(self):
        return self._ecg_status

    @ecg_status.setter
    def ecg_status(self, value):
        self._ecg_status = value

    def updateECG(self, value):
        if value == ECG.STATUS.FAILED_TO_CONNECT:
            self.scanner.sensor_client.resetClient()
            self.scanner.scan()
        self.ecg_status = value
        if value == ECG.STATUS.STOP:
            self.ecg_status = ECG.STATUS.READY
        self.updateRecordingStatus()

    @property
    def vicon_status(self):
        return self._vicon_status

    @vicon_status.setter
    def vicon_status(self, value):
        self._vicon_status = value

    def updateStatusBar(self, val):
        self.view.statusbar.showMessage("IBI: "+str(val) )

    def updateVicon(self, value):
        if value == VICON.STATUS.START or value == VICON.STATUS.STOP:
            self.vicon_status = value
            self.startStopRecording()

        if value == VICON.STATUS.STOP:
            self.vicon_status = VICON.STATUS.READY
        self.updateRecordingStatus()

    def run(self):
        self.view.show()
        if self.is_ECG:
            self.scanner.scan()
        return self.app.exec_()

    def sendTCPEvenets(self):
        self.tcp_sender.send("http://tg03b-080201127411/")

    def startStopRecording(self):
        '''
        TTL sender is
        '''

        if self.vicon_status == VICON.STATUS.START:
            # a controll for ECG mode only
            if self.is_ECG and self.is_ttl:
                # send ttl
                self.ttl_sender.send(self.ser)
                # send TCP
                self.sendTCPEvenets()
                # start recording
                self.scanner.startRecording()
                self.playNotification()
            elif self.is_ECG and not self.is_ttl:
                self.scanner.startRecording()
                self.playNotification()
            else:
                # send ttl
                self.ttl_sender.send(self.ser)
                # send TCP
                self.sendTCPEvenets()

                self.playNotification()

        elif self.vicon_status == VICON.STATUS.STOP:
            if self.is_ECG and self.is_ttl:
                # send ttl
                self.ttl_sender.send(self.ser)
                # send TCP
                self.sendTCPEvenets()
                self.scanner.stopRecording()
                self.playNotification()
            elif self.is_ECG and not self.is_ttl:
                self.scanner.stopRecording()
                self.playNotification()
            else:
                # send ttl
                self.ttl_sender.send(self.ser)
                # send TCP
                self.sendTCPEvenets()
                self.playNotification()



    def showStatus(self, msg):
        self.view.statusbar.showMessage(msg)

    def updateRecordingStatus(self):
        # ECG mode
        if self.is_ECG:
            if self.ecg_status == ECG.STATUS.SEARCHING_SENSORS:
                self.view.startStopButton.setEnabled(False)
                self.ECG_recording = False
            elif self.ecg_status == ECG.STATUS.RECORDING:
                self.view.startStopButton.setText("Recording")
                self.view.startStopButton.setStyleSheet("background-color: yellow")
                self.view.startStopButton.setEnabled(False)
                self.ECG_recording = True
            elif (self.ecg_status == ECG.STATUS.READY):
                self.view.startStopButton.setText("Ready")
                self.view.startStopButton.setStyleSheet("background-color: green")
                self.view.startStopButton.setEnabled(False)
                self.ECG_recording = False
            else:
                self.view.startStopButton.setText("Start")
                self.view.startStopButton.setStyleSheet("background-color: blue")
                self.view.startStopButton.setEnabled(True)
                self.ECG_recording = False
        else:
            # TTL mode
            if self.vicon_status == VICON.STATUS.READY:
                self.view.startStopButton.setText("Ready")
                self.view.startStopButton.setStyleSheet("background-color: green")
                self.view.startStopButton.setEnabled(False)
            if self.vicon_status == VICON.STATUS.START:
                self.view.startStopButton.setText("Recording")
                self.view.startStopButton.setStyleSheet("background-color: yellow")
                self.view.startStopButton.setEnabled(False)

    def playNotification(self):

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(BUZZER.PIN, GPIO.OUT, initial=GPIO.LOW)

        GPIO.output(BUZZER.PIN, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(BUZZER.PIN, GPIO.LOW)

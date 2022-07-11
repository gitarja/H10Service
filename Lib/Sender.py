import time
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
from Lib.Conf import VICON

import socket
from threading import Event
import serial

HIGH = 255
LOW = 0

def timeNow():
    timenow = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
    return timenow


class TTLSender(QThread):

    run_output = pyqtSignal(int)
    time = Event()

    def __init__(self):
        QThread.__init__(self)
        self._isRunning = False

    def setSerial(self, ser: serial.Serial):
        self.ser = ser

    def run(self) -> None:
        # send the information we want to send
        # to start, we need A rising edge (or positive edge) is the low-to-high transition

        print("sending ttl at: " + timeNow())
        self.ser.write(HIGH)
        self.time.wait(100. / 1000)
        self.ser.write(LOW)
        self.playNotification()

    def stop(self):
        self._isRunning = False
        self.time.set()
        self.time.clear()
        self.run_output.emit(0)


class SendReadUDP(QThread):
    is_started = pyqtSignal(int)
    capture_start = False

    def __init__(self, is_read: bool = True):
        QThread.__init__(self)
        print("Init socket binding")
        self.is_read = is_read
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP


    def read(self):

        self.sock.bind(("", VICON.UDP_PORT))
        self.sock.setblocking(0)
        while True:
            try:
                # Attempt to receive up to 1024 bytes of data
                data, addr = self.sock.recvfrom(300)
                # print(data)
                # Echo the data back to the sender
                if "CaptureStart" in data.decode("utf-8") and not self.capture_start:
                    print("Nexus is started at: " + timeNow())
                    self.is_started.emit(1)
                    self.capture_start = True
                    # break
                elif "CaptureStop" in data.decode("utf-8") and self.capture_start:
                    print("Nexus is stop at: " + timeNow())
                    self.is_started.emit(1)
                    self.capture_start = False

            except socket.error:
                # If no data is received, you get here, but it's not an error
                # Ignore and continue
                pass
            time.sleep(1. / 10000000)

    def run(self) -> None:
        self.read()

    def stop(self):
        self.sock.detach()
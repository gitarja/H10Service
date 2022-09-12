import time
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
import socket
from PyQt5.QtCore import QObject
from Lib.Conf import VICON
import serial
from time import perf_counter

HIGH = 1
LOW = 0


def timeNow():
    timenow = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
    return timenow


class TTLSender(QObject):

    def setSerial(self, ser: serial.Serial):
        self.ser = ser

    def send(self) -> None:
        # send the information we want to send
        # to start, we need A rising edge (or positive edge) is the low-to-high transition

        print("Sending ttl at: " + timeNow())
        self.ser.write(LOW)
        self.ser.write(HIGH)
        t1 = perf_counter()
        while perf_counter() - t1 < (100./1000):
            None
        self.ser.write(LOW)
        self.ser.write(HIGH)


class UDPSender(object):

    def __init__(self):
        print("Init socket binding")
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                  socket.SOCK_DGRAM)  # UDP
        self.packet_ID = 0

    def send(self, trial_name, database_path, start=True):
        self.packet_ID += 1
        #### get current time in format HHMMSS
        timenow = datetime.datetime.now().time().strftime("%H%M%S")
        #### simple message, please note the variables. Using the current time allows
        #### having unique ID for the trial. If the recording exist with the current
        #### file name, the recording won't start unless in Nexus the "Permit overwrite
        #### existing files" is ticked.
        if start:
            test_message = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>" \
                           "<CaptureStart>" \
                           "<Name VALUE=\"" + trial_name + "\"/>" \
                                                                                     "<Notes VALUE=\"\"/>" \
                                                                                     "<Description VALUE=\"\"/>" \
                                                                                     "<DatabasePath VALUE=\""+VICON.DATABASE_PATH+"\"/>" \
                                                                                     "<Delay VALUE = \"-20\"/>" \
                                                                                     "<PacketID VALUE=\"" + str(
                self.packet_ID) + "\"/>" \
                             "</CaptureStart>"
        else:
            test_message = "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>" \
                           "<CaptureStop RESULT=\"SUCCESS\">" \
                           "<Name VALUE=\"" + trial_name + "\"/>" \
                                                                                     "<Notes VALUE=\"\"/>" \
                                                                                     "<Description VALUE=\"\"/>" \
                                                                                     "<DatabasePath VALUE=\""+VICON.DATABASE_PATH+"\"/>" \
                                                                                     "<Delay VALUE = \"-20\"/>" \
                                                                                     "<PacketID VALUE=\"" + str(
                self.packet_ID) + "\"/>" \
                                  "</CaptureStop>"

        try:
            self.sock.sendto(test_message.encode(), (VICON.UDP_IP, VICON.UDP_PORT))
        except socket.error:
            print("Cannot send UDP message to Nexus")
            raise


class UDPReceiver(QThread):
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
                # Attempt to receive up to 300 bytes of data
                data, addr = self.sock.recvfrom(300)
                # print(data)
                # Echo the data back to the sender
                if "CaptureStart" in data.decode("utf-8") and not self.capture_start:
                    print("Nexus is started at: " + timeNow())
                    self.is_started.emit(VICON.STATUS.START)
                    self.capture_start = True
                    # break
                elif "CaptureStop" in data.decode("utf-8") and self.capture_start:
                    print("Nexus is stop at: " + timeNow())
                    self.is_started.emit(VICON.STATUS.STOP)
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

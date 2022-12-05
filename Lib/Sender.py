import time
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
import socket
from PyQt5.QtCore import QObject
from Lib.Conf import VICON, ECG
import serial
from time import perf_counter
import requests
import json

HIGH = 1
LOW = 0


def timeNow():
    timenow = datetime.datetime.now().time().strftime("%H:%M:%S.%f")
    return timenow


class TTLSender(QObject):



    def send(self, ser) -> None:
        # send the information we want to send
        # to start, we need A rising edge (or positive edge) is the low-to-high transition
        if not ser.isOpen():
            ser.open()
        with open(ECG.RECORDING_PATH + "log.txt", "a") as myfile:
            myfile.write("\nSending ttl at: " + timeNow())
        print("Sending ttl at: " + timeNow())
        ser.write(HIGH)
        t1 = perf_counter()
        while perf_counter() - t1 < (200./1000):
            None
        ser.write(HIGH)

        # close serial
        ser.close()




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


class TCPSender:

    def __init__(self):
        self.start_event =  [
            "start-stop-event",
            {
                "time":datetime.datetime.now().timestamp(),
            }
        ]
        self.stop_event = [
            "stop-event",
            {
                "time":datetime.datetime.now().timestamp(),
            }
        ]



    def send(self, tobii_url, start=True):
        rest_url = tobii_url + "rest/recorder!send-event"

        data = self.start_event
        if start == False:
            data = self.stop_event
        try:
            r = requests.post(url=rest_url, data=json.dumps(data))
            return r
        except requests.exceptions.HTTPError as errh:
            print("Cannot connect")
        except requests.exceptions.ConnectionError as errc:
            print("Cannot connect")
        except requests.exceptions.Timeout as errt:
            print("Cannot connect")
        except requests.exceptions.RequestException as err:
            print("Cannot connect")


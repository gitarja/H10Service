import time

from PyQt5.QtCore import QObject, pyqtSignal, QByteArray, Qt, QTimer
from PyQt5.QtBluetooth import (QBluetoothDeviceDiscoveryAgent,
                                 QLowEnergyController, QLowEnergyService,
                                 QBluetoothUuid)

from Lib.Logger import Logger
from math import ceil
from datetime import datetime
from Lib.Conf import ECG


def currentDateTime()-> str:
    date_time = str(datetime.now())
    date_time = date_time.replace(" ", "_")
    date_time = date_time.replace("-", "")
    date_time = date_time.replace(":", "")
    date_time = date_time.replace(".", "")
    return date_time



class SensorScanner(QObject):

    '''
    this class is a modified version of OpenHRV: https://github.com/JanCBrammer/OpenHRV
    '''

    sensor_update = pyqtSignal(object)
    status_update = pyqtSignal(str)


    def __init__(self):
        super().__init__()
        self.scanner = QBluetoothDeviceDiscoveryAgent()
        self.sensor_client = SensorClient()
        self.sensor = None
        self.scanner.finished.connect(self._handle_scan_result) # trigger the function when scanner is finished
        self.scanner.error.connect(self._handle_scan_error)
        # self.scanner.errorOccurred.connect(self._handle_scan_error)

    def scan(self):
        if self.scanner.isActive():
            self.status_update.emit("Searching for sensors (this might take a while).")

            return
        self.status_update.emit("Searching for sensors (this might take a while).")
        self.sensor_client.recording_status.emit(ECG.STATUS.SEARCHING_SENSORS)
        self.scanner.start()


    def startRecording(self):
        if self.sensor != None:
            self.sensor_client.startRecording()
        else:
            self.scan()

    def stopRecording(self):
        self.status_update.emit("Recording complete")
        self.sensor_client.recording_status.emit(ECG.STATUS.STOP)
        self.sensor_client.start_recording = False


    def _handle_scan_result(self):
        polar_sensors = [d for d in self.scanner.discoveredDevices()
                         if "Polar" in str(d.name())]    # TODO: comment why rssi needs to be negative
        if not polar_sensors:
            self.status_update.emit("Couldn't find sensors.")
            self.sensor_client.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)

            return
        self.sensor = polar_sensors[0] # take the first sensor
        self.status_update.emit("Sensor is ready")
        self.sensor_client.recording_status.emit(ECG.STATUS.READY)
        self.sensor_client.connect_client(self.sensor)


    def _handle_scan_error(self, error):
        self.status_update.emit("Error")
        self.sensor_client.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)


class SensorClient(QObject):
    """
    Connect to a Polar sensor that acts as a Bluetooth server / peripheral.
    On Windows, the sensor must already be paired with the machine running
    OpenHRV. Pairing isn't implemented in Qt6.

    In Qt terminology client=central, server=peripheral.
    """
    rr_status = pyqtSignal(bool)
    status_update = pyqtSignal(str)
    recording_status = pyqtSignal(int)
    start_recording = False


    def __init__(self):
        super().__init__()

        self.log =  Logger()
        self.client = None
        self.hr_service = None
        self.hr_notification = None
        self.sensor = None
        self.ENABLE_NOTIFICATION = QByteArray.fromHex(b"0100")
        self.DISABLE_NOTIFICATION = QByteArray.fromHex(b"0000")
        self.HR_SERVICE = QBluetoothUuid.HeartRate
        self.HR_CHARACTERISTIC = QBluetoothUuid.HeartRateMeasurement

        self.rr_count = 0

    def _sensor_address(self):
        return self.client.remoteAddress().toString()

    def connect_client(self, sensor):
        if self.client:
            msg = f"Currently connected to sensor at {self._sensor_address()}." \
                   " Please disconnect before (re-)connecting to (another) sensor."
            self.status_update.emit(msg)
            return


        # connecting to the sensor
        self.status_update.emit(f"Connecting to sensor at {sensor.address().toString()}.")
        self.client = QLowEnergyController.createCentral(sensor)
        self.client.error.connect(self._catch_error)
        # self.client.errorOccurred.connect(self._catch_error)
        self.client.connected.connect(self._discover_services)
        self.client.discoveryFinished.connect(self._connect_hr_service, Qt.QueuedConnection)
        self.client.disconnected.connect(self.resetClient)
        self.client.connectToDevice()

    def disconnect_client(self):
        if self.hr_notification and self.hr_service:
            if not self.hr_notification.isValid():
                return
            print("Unsubscribing from HR service.")
            self.hr_service.writeDescriptor(self.hr_notification, self.DISABLE_NOTIFICATION)
        if self.client:
            self.status_update.emit(f"Disconnecting from sensor at {self._sensor_address()}.")
            self.client.disconnectFromDevice()

    def _discover_services(self):
        self.client.discoverServices()

    def _connect_hr_service(self):
        hr_service = [s for s in self.client.services() if s.toUInt16()[0] == self.HR_SERVICE]
        if not hr_service:
            self.status_update.emit(f"Couldn't find HR service on {self._sensor_address()}.")
            self.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)
            return
        self.hr_service = self.client.createServiceObject(*hr_service)
        if not self.hr_service:
            self.status_update.emit(f"Couldn't establish connection to HR service on {self._sensor_address()}.")
            return

        # create a service and connect to it
        self.hr_service.stateChanged.connect(self._start_hr_notification)
        self.hr_service.characteristicChanged.connect(self._data_handler)
        self.hr_service.discoverDetails()



    def startRecording(self):
        self.status_update.emit("Recording")
        self.log.initializeLog(ECG.RECORDING_PATH + str(currentDateTime()) + ".csv")
        self.recording_status.emit(ECG.STATUS.RECORDING)
        self.start_recording = True



    def _start_hr_notification(self, state):
        # if state != QLowEnergyService.RemoteServiceDiscovered:
        if state != QLowEnergyService.ServiceDiscovered:
            return
        hr_char = self.hr_service.characteristic(QBluetoothUuid(QBluetoothUuid.HeartRateMeasurement))
        # hr_char = self.hr_service.characteristic(self.HR_CHARACTERISTIC)
        if not hr_char.isValid():
            self.status_update.emit(f"Couldn't find HR characterictic on {self._sensor_address()}.")
        self.hr_notification = hr_char.descriptor(QBluetoothUuid(QBluetoothUuid.DescriptorType.ClientCharacteristicConfiguration))
        if not self.hr_notification.isValid():
            self.status_update.emit("HR characteristic is invalid.")
        self.hr_service.writeDescriptor(self.hr_notification, self.ENABLE_NOTIFICATION)

    def resetClient(self):
        self.status_update.emit(f"Discarding sensor at {self._sensor_address()}.")

        self._remove_service()
        self._remove_client()

    def _remove_service(self):
        try:
            self.hr_service.deleteLater()
        except Exception as e:
            self.status_update.emit(f"Couldn't remove service: {e}")
            self.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)
        finally:
            self.hr_service = None
            self.hr_notification = None

    def _remove_client(self):
        try:
            self.client.disconnected.disconnect()
            self.client.deleteLater()
        except Exception as e:
            self.status_update.emit(f"Couldn't remove client: {e}")
            self.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)
        finally:
            self.client = None

    def _catch_error(self, error):
        self.status_update.emit(f"An error occurred: {error}. Disconnecting sensor.")
        self.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)
        self.resetClient()

    def _data_handler(self, characteristic, data):    # characteristic is unused but mandatory argument


        """
        `data` is formatted according to the
        "GATT Characteristic and Object Type 0x2A37 Heart Rate Measurement"
        which is one of the three characteristics included in the
        "GATT Service 0x180D Heart Rate".

        `data` can include the following bytes:
        - flags
            Always present.
            - bit 0: HR format (uint8 vs. uint16)
            - bit 1, 2: sensor contact status
            - bit 3: energy expenditure status
            - bit 4: RR interval status
        - HR
            Encoded by one or two bytes depending on flags/bit0. One byte is
            always present (uint8). Two bytes (uint16) are necessary to
            represent HR > 255.
        - energy expenditure
            Encoded by 2 bytes. Only present if flags/bit3.
        - inter-beat-intervals (IBIs)
            One IBI is encoded by 2 consecutive bytes. Up to 18 bytes depending
            on presence of uint16 HR format and energy expenditure.
        """


        data = data.data()    # convert from QByteArray to Python bytes

        byte0 = data[0]
        uint8_format = (byte0 & 1) == 0
        energy_expenditure = ((byte0 >> 3) & 1) == 1
        rr_interval = ((byte0 >> 4) & 1) == 1


        print(self.rr_count)
        if not rr_interval:
            time.sleep(0.5)
            self.rr_count += 1
            if self.rr_count > 5: # if the program fails 5 times to fetch the RR
                self.recording_status.emit(ECG.STATUS.FAILED_TO_CONNECT)
            return

        self.rr_count = 0
        first_rr_byte = 2
        if uint8_format:
            # hr = data[1]
            pass
        else:
            # hr = (data[2] << 8) | data[1] # uint16
            first_rr_byte += 1
        if energy_expenditure:
            # ee = (data[first_rr_byte + 1] << 8) | data[first_rr_byte]
            first_rr_byte += 2

        # eliminate doubles rr
        if len(data) > 4:
            first_rr_byte += 2
        for i in range(first_rr_byte, len(data), 2):
            record_time = datetime.now()
            ibi = (data[i + 1] << 8) | data[i]
            # Polar H7, H9, and H10 record IBIs in 1/1024 seconds format.
            # Convert 1/1024 sec format to milliseconds.
            # TODO: move conversion to model and only convert if sensor doesn't
            # transmit data in milliseconds.
            ibi = ceil(ibi / 1024 * 1000)
            # write rr into a csv file
            if self.start_recording:
                self.log.write(ibi, record_time)


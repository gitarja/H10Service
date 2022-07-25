import yaml
from yaml.loader import SafeLoader
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "Settings.yml") as f:
    settings = yaml.load(f, Loader=SafeLoader)

# Vicon setting
class VICON:
    DATABASE_PATH = settings["VICON"]["DATABASE_PATH"]
    TRIAL_NAME = settings["VICON"]["TRIAL_NAME"]
    UDP_IP = settings["VICON"]["UDP_IP"]  # address to send UDP, assigned in NEXUS Recording
    UDP_PORT = settings["VICON"]["UDP_PORT"]  # port assigned in NEXUS Recording
    class STATUS:
        READY = settings["VICON"]["STATUS"]["READY"]
        RECORDING = settings["VICON"]["STATUS"]["RECORDING"]


# ECG status
class ECG:
    RECORDING_PATH = settings["ECG"]["RECORDNING_PATH"]
    class STATUS:
        SEARCHING_SENSORS = settings["ECG"]["STATUS"]["SEARCHING_SENSORS"]
        READY = settings["ECG"]["STATUS"]["READY"]
        RECORDING = settings["ECG"]["STATUS"]["RECORDING"]
        FAILED_TO_CONNECT = settings["ECG"]["STATUS"]["FAILED_TO_CONNECT"]
        INITIALIZED = settings["ECG"]["STATUS"]["INITIALIZED"]

# TTL
class TTL:
    PORT = settings["TTL"]["PORT"]


# Buzzer
class BUZZER:
    PIN = settings["BUZZER"]["PIN"]
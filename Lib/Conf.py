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


# Recording status
class RECORDING_STATUS:
    SEARCHING_SENSORS = settings["RECORDING_STATUS"]["SEARCHING_SENSORS"]
    READY = settings["RECORDING_STATUS"]["READY"]
    RECORDING = settings["RECORDING_STATUS"]["RECORDING"]
    FAILED_TO_CONNECT = settings["RECORDING_STATUS"]["FAILED_TO_CONNECT"]
    INITIALIZED = settings["RECORDING_STATUS"]["INITIALIZED"]

# Recording
class RECORDING:
    PATH = settings["RECORDING"]["PATH"]


# TTL
class TTL:
    PORT = settings["TTL"]["PORT"]


# Buzzer
class BUZZER:
    PIN = settings["BUZZER"]["PIN"]
import yaml
from yaml.loader import SafeLoader
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "Settings.yml") as f:
    settings = yaml.load(f, Loader=SafeLoader)

# Vicon setting
class VICON:
    # Open the file and load the file
    DATABASE_PATH = settings["VICON"]["DATABASE_PATH"]
    TRIAL_NAME = settings["VICON"]["TRIAL_NAME"]
    UDP_IP = settings["VICON"]["UDP_IP"]  # address to send UDP, assigned in NEXUS Recording
    UDP_PORT = settings["VICON"]["UDP_PORT"]  # port assigned in NEXUS Recording

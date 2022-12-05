#! /bin/sh

if sudo bluetoothctl -- trust F9:04:90:1C:DB:0A; then

	if sudo bluetoothctl -- connect F9:04:90:1C:DB:0A; then
		sudo python main.py --ttl True --ECG True
	fi
fi

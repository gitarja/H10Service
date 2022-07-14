#! /bin/sh

if sudo bluetoothctl -- trust dd:4e:fa:3f:78:00; then

	if sudo bluetoothctl -- connect dd:4e:fa:3f:78:00; then
		sudo python main.py --ttl False
	fi
fi

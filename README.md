# OLA powered DMX Light Composition on a Raspberry Pi.

## Project 'Ricochet' by Jesus Hilario-Reyes.

## Engineering by Jeremy Wiles-Young.

A python structure to run lighting compositions in real time.

The Set Up:

- Raspberry Pi 3B+
- ENNTEC OPEN DMX

Rough Directions for the Raspberry Pi setup:

# 1. Create OLA systemd service

# /etc/systemd/system/olad.service

[Unit]
Description=Open Lighting Architecture Daemon
After=network.target
Before=dmx-composition.service

[Service]
Type=simple
ExecStart=/usr/bin/olad -f
Restart=always
User=root

[Install]
WantedBy=multi-user.target

# 2. Create your composition service

# /etc/systemd/system/dmx-composition.service

[Unit]
Description=DMX Light Composition
After=olad.service
Requires=olad.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/your/composition.py
WorkingDirectory=/path/to/your/directory
User=pi
Restart=always

[Install]
WantedBy=multi-user.target

# 3. Create udev rule for Enttec USB device

# /etc/udev/rules.d/10-dmx.rules

SUBSYSTEM=="usb", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", MODE="0666", GROUP="dialout"

# 4. Commands to enable everything:

sudo systemctl daemon-reload
sudo systemctl enable olad.service
sudo systemctl enable dmx-composition.service
sudo udevadm control --reload-rules
sudo udevadm trigger

# PiBeacon

This project was build during the module "Software Engineering Basics II" from the crystal team in course TIF14A.

Team Members:

* Christian Schlegel
* Daniel Haß
* Henrik Schaffhauser
* Tobias Zeiser

## Goal

Implementing a Bluetooth Low Energy Beacon based on the RaspberryPi 3 platform.
Several beacon standards are supported:

* Apple iBeacon
    * https://developer.apple.com/ibeacon/
* AltBeacon
    * http://altbeacon.org
* Google Eddystone Beacon
    * https://developers.google.com/beacons/
* DHBW Beacon
    * A custom beacon standard based on Eddystone UID & TLM frames

## Requirements

### Hardware

* RaspberryPi No. 3

### Software

* Raspbian (Debian based Linux)
    * https://www.raspbian.org
* BlueZ (Linux Standard HCI Interface) v5.23-2
    * bluez-hcidump
* Qt4 v4.11.2
    * python3-pyqt4 (Qt4 Python bindings)

## Usage

### Install required software

```
sudo apt-get install python3-pyqt4 bluez-hcidump
```

### Permissions

Run the setup-permissions script as follows to apply the correct permissions to run PiBeacon with a normal user:

```
sudo setup-permissions.sh
```

### Autostart GUI

To activate the automatic startup of PiBeacon in LXDE (which is the default desktop environment on the Raspberry) put the following line into this file:

``` /home/pi/.config/lxsession/LXDE-pi/autostart ```

```
@python3 <path/to/the/controller.py>
```

### GUI Mode

Run the ```src/controller.py``` without any arguments to run the PiBeacon in GUI mode.
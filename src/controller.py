#!/usr/bin/env python3

#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : main
#  --------------------------------------------------------------
#   Autor(en)       : Daniel Haß
#   Beginn-Datum    : 18.07.16
#  --------------------------------------------------------------
#   Beschreibung    : Main class of the project
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#   09.08.2016           tz    Hinzufügen der Funktion die die Standardeinstellungen für die Config bereitstellt
#  --------------------------------------------------------------
import sys
import subprocess
import os.path

from comm.intcomm import IntComm
from comm.intmessage import IntMessage
from beacon.pibeacon import PiBeacon
from utils.debug import DBG
from gui.gui import Gui
from scanner.scannerble import ScannerBLE
from scanner.scannerbt import ScannerBT
from conf.config import BeaconConfig


class Controller(IntComm):

    _pibeacon = None
    _scannerble = None
    _scannerbt = None
    _gui = None
    _config = None

    # default values for different beacon types
    _default_ibeacon = {'UUID': 'e20a39f4-73f5-4bc4-a12f-17d1ad07a961',
                        'MAJOR': '0',
                        'MINOR': '0',
                        'TX': '-60',
                        'INTERVAL': '1280'}

    _default_altbeacon = {'BID': 'e20a39f473f54bc4a12f17d1ad07a96100000000',
                          'RSSI': '-60',
                          'MFG': '01',
                          'INTERVAL': '1280'}

    _default_eddystone = {'NID': 'e20a39f473f54bc4a12f',
                          'IID': '17d1ad07a961',
                          'TX': '-60',
                          'INTERVAL': '1280'}

    _default_dhbwbeacon = {'NID': 'e20a39f473f54bc4a12f',
                           'IID': '17d1ad07a961',
                           'TX': '-60',
                           'INTERVAL': '1280'}

    _alert_scan = {'ALERT_TEXT': "Beacon is running, can't scan!",
                   'ALERT_DETAIL': "There is a Beacon running in background. Please stop it to allow scanning."}

    def __init__(self):
        Controller.check_bt_enabled()

        Controller.check_permissions()  # check for correct permissions on the needed executables

        self._config = Controller.init_config()  # initialize the config

        self._pibeacon = PiBeacon(self.beacon_comm, self._config.General_dict['BLUETOOTH_DEVICE'])
        self._scannerble = ScannerBLE(self.scanner_comm, self._config.General_dict['BLUETOOTH_DEVICE'])
        self._scannerbt = ScannerBT(self.scanner_comm, self._config.General_dict['BLUETOOTH_DEVICE'])

        # check if we run in cli mode
        #if len(sys.argv) > 1:
        #    if sys.argv[1] == "--cli" or sys.argv[1] == "--help":
        #        self.cli()
        # start the gui if not running in cli mode
        #else:
        #    self._gui = Gui(self.gui_comm, self._config)
        #    self._gui.start_gui()

        self._gui = Gui(self.gui_comm, self._config)
        self._gui.start_gui()

    def comm(self, msg):
        pass

    '''
    # checks given CLI arguments
    def cli(self):
        DBG("Running in cli mode")

        if sys.argv[1] == "--help":
            Controller.print_cli_help()
            exit()
        elif sys.argv[2] == "--ibeacon":
            msg = IntMessage(IntMessage.START_IBEACON, self._config.IBeacon_dict)
        elif sys.argv[2] == "--eddystone":
            msg = IntMessage(IntMessage.START_EDDYSTONE, self._config.Eddystone_dict)
        elif sys.argv[2] == "--altbeacon":
            msg = IntMessage(IntMessage.START_ALTBEACON, self._config.AltBeacon_dict)
        elif sys.argv[2] == "--dhbw":
            msg = IntMessage(IntMessage.START_DHBWBEACON, self._config.DHBWBeacon_dict)
        elif sys.argv[2] == "--scanble":
            self._scannerble.scan()
            input("Press key to stop...")
            self._scannerble.stop_scan()
            exit()
        elif sys.argv[2] == "--scanbt":
            self._scannerbt.scan()
            exit()
        else:
            Controller.print_cli_help()
            exit()

        self.gui_comm(msg)
        input("Beacon running. Press key to exit...")
        msg = IntMessage(IntMessage.STOP_BEACON)
        self.gui_comm(msg)
    '''

    # messages from beacons
    def beacon_comm(self, msg):
        if msg.get_type() is IntMessage.BEACON_DATA_ERROR:  # pass input error back to GUI
            self._gui.comm(IntMessage(IntMessage.ALERT_GUI, {'ALERT_TEXT': "Your input is not correct!",
                                                             'ALERT_DETAIL': msg.get_payload()['ERROR']}))
        elif msg.get_type() is IntMessage.SIGNAL_IBEACON or \
                msg.get_type() is IntMessage.SIGNAL_EDDYSTONE or \
                msg.get_type() is IntMessage.SIGNAL_ALTBEACON or \
                msg.get_type() is IntMessage.SIGNAL_DHBWBEACON:
            signal_hex = msg.get_payload()['DATA']
            DBG("Current Signal: " + str(signal_hex))
            self._gui.comm(IntMessage(msg.get_type(), {'TEXT': signal_hex}))

    # messages from GUI
    def gui_comm(self, msg):
        if not isinstance(msg, IntMessage):
            raise Exception("Message has to be an IntMessage")
        msg_type = msg.get_type()
        pl = msg.get_payload()

        # start different beacon standards
        if msg_type is IntMessage.START_IBEACON:
            DBG('Started iBeacon')
            self._pibeacon.start_ibeacon(pl['UUID'], pl['MAJOR'], pl['MINOR'], pl['TX'], pl['INTERVAL'])
        elif msg_type is IntMessage.START_ALTBEACON:
            self._pibeacon.start_altbeacon(pl['BID'], pl['RSSI'], pl['MFG'], pl['INTERVAL'])
        elif msg_type is IntMessage.START_EDDYSTONE:
            DBG('Started Eddystone Beacon')
            self._pibeacon.start_eddystone(pl['NID'], pl['IID'], pl['TX'], pl['INTERVAL'])
        elif msg_type is IntMessage.START_DHBWBEACON:
            DBG('Started DHBW Beacon')
            self._pibeacon.start_dhbw_beacon(pl['NID'], pl['IID'], pl['TX'], pl['INTERVAL'])
        elif msg_type is IntMessage.STOP_BEACON:
            DBG('Stopped Beacon')
            self._pibeacon.stop()
        elif msg_type is IntMessage.START_SCAN_BLE:
            if not self._pibeacon.is_running():
                DBG('Started BLE Scan')
                self._scannerble.scan()
            else:
                self._gui.comm(IntMessage(IntMessage.ALERT_GUI, Controller._alert_scan))
        elif msg_type is IntMessage.STOP_SCAN_BLE:
            DBG('Stopped BLE Scan')
            self._scannerble.stop_scan()
        elif msg_type is IntMessage.START_SCAN_BT:
            if not self._pibeacon.is_running():
                DBG('Started BT Scan')
                self._scannerbt.scan()
            else:
                self._gui.comm(IntMessage(IntMessage.ALERT_GUI, Controller._alert_scan))
        elif msg_type is IntMessage.RESET_IBEACON:
            msg = IntMessage(IntMessage.RESET_IBEACON, Controller._default_ibeacon)
            self._gui.comm(msg)
        elif msg_type is IntMessage.RESET_ALTBEACON:
            msg = IntMessage(IntMessage.RESET_ALTBEACON, Controller._default_altbeacon)
            self._gui.comm(msg)
        elif msg_type is IntMessage.RESET_EDDYSTONE:
            msg = IntMessage(IntMessage.RESET_EDDYSTONE, Controller._default_eddystone)
            self._gui.comm(msg)
        elif msg_type is IntMessage.RESET_DHBWBEACON:
            msg = IntMessage(IntMessage.RESET_DHBWBEACON, Controller._default_dhbwbeacon)
            self._gui.comm(msg)
        elif msg_type is IntMessage.GUI_READY:
            self.autostart_beacon()
        elif msg_type is IntMessage.SET_AUTOSTART_IBEACON:
            self._config.save_config(BeaconConfig.General, 'DEFAULT_BEACON', BeaconConfig.IBeacon)
            self._config.save_file()
        elif msg_type is IntMessage.SET_AUTOSTART_ALTBEACON:
            self._config.save_config(BeaconConfig.General, 'DEFAULT_BEACON', BeaconConfig.AltBeacon)
            self._config.save_file()
        elif msg_type is IntMessage.SET_AUTOSTART_DHBWBEACON:
            self._config.save_config(BeaconConfig.General, 'DEFAULT_BEACON', BeaconConfig.DHBWBeacon)
            self._config.save_file()
        elif msg_type is IntMessage.SET_AUTOSTART_EDDYSTONE:
            self._config.save_config(BeaconConfig.General, 'DEFAULT_BEACON', BeaconConfig.Eddystone)
            self._config.save_file()
        elif msg_type is IntMessage.SAVE_IBEACON:
            self._config.save_dict(pl, self._config.IBeacon)
            self._config.save_file()
        elif msg_type is IntMessage.SAVE_ALTBEACON:
            self._config.save_dict(pl, self._config.AltBeacon)
            self._config.save_file()
        elif msg_type is IntMessage.SAVE_DHBWBEACON:
            self._config.save_dict(pl, self._config.DHBWBeacon)
            self._config.save_file()
        elif msg_type is IntMessage.SAVE_EDDYSTONE:
            self._config.save_dict(pl, self._config.Eddystone)
            self._config.save_file()

    # messages from scanner
    def scanner_comm(self,msg):
        DBG("Controller scanned: " + str(msg.get_payload()))
        self._gui.comm(msg) # send scanning data to gui

    def autostart_beacon(self):
        default_beacon = self._config.General_dict['DEFAULT_BEACON']
        if default_beacon == BeaconConfig.IBeacon:
            self.gui_comm(IntMessage(IntMessage.START_IBEACON, self._config.IBeacon_dict))
        elif default_beacon == BeaconConfig.AltBeacon:
            self.gui_comm(IntMessage(IntMessage.START_ALTBEACON, self._config.AltBeacon_dict))
        elif default_beacon == BeaconConfig.Eddystone:
            self.gui_comm(IntMessage(IntMessage.START_EDDYSTONE, self._config.Eddystone_dict))
        elif default_beacon == BeaconConfig.DHBWBeacon:
            self.gui_comm(IntMessage(IntMessage.START_DHBWBEACON, self._config.DHBWBeacon_dict))

    @staticmethod
    def check_bt_enabled():
        hciconfig_bin = subprocess.check_output(['which', 'hciconfig'])
        hciconfig_bin = hciconfig_bin.decode('utf-8').rstrip()
        output = subprocess.check_output(hciconfig_bin)
        if not output:
            DBG('Bluetooth not enabled')
            exit(-1)

    # checks if hcitool, hciconfig and hcidump have the correct permissions
    @staticmethod
    def check_permissions():
        needed_perm = "cap_net_admin,cap_net_raw+eip"  # needed permissions for hci-executables
        hcitool_bin = subprocess.check_output(['which', 'hcitool']) # get current permissions of hcitool
        hcitool_bin = hcitool_bin.decode('utf-8').rstrip()
        hciconfig_bin = subprocess.check_output(['which', 'hciconfig'])  # get current permissions of hciconfig
        hciconfig_bin = hciconfig_bin.decode('utf-8').rstrip()
        hcidump_bin = subprocess.check_output(['which', 'hcidump'])  # get current permissions of hcidump
        hcidump_bin = hcidump_bin.decode('utf-8').rstrip()
        perm1 = subprocess.check_output(['getcap', hcitool_bin])
        perm2 = subprocess.check_output(['getcap', hciconfig_bin])
        perm3 = subprocess.check_output(['getcap', hcidump_bin])

        # check if permissions are correct
        if needed_perm not in str(perm1) or needed_perm not in str(perm2) or needed_perm not in str(perm3):
            print('Permissions of hciconfig and hcitool are not correct!'
                  '\nUse the setup-permissions script to fix this.',
                  file=sys.stderr)
            exit(-1)  # exit with error if permissions are not correct

    # prints help for PiBeacon usage
#    @staticmethod
#    def print_cli_help():
#        print('''
#PiBeacon v0.5.0 - A BLE Beacon based on a RaspberryPi

#Usage: controller.py [OPTIONS]

#Options:
#    <no options>            run PiBeacon in GUI mode
#    --cli [CLI_OPTIONS]     run PiBeacon in CLI mode
#    --help                  prints this help

#CLI-Options:
#    --ibeacon               start iBeacon advertisement
#    --eddystone             start Eddystone advertisement
#    --altbeacon             start AltBeacon advertisement
#    --dhbw                  start DHBW Beacon advertisement
#    --scanble               start scanning for BLE Beacons
#    --scanbt                start scanning for Bluetooth devices
#        ''')

    # Creates the Config.ini and saves the default settings
    @staticmethod
    def init_config():
        DBG("Init config..")
        dir = os.path.expanduser('~') + '/.config/pibeacon/'
        file = 'config.ini'
        path = dir + file
        os.makedirs(dir, exist_ok=True)  # creates directory and file if not existing
        config = BeaconConfig(path)
        # save default values if sections are empty
        if not config.IBeacon_dict:
            config.save_dict(Controller._default_ibeacon, config.IBeacon)
        if not config.AltBeacon_dict:
            config.save_dict(Controller._default_altbeacon, config.AltBeacon)
        if not config.Eddystone_dict:
            config.save_dict(Controller._default_eddystone, config.Eddystone)
        if not config.DHBWBeacon_dict:
            config.save_dict(Controller._default_dhbwbeacon, config.DHBWBeacon)
        if not config.General_dict:
            config.save_dict({'BLUETOOTH_DEVICE': 'hci0', 'DEFAULT_BEACON': BeaconConfig.IBeacon}, config.General)
        config.save_file()
        return config


# start PiBeacon and fire up the controller
def main():
    # start of the program
    DBG("Welcome to PiBeacon!")
    controller = Controller()

# check if we run as main class
if __name__ == '__main__':
    main()

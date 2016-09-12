#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : Scanner
#  --------------------------------------------------------------
#   Autor(en)       : Daniel Haß
#   Beginn-Datum    : 01.08.2016
#  --------------------------------------------------------------
#   Beschreibung    : Scan for nearby bluetooth devices
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------
import subprocess
import threading

from comm.intcomm import IntComm
from comm.intmessage import IntMessage

class ScannerBT():

    _commcallback = None
    _btscan = None
    _hci = None

    def __init__(self, commcallback, hci_dev):
        self._commcallback = commcallback
        self._hci = hci_dev

    def scan(self):
        subprocess.call(["hciconfig", self._hci, 'reset'])  # reset HCI settings
        # start HCI bluetooth scan for pairable devices
        self._btscan = subprocess.Popen(["hcitool", "-i", self._hci, "scan"], stdout=subprocess.PIPE)
        self._commcallback(IntMessage(IntMessage.BT_SCAN, {'TEXT': 'Scan started ...\n'}))
        while self._btscan.poll() is None:  # wait for scan process to finish
            self.read_from_stdout(self._btscan.stdout)
        self.read_from_stdout(self._btscan.stdout)
        self._commcallback(IntMessage(IntMessage.BT_SCAN, {'TEXT': 'Scan finished ...\n'}))

    def read_from_stdout(self, stdout):
        output = stdout.readline().decode()
        # send scanned data to controller
        self._commcallback(IntMessage(IntMessage.BT_SCAN, {'TEXT': output}))

    #def stop_scan(self):
    #    self._btscan.kill()

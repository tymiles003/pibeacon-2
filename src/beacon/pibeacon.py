#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : beacon
#  --------------------------------------------------------------
#   Autor(en)       : Daniel Haß
#   Beginn-Datum    : 18.07.16
#  --------------------------------------------------------------
#   Beschreibung    : Wrapper for different beacon standards
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------
from beacon.ibeacon import IBeacon
from beacon.eddybeacon import EddyBeacon
from beacon.altbeacon import AltBeacon
from beacon.dhbwbeacon import DhbwBeacon
from beacon.hci import HCI
from comm.intcomm import IntComm
from comm.intmessage import IntMessage as IntMsg

class PiBeacon(IntComm):

    _commCallback = None
    _currentBeacon = None
    _running = False
    _hci = None

    def __init__(self, commCallback, ble_dev):
        self._commCallback = commCallback
        self._hci = HCI(ble_dev)

    def comm(self, msg):
        pass

    def start_dhbw_beacon(self, namespace, instance, tx, interval):
        if self._currentBeacon is not None:
            self.stop()
        # we use the Eddystone Beacon validator here cause the DHBW Beacon handles the same values
        check_result = EddyBeacon.check_input(namespace, instance, tx)
        if type(check_result) is str:
            self._commCallback(IntMsg(IntMsg.BEACON_DATA_ERROR, {'ERROR': check_result}))
            return
        self._currentBeacon = DhbwBeacon(namespace, instance, tx, interval, self._hci)
        data = self._currentBeacon.start()
        self._commCallback(IntMsg(IntMsg.SIGNAL_DHBWBEACON, {'DATA': 'Starting DHBWBeacon:\n'+' '.join(data).upper()}))
        self._running = True

    def start_ibeacon(self, uuid, major, minor, tx, interval):
        if self._currentBeacon is not None:
            self.stop()
        check_result = IBeacon.check_input(uuid, major, minor, tx)
        if type(check_result) is str:
            self._commCallback(IntMsg(IntMsg.BEACON_DATA_ERROR, {'ERROR': check_result}))
            return
        self._currentBeacon = IBeacon(uuid, major, minor, tx, interval, self._hci)
        data = self._currentBeacon.start()
        self._commCallback(IntMsg(IntMsg.SIGNAL_IBEACON, {'DATA': 'Starting iBeacon:\n'+' '.join(data).upper()}))
        self._running = True

    def start_eddystone(self, namespace, instance, tx, interval):
        if self._currentBeacon is not None:
            self.stop()
        check_result = EddyBeacon.check_input(namespace, instance, tx)
        if type(check_result) is str:
            self._commCallback(IntMsg(IntMsg.BEACON_DATA_ERROR, {'ERROR': check_result}))
            return
        self._currentBeacon = EddyBeacon(namespace, instance, tx, interval, self._hci)
        data = self._currentBeacon.start()
        self._commCallback(IntMsg(IntMsg.SIGNAL_EDDYSTONE, {'DATA': 'Starting Eddystone:\n'+' '.join(data).upper()}))
        self._running = True

    def start_altbeacon(self, bid, rssi, mfg, interval):
        if self._currentBeacon is not None:
            self.stop()
        check_result = AltBeacon.check_input(bid, rssi, mfg)
        if type(check_result) is str:
            self._commCallback(IntMsg(IntMsg.BEACON_DATA_ERROR, {'ERROR': check_result}))
            return
        self._currentBeacon = AltBeacon(bid, rssi, mfg, interval, self._hci)
        data = self._currentBeacon.start()
        self._commCallback(IntMsg(IntMsg.SIGNAL_ALTBEACON, {'DATA': 'Starting Altbeacon:\n'+' '.join(data).upper()}))
        self._running = True

    def start(self):
        raise NotImplemented
    
    def stop(self):
        if self._currentBeacon is not None:
            self._currentBeacon.stop()
            if isinstance(self._currentBeacon, IBeacon):
                self._commCallback(IntMsg(IntMsg.SIGNAL_IBEACON, {'DATA': 'Stopped Beacon'}))
            elif isinstance(self._currentBeacon, EddyBeacon):
                self._commCallback(IntMsg(IntMsg.SIGNAL_EDDYSTONE, {'DATA': 'Stopped Beacon'}))
            elif isinstance(self._currentBeacon, AltBeacon):
                self._commCallback(IntMsg(IntMsg.SIGNAL_ALTBEACON, {'DATA': 'Stopped Beacon'}))
            elif isinstance(self._currentBeacon, DhbwBeacon):
                self._commCallback(IntMsg(IntMsg.SIGNAL_DHBWBEACON, {'DATA': 'Stopped Beacon'}))
            self._running = False

    def is_running(self):
        return self._running

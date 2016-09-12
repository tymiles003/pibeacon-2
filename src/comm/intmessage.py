#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           :
#  --------------------------------------------------------------
#   Autor(en)       :
#   Beginn-Datum    :
#  --------------------------------------------------------------
#   Beschreibung    :
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------

class IntMessage():

    # Message Types:
    START_IBEACON = 1
    START_DHBWBEACON = 2
    START_EDDYSTONE = 3
    START_ALTBEACON = 4
    STOP_BEACON = 5
    START_SCAN_BLE = 6
    STOP_SCAN_BLE = 7
    START_SCAN_BT = 8
    STOP_SCAN_BT = 9
    SCANNED_IBEACON = 10
    SCANNED_ALTBEACON = 11
    SCANNED_EDDYSTONEUID = 12
    SCANNED_DHBWBEACON = 13
    ALERT_GUI = 14
    BEACON_DATA_ERROR = 15
    BT_SCAN = 16
    RESET_IBEACON = 17
    RESET_DHBWBEACON = 18
    RESET_EDDYSTONE = 19
    RESET_ALTBEACON = 20
    SIGNAL_IBEACON = 21
    SIGNAL_EDDYSTONE = 22
    SIGNAL_ALTBEACON = 23
    SIGNAL_DHBWBEACON = 24
    GUI_READY = 25
    SET_AUTOSTART_IBEACON = 26
    SET_AUTOSTART_ALTBEACON = 27
    SET_AUTOSTART_EDDYSTONE = 28
    SET_AUTOSTART_DHBWBEACON = 29
    SAVE_IBEACON = 30
    SAVE_DHBWBEACON = 31
    SAVE_EDDYSTONE = 32
    SAVE_ALTBEACON = 33

    _type = None
    _payload = None

    def __init__(self, type, payload=None):
        self._type = type
        self._payload = payload

    def addVal(self, key, value):
        # TODO needs implementation
        raise NotImplemented

    def get_type(self):
        return self._type

    def get_payload(self):
        return self._payload

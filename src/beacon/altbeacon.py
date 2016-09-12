#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : beacon
#  --------------------------------------------------------------
#   Autor(en)       : Daniel Haß
#   Beginn-Datum    : 18.07.16
#  --------------------------------------------------------------
#   Beschreibung    : Object representation of an AltBeacon
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------
from beacon.hci import HCI

class AltBeacon():

    _bid = None
    _rssi = None
    _mfg = None
    _interval = None

    _hci = None

    _altbeacon_prefix = "1f02011a1bff1801beac"

    def __init__(self, bid, rssi, mfg, interval, hci):
        self._bid = bid
        self._rssi = int(rssi)
        self._mfg = mfg
        self._interval = interval

        self._hci = hci

    def start(self):
        data = self.build_adv_data()
        self._hci.start_adv(data, self._interval)
        return data

    def stop(self):
        self._hci.stop_adv()

    # build advertisement data
    def build_adv_data(self):
        adv = []
        adv.extend(HCI.to_hex_array(AltBeacon._altbeacon_prefix))  # AltBeacon prefix, Radius Network MFG-ID
        adv.extend(HCI.to_hex_array(self._bid))  # add BID to data string
        adv.append(format(self._rssi & 0xFF, 'x'))  # convert TX to signed hex value
        if len(self._mfg) == 1:  # added leading zero to MFG ID if the user entered only one char
            self._mfg = '0' + self._mfg
        adv.extend(HCI.to_hex_array(self._mfg))
        return adv

    # check user input for errors
    @staticmethod
    def check_input(bid, rssi, mfg):
        error = False
        try:
            int(bid, 16)  # convert BID to HEX to check for non HEX chars
        except ValueError:
            error = "BeaconID contains non HEX chars"

        if len(bid) != 40:  # check length of BID
            error = "BeaconID has to be 20 bytes long"

        # check tx
        if int(rssi) > 0 or int(rssi) < -127:  # check if RSSI is valid
            error = "RSSI value is bigger than 0 oder smaller than -127"

        try:
            int(mfg, 16)  # convert MFG ID to HEX to check for non HEX chars
        except ValueError:
            error = "MFG contains non HEX chars"

        if len(mfg) > 2:  # check length of MFG ID
            error = "MFG is to long"

        return error
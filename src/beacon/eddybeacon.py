#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : beacon
#  --------------------------------------------------------------
#   Autor(en)       : Daniel Haß
#   Beginn-Datum    : 18.07.16
#  --------------------------------------------------------------
#   Beschreibung    : Object representation of an Eddystone Beacon
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------
from beacon.hci import HCI

class EddyBeacon():

    _namespace = None
    _instance = None
    _tx = None
    _interval = None

    _hci = None

    _eddy_prefix = "1F02011A0303AAFE1716AAFE"

    def __init__(self, namespace, instance, tx, interval, hci):
        self._namespace = namespace
        self._instance = instance
        self._tx = int(tx)
        self._interval = interval

        self._hci = hci

    def start(self):
        data = self.build_adv_data()
        self._hci.start_adv(data, self._interval)
        return data

    def stop(self):
        self._hci.stop_adv()

    # build advertisement data for UID frame
    def build_adv_data(self):
        adv = []
        adv.extend(HCI.to_hex_array(EddyBeacon._eddy_prefix)) # EddystoneBeacon prefix
        adv.append('00')  # set Eddystone frame type - 0x00 for UID-Frame
        adv.append(format(self._tx & 0xFF, 'x'))  # convert TX to signed hex value
        adv.extend(HCI.to_hex_array(self._namespace))  # add Namespace ID to data string
        adv.extend(HCI.to_hex_array(self._instance))  # add Instance ID to data string
        adv.extend(['00', '00'])  # add two zeroed bytes - reserved for further use
        return adv

    # check user input for errors
    @staticmethod
    def check_input(namespace, instance, tx):
        error = True

        try:
            int(namespace, 16)  # convert Namespace ID to HEX to check for non HEX chars
        except ValueError:
            error = "Namespace contains non HEX chars"

        if len(namespace) != 20:  # check length of Namespace ID
            error = "Namespace has to be 20 bytes long"

        try:
            int(instance, 16)  # convert Instance ID to HEX to check for non HEX chars
        except ValueError:
            error = "Instance contains non HEX chars"

        if len(instance) != 12:  # check length of Instance ID
            error = "Namespace has to be 6 bytes long"

        # check tx
        if int(tx) > 20 or int(tx) < -100:  # check of TX is valid
            error = "TX value is bigger than 20 oder smaller than -100"

        return error
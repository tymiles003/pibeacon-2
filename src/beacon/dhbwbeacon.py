#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : beacon
#  --------------------------------------------------------------
#   Autor(en)       : Daniel Haß
#   Beginn-Datum    : 05.08.16
#  --------------------------------------------------------------
#   Beschreibung    : Object representation of an DHBW Beacon
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------
import threading
import time
from beacon.hci import HCI

class DhbwBeacon():

    _namespace = None
    _instance = None
    _tx = None
    _interval = None
    _wrapper = None

    _hci = None

    _eddy_prefix = "1F02011A0303AAFE1716AAFE"

    def __init__(self, namespace, instance, tx, interval, hci):
        self._namespace = namespace
        self._instance = instance
        self._tx = int(tx)
        self._interval = interval

        self._hci = hci

    def start(self):
        data_uid = self.build_adv_data_uid()
        self._wrapper = DhbwBeaconWrapper(data_uid, float(self._interval), self._hci)
        self._wrapper.start()
        return data_uid

    def stop(self):
        self._wrapper.stop()
        self._hci.stop_adv()

    # build advertisement data for UID frame
    def build_adv_data_uid(self):
        adv = []
        adv.extend(HCI.to_hex_array(DhbwBeacon._eddy_prefix)) # EddystoneBeacon prefix
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

        if int(tx) > 20 or int(tx) < -100:  # check of TX is valid
            error = "TX value is bigger than 20 oder smaller than -100"

        return error

# Thread needed for frame switching between UID and TLM
class DhbwBeaconWrapper(threading.Thread):

    _dataUID = None
    _interval = None
    _running = True
    _advCount = 1
    _timeStart = 0

    _eddy_tlm_prefix = "1902011A0303AAFE1116AAFE"

    def __init__(self, uid, interval, hci):
        threading.Thread.__init__(self)
        self._dataUID = uid
        self._interval = float(interval/1000)
        self._hci = hci

    def run(self):
        self._timeStart = time.time()  # save the time at startup
        self._hci.power_hci_dev()  # power on the HCI device
        while self._running:
            # TLM advertisement
            time.sleep(self._interval) # pause interval to next advertisement
            if self._running: self._hci.one_time_adv(self.build_adv_data_tlm()) # send one TLM advertisement
            self._advCount += 1 # increase counter for TLM PDU value

            # UID advertisement
            time.sleep(self._interval) # pause interval to next advertisement
            if self._running: self._hci.one_time_adv(self._dataUID) # send one UID advertisement
            self._advCount += 1 # increase counter for TLM PDU value

    # build advertisement data for TLM frame
    def build_adv_data_tlm(self):
        adv = []
        adv.extend(HCI.to_hex_array(DhbwBeaconWrapper._eddy_tlm_prefix))  # EddystoneBeacon TLM prefix
        adv.append('20') # EddystoneBeacon Frame Type - TLM
        adv.append('00') # TLM Version
        adv.extend(['00', '00']) # Battery value - currently not supported = 0x0000
        adv.extend(['80', '00']) # Beacon temperature - currently not supported = 0x8000 (-128°C)
        adv.extend(HCI.to_hex_array(format(self._advCount, '08x'))) # Advertising PDU count - convert int to hex
        adv.extend(HCI.to_hex_array(format(int((time.time() - self._timeStart)/0.1), '08x'))) # Time since power-on or reboot
        return adv

    def stop(self):
        self._running = False

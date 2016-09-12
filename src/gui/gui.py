#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : gui.gui
#  --------------------------------------------------------------
#   Autor(en)       : Henrik Schaffhauser
#   Beginn-Datum    : 22.07.2016
#  --------------------------------------------------------------
#   Beschreibung    : GUI functions
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#  --------------------------------------------------------------
import sys
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import *
from PyQt4.QtCore import *

from comm.intcomm import IntComm
from comm.intmessage import IntMessage
from conf.config import BeaconConfig
from gui.BeaconUI import Ui_PiBeacon
from utils.debug import DBG

class Gui(IntComm):

    _commCallback = None
    _config = None
    _app = None
    _ui = None
    _mainwindow = None

    def __init__(self, commCallback, config):
        self._commCallback = commCallback
        self._config = config

    def comm(self, msg):
        pl = msg.get_payload()

        if msg.get_type() is IntMessage.ALERT_GUI:
            self.show_dialog(msg.get_payload()['ALERT_TEXT'], msg.get_payload()['ALERT_DETAIL'])

        #Beacon scan - parameters textbox output
        blebar = self._ui.bcscanausgabe.verticalScrollBar()
        if msg.get_type() is IntMessage.SCANNED_IBEACON:
            self._ui.bcscanausgabe.append('iBeacon' + '\nUUID: ' + '\t' + str(pl['UUID']) + '\nMAJOR: ' + '\t' + str(pl['MAJOR']) + '\nMINOR: ' + '\t' + str(pl['MINOR']) + '\nTX: ' + '\t' + str(pl['TX']) + '\n')
            blebar.setValue(blebar.maximum())

        if msg.get_type() is IntMessage.SCANNED_ALTBEACON:
            self._ui.bcscanausgabe.append('Alt Beacon' + '\nBID: ' + '\t' + str(pl['BID']) + '\nRSSI: ' + '\t' + str(pl['RSSI']) + '\nMFG: ' + '\t' + str(pl['MFG']) + '\n')
            blebar.setValue(blebar.maximum())

        if msg.get_type() is IntMessage.SCANNED_EDDYSTONEUID:
            self._ui.bcscanausgabe.append('Eddystone Beacon' + '\nNID: ' + '\t' + str(pl['NID']) + '\nIID: ' + '\t' + str(pl['IID']) + '\nTX: ' + '\t' + str(pl['TX']) + '\n')
            blebar.setValue(blebar.maximum())

        if msg.get_type() is IntMessage.SCANNED_DHBWBEACON:
            self._ui.bcscanausgabe.append('DHBW-Beacon' + '\nNID: ' + '\t' + str(pl['NID']) + '\nIID: ' + '\t' + str(pl['IID']) + '\nTX: ' + '\t' + str(pl['TX']) + '\n')
            blebar.setValue(blebar.maximum())

        #print sent signal into the outbox for each beacon type
        if msg.get_type() is IntMessage.SIGNAL_IBEACON:
            self._ui.ibgesendetessignal.append(str(pl['TEXT']))

        if msg.get_type() is IntMessage.SIGNAL_ALTBEACON:
            self._ui.abgesendetessignal.append(str(pl['TEXT']))

        if msg.get_type() is IntMessage.SIGNAL_EDDYSTONE:
            self._ui.ebgesendetessignal.append(str(pl['TEXT']))

        if msg.get_type() is IntMessage.SIGNAL_DHBWBEACON:
            self._ui.dbgesendetessignal.append(str(pl['TEXT']))

        #Bluetooth scan - parameters textbox output
        btbar = self._ui.btscanausgabe.verticalScrollBar()
        if msg.get_type() is IntMessage.BT_SCAN:
            self._ui.btscanausgabe.append(str(pl['TEXT']))
            btbar.setValue(btbar.maximum())

        #receive default values from controller
        if msg.get_type() is IntMessage.RESET_IBEACON:
            self.ibdefaultvalues(pl)

        if msg.get_type() is IntMessage.RESET_ALTBEACON:
            self.abdefaultvalues(pl)

        if msg.get_type() is IntMessage.RESET_EDDYSTONE:
            self.ebdefaultvalues(pl)

        if msg.get_type() is IntMessage.RESET_DHBWBEACON:
            self.dbdefaultvalues(pl)

    #Definition of the alert box
    def show_dialog(self, msgtxt, detailtxt):
       msg = QMessageBox()
       msg.setIcon(QMessageBox.Information)
       msg.setText(msgtxt)
       msg.setWindowTitle("Alert")
       msg.setDetailedText(detailtxt)
       msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
       retval = msg.exec()
       DBG ("value of pressed message box button:"), retval

    def start_gui(self):
        self._app = QtGui.QApplication(sys.argv)
        self._mainwindow = QtGui.QMainWindow()
        self._ui = Ui_PiBeacon()
        self._ui.setupUi(self._mainwindow)
        self.ibrssbutton()
        self.abrssbutton()
        self.ebrssbutton()
        self.dbrssbutton()
        self.bcscan()
        self.btscan()
        self.saved_values()
        self._mainwindow.show()
        self._ui.menuSave.triggered[QAction].connect(self.save_to_config)
        self._commCallback(IntMessage(IntMessage.GUI_READY))
        self._app.aboutToQuit.connect(self.uiclosed)
        sys.exit(self._app.exec_())

    #receive default values for iBeacon
    def ibdefaultvalues(self, dictvalue):
        self._ui.ibaktuellerdatastring.setText(dictvalue['UUID'])
        self._ui.ibmajor.setValue(float(dictvalue['MAJOR']))
        self._ui.ibminor.setValue(float(dictvalue['MINOR']))
        self._ui.ibtx.setValue(float(dictvalue['TX']))
        self._ui.ibsendeintervall.setValue(float(dictvalue['INTERVAL']))

    #receive default values for AltBeacon
    def abdefaultvalues(self, dictvalue):
        self._ui.abaktuellerdatastring.setText(dictvalue['BID'])
        self._ui.abrssi.setValue(float(dictvalue['RSSI']))
        self._ui.abmfg.setText(dictvalue['MFG'])
        self._ui.absendeintervall.setValue(float(dictvalue['INTERVAL']))

    #receive default values for Eddystone Beacon
    def ebdefaultvalues(self, dictvalue):
        self._ui.ebaktuellerdatastringnid.setText(dictvalue['NID'])
        self._ui.ebaktuellerdatastringiid.setText(dictvalue['IID'])
        self._ui.ebtx.setValue(float(dictvalue['TX']))
        self._ui.ebsendeintervall.setValue(float(dictvalue['INTERVAL']))

    #receive default values for DHBW-Beacon
    def dbdefaultvalues(self, dictvalue):
        self._ui.dbaktuellerdatastringnid.setText(dictvalue['NID'])
        self._ui.dbaktuellerdatastringiid.setText(dictvalue['IID'])
        self._ui.dbtx.setValue(float(dictvalue['TX']))
        self._ui.dbsendeintervall.setValue(float(dictvalue['INTERVAL']))

    #load saved values from config
    def saved_values(self):
        ibconf = self._config.IBeacon_dict
        abconf = self._config.AltBeacon_dict
        ebconf = self._config.Eddystone_dict
        dbconf = self._config.DHBWBeacon_dict

        #load saved values
        self.ibdefaultvalues(ibconf)
        self.abdefaultvalues(abconf)
        self.ebdefaultvalues(ebconf)
        self.dbdefaultvalues(dbconf)

    # save values to config
    def save_to_config(self):
        self._commCallback(IntMessage(IntMessage.SAVE_IBEACON, {'UUID': self._ui.ibaktuellerdatastring.text(),
                                                                'MAJOR': self._ui.ibmajor.text(),
                                                                'MINOR': self._ui.ibminor.text(),
                                                                'TX': self._ui.ibtx.text(),
                                                                'INTERVAL': self._ui.ibsendeintervall.text()}))

        self._commCallback(IntMessage(IntMessage.SAVE_ALTBEACON, {'BID': self._ui.abaktuellerdatastring.text(),
                                                                   'RSSI': self._ui.abrssi.text(),
                                                                   'MFG': self._ui.abmfg.text(),
                                                                   'INTERVAL': self._ui.absendeintervall.text()}))

        self._commCallback(IntMessage(IntMessage.SAVE_EDDYSTONE, {'NID': self._ui.ebaktuellerdatastringnid.text(),
                                                                   'IID': self._ui.ebaktuellerdatastringiid.text(),
                                                                   'TX': self._ui.ebtx.text(),
                                                                   'INTERVAL': self._ui.ebsendeintervall.text()}))

        self._commCallback(IntMessage(IntMessage.SAVE_DHBWBEACON, {'NID': self._ui.dbaktuellerdatastringnid.text(),
                                                                    'IID': self._ui.dbaktuellerdatastringiid.text(),
                                                                    'TX': self._ui.dbtx.text(),
                                                                    'INTERVAL': self._ui.dbsendeintervall.text()}))

        self.show_dialog("Saved current values!", "The current values of all Beacons have been saved."
                                                  "They will be available on the next application start.")

    #Beacon Scan Output
    def bcscan(self):
        self._ui.bcscanstart.clicked.connect(self.bcscanstart_clicked)
        self._ui.bcscanstop.clicked.connect(self.bcscanstop_clicked)

    def bcscanstart_clicked(self):

        msg = IntMessage(IntMessage.START_SCAN_BLE)
        self._commCallback(msg)
        DBG ("Scan Button clicked")

    def bcscanstop_clicked(self):

        msg = IntMessage(IntMessage.STOP_SCAN_BLE)
        self._commCallback(msg)
        DBG ("Stop Button clicked")

    #Bluetooth Scan Output
    def btscan(self):
        self._ui.btscanstart.clicked.connect(self.btscanstart_clicked)

    def btscanstart_clicked(self):

        msg = IntMessage(IntMessage.START_SCAN_BT)
        self._commCallback(msg)

    #Definition of the iBeacon Buttons
    def ibrssbutton(self):
        self._ui.ibreset.clicked.connect(self.ibreset_clicked)
        self._ui.ibstart.clicked.connect(self.ibstart_clicked)
        self._ui.ibstop.clicked.connect(self.ibstop_clicked)
        self._ui.ibsetasautostart.clicked.connect(self.ibsetasautostart_clicked)

    def ibstart_clicked(self):

        msg = IntMessage(IntMessage.START_IBEACON, {'UUID': self._ui.ibaktuellerdatastring.text(),
                                                    'MAJOR': self._ui.ibmajor.text(),
                                                    'MINOR': self._ui.ibminor.text(),
                                                    'TX': self._ui.ibtx.text(),
                                                    'INTERVAL': self._ui.ibsendeintervall.text()})

        DBG(msg.get_payload())
        self._commCallback(msg)

    def ibstop_clicked(self):
        DBG("Stop Button clicked")
        msg = IntMessage(IntMessage.STOP_BEACON)
        self._commCallback(msg)

    def ibreset_clicked(self):
        DBG("Reset Button clicked")
        msg = IntMessage(IntMessage.RESET_IBEACON)
        self._commCallback(msg)

    def ibsetasautostart_clicked(self):
        DBG("Set as Autostart clicked")
        msg = IntMessage(IntMessage.SET_AUTOSTART_IBEACON)
        self._commCallback(msg)

    #Definition of the AltBeacon Buttons
    def abrssbutton(self):
        self._ui.abreset.clicked.connect(self.abreset_clicked)
        self._ui.abstart.clicked.connect(self.abstart_clicked)
        self._ui.abstop.clicked.connect(self.abstop_clicked)
        self._ui.absetasautostart.clicked.connect(self.absetasautostart_clicked)

    def abstart_clicked(self):

        msg = IntMessage(IntMessage.START_ALTBEACON, {'BID': self._ui.abaktuellerdatastring.text(),
                                                      'RSSI': self._ui.abrssi.text(),
                                                      'MFG': self._ui.abmfg.text(),
                                                      'INTERVAL': self._ui.absendeintervall.text()})

        DBG(msg.get_payload())
        self._commCallback(msg)

    def abstop_clicked(self):
        DBG("Stop Button clicked")
        msg = IntMessage(IntMessage.STOP_BEACON)
        self._commCallback(msg)

    def abreset_clicked(self):
        DBG("Reset Button clicked")
        msg = IntMessage(IntMessage.RESET_ALTBEACON)
        self._commCallback(msg)

    def absetasautostart_clicked(self):
        DBG("Set as Autostart clicked")
        msg = IntMessage(IntMessage.SET_AUTOSTART_ALTBEACON)
        self._commCallback(msg)

    #Definition of the Eddystone Beacon Buttons
    def ebrssbutton(self):
        self._ui.ebreset.clicked.connect(self.ebreset_clicked)
        self._ui.ebstart.clicked.connect(self.ebstart_clicked)
        self._ui.ebstop.clicked.connect(self.ebstop_clicked)
        self._ui.ebsetasautostart.clicked.connect(self.ebsetasautostart_clicked)

    def ebstart_clicked(self):

        msg = IntMessage(IntMessage.START_EDDYSTONE, {'NID': self._ui.ebaktuellerdatastringnid.text(),
                                                    'IID': self._ui.ebaktuellerdatastringiid.text(),
                                                    'TX': self._ui.ebtx.text(),
                                                    'INTERVAL': self._ui.ebsendeintervall.text()})

        DBG(msg.get_payload())
        self._commCallback(msg)

    def ebstop_clicked(self):
        DBG("Stop Button clicked")
        msg = IntMessage(IntMessage.STOP_BEACON)
        self._commCallback(msg)

    def ebreset_clicked(self):
        DBG("Reset Button clicked")
        msg = IntMessage(IntMessage.RESET_EDDYSTONE)
        self._commCallback(msg)

    def ebsetasautostart_clicked(self):
        DBG("Set as Autostart clicked")
        msg = IntMessage(IntMessage.SET_AUTOSTART_EDDYSTONE)
        self._commCallback(msg)

    #Defintion of the DHBW Beacon Buttons
    def dbrssbutton(self):
        self._ui.dbreset.clicked.connect(self.dbreset_clicked)
        self._ui.dbstart.clicked.connect(self.dbstart_clicked)
        self._ui.dbstop.clicked.connect(self.dbstop_clicked)
        self._ui.dbsetasautostart.clicked.connect(self.dbsetasautostart_clicked)

    def dbstart_clicked(self):
        msg = IntMessage(IntMessage.START_DHBWBEACON, {'NID': self._ui.dbaktuellerdatastringnid.text(),
                                                      'IID': self._ui.dbaktuellerdatastringiid.text(),
                                                      'TX': self._ui.dbtx.text(),
                                                      'INTERVAL': self._ui.dbsendeintervall.text()})

        DBG(msg.get_payload())
        self._commCallback(msg)

    def dbstop_clicked(self):
        DBG("Stop Button clicked")
        msg = IntMessage(IntMessage.STOP_BEACON)
        self._commCallback(msg)

    def dbreset_clicked(self):
        DBG("Reset Button clicked")
        msg = IntMessage(IntMessage.RESET_DHBWBEACON)
        self._commCallback(msg)

    def dbsetasautostart_clicked(self):
        DBG("Set as Autostart clicked")
        msg = IntMessage(IntMessage.SET_AUTOSTART_DHBWBEACON)
        self._commCallback(msg)

    #ui closed
    def uiclosed(self):
        msg = IntMessage(IntMessage.STOP_BEACON)
        self._commCallback(msg)
        #self._app.exec_()
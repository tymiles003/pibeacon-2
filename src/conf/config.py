#  **************************************************************
#   Projekt         : PiBeacon
#   Modul           : Config.py
#  --------------------------------------------------------------
#   Autor(en)       : Tobias Zeiser
#   Beginn-Datum    : 18.07.2016
#  --------------------------------------------------------------
#   Beschreibung    : Objekt zum verwalten des Ini Files
#  --------------------------------------------------------------
#
#  **************************************************************
#   Änderungs-Protokoll:
#  --------------------------------------------------------------
#   wann                 wer   was
#   25.07.2016           tz    Hinzufügen der Funktion speichere_dict und Fertigstellen der Funtkion speichern_der_config
#   27.05.2016           tz    Überarbeiten der Unit
#   27.05.2016           tz    Hinzufügen der Überprüfung ob die Datei bereits existiert
#  --------------------------------------------------------------

import configparser
import os.path


class BeaconConfig:
    Config = configparser.ConfigParser()
    Config.optionxform = str  # preserve case for saved values
    ##################################################################
    # Here constants are defined
    ##################################################################
    IBeacon = 'IBeacon'
    AltBeacon = 'AltBeacon'
    DHBWBeacon = 'DHBWBeacon'
    General = 'General'
    Eddystone = 'Eddystone'
    General_dict = {}
    IBeacon_dict = {}
    AltBeacon_dict = {}
    DHBWBeacon_dict = {}
    Eddystone_dict = {}
    filename = ''

    ##################################################################
    # constructor of the BeaconConfig Object. Creates the ini file and the sections
    ##################################################################
    def __init__(self, dateiname):
        self.filename = dateiname
        if os.path.exists(dateiname):
            self.Config.read(dateiname)
            self.fill_dict()
        else:
            open(dateiname, 'w+')
            self.Config.read(dateiname)
            self.Config.add_section(self.General)
            self.Config.add_section(self.AltBeacon)
            self.Config.add_section(self.Eddystone)
            self.Config.add_section(self.IBeacon)
            self.Config.add_section(self.DHBWBeacon)
            self.fill_dict()
            self.save_file()

    ##################################################################
    # This function read the sections from the ini file and save them to the dictionaries
    ##################################################################
    def read_beacon_config(self, section, beaconlist):
        try:
            options = self.Config.options(section)
            for options in options:
                beaconlist[options] = self.Config.get(section, options)
        except configparser.NoSectionError:
            raise Exception('Section does not exist')

    ##################################################################
    # save key=value pairs whit the related section in the ini file
    ##################################################################
    def save_config(self, section, key, value):
        if self.Config.has_section(section):
            self.Config.set(section, key, value)
        if section == self.AltBeacon:
            if key in self.AltBeacon_dict:
                self.AltBeacon_dict[key] = value
        if section == self.IBeacon:
            if key in self.IBeacon_dict:
                self.IBeacon_dict[key] = value
        if section == self.DHBWBeacon:
            if key in self.DHBWBeacon_dict:
                self.DHBWBeacon_dict[key] = value
        if section == self.Eddystone:
            if key in self.DHBWBeacon:
                self.Eddystone_dict[key] = value

    ##################################################################
    # Save the dictionaries in the ini file with the related section
    ##################################################################
    def save_dict(self, beacondict, section):
        for keys in beacondict.keys():
            self.save_config(section, keys, beacondict[keys])

    def fill_dict(self):
        self.read_beacon_config(self.General, self.General_dict)
        self.read_beacon_config(self.Eddystone, self.Eddystone_dict)
        self.read_beacon_config(self.AltBeacon, self.AltBeacon_dict)
        self.read_beacon_config(self.IBeacon, self.IBeacon_dict)
        self.read_beacon_config(self.DHBWBeacon, self.DHBWBeacon_dict)

    ##################################################################
    # save the changes in the File. Must call after changes!
    ##################################################################
    def save_file(self):
        with open(self.filename, 'w') as configfile:
            self.Config.write(configfile)
            self.fill_dict()

#!/usr/bin/env python

# OPTAA calibration parser
#
# Create the necessary CI calibration ingest information from an OPTAA calibration file

import csv
import json
import os
import sys
import datetime


class NutnrCalibration:
    def __init__(self, asset_tracking_number, lower=217, upper=240):
        self.cal_temp = None
        self.wavelengths = []
        self.eno3 = []
        self.eswa = []
        self.di = []
        self.lower_limit = lower
        self.upper_limit = upper
        self.asset_tracking_number = None
        self.date = None
        self.serial = None

    def read_cal(self, filename):
        with open(filename) as fh:
            for line in fh:
                parts = line.split(',')

                if len(parts) < 2:
                    continue  # skip anything that is not key value paired
                record_type = parts[0]
                if record_type == 'H':
                    key_value = parts[1].split()
                    if len(key_value) == 2:
                        name, value = key_value
                        if name == 'T_CAL':
                            self.cal_temp = float(value)
                    elif "creation" in key_value:
                        cal_date = key_value[-2]
                        cal_date = datetime.datetime.strptime(cal_date, "%d-%b-%Y").strftime("%Y%m%d")
                        self.date = cal_date
                    elif "SUNA" in key_value:
                        self.serial = str(key_value[1]).lstrip('0')

                elif record_type == 'E':
                    _, wavelength, eno3, eswa, _, di = parts
                    self.wavelengths.append(float(wavelength))
                    self.eno3.append(float(eno3))
                    self.eswa.append(float(eswa))
                    self.di.append(float(di))

    def write_cal_info(self):
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name', 'value', 'notes'])
            writer.writerow([self.serial,'CC_cal_temp', self.cal_temp])
            writer.writerow([self.serial,'CC_wl', json.dumps(self.wavelengths)])
            writer.writerow([self.serial,'CC_eno3', json.dumps(self.eno3)])
            writer.writerow([self.serial,'CC_eswa', json.dumps(self.eswa)])
            writer.writerow([self.serial,'CC_di', json.dumps(self.di)])
            writer.writerow([self.serial,'CC_lower_wavelength_limit_for_spectra_fit', self.lower_limit])
            writer.writerow([self.serial,'CC_upper_wavelength_limit_for_spectra_fit', self.upper_limit])

def main():
    lookup = {}
    with open('nutnr_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    os.chdir('Manufacturer Cal Files')
    for sheet in os.listdir(os.getcwd()):
        cal = NutnrCalibration("")
        cal.read_cal(sheet)
        cal.asset_tracking_number = lookup[cal.serial]
        os.chdir("../Cal Sheets")
        cal.write_cal_info()
        os.chdir("../Manufacturer Cal Files")
    os.chdir('..')

if __name__ == '__main__':
    main()

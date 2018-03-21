#!/usr/bin/env python

# SPKIR calibration parser
#
# Create the necessary CI calibration ingest information from an SPKIR calibration file

import csv
import json
import os
import sys
import datetime
import re
from dateutil.parser import parse

constants = {'CC_angular_resolution':1.096, 'CC_depolarization_ratio':0.039, 'CC_measurement_wavelength':700, 'CC_scattering_angle':140}
class FlntuaCalibration:
    def __init__(self):
        self.chl= None
        self.vol = None
        self.asset_tracking_number = None
        self.serial = None
        self.date = None

    def read_cal(self, filename):
        with open(filename) as fh:
            for line in fh:
                parts = line.split()
                if not len(parts):  # skip blank lines
                    continue
                if 'ECO' == parts[0]:
                    self.serial = parts[-1]
                elif 'Created' == parts[0]:
                    self.date = datetime.datetime.strptime(parts[-1], '%m/%d/%y').strftime('%Y%m%d')
                deconstruct = parts[0].split('=')
                if deconstruct[0] == 'NTU':
                    self.vol = (parts[1], parts[2])
                elif deconstruct[0] == 'Chl':
                    self.chl = (parts[1], parts[2])

    def write_cal_info(self):
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name','value','notes'])
            writer.writerow([self.serial,'CC_angular_resolution', constants['CC_angular_resolution'],''])
            writer.writerow([self.serial,'CC_dark_counts_chlorophyll_a', self.chl[1], ''])
            writer.writerow([self.serial,'CC_dark_counts_volume_scatter', self.vol[1], ''])
            writer.writerow([self.serial,'CC_depolarization_ratio', constants['CC_depolarization_ratio'],''])
            writer.writerow([self.serial,'CC_measurement_wavelength', constants['CC_measurement_wavelength'],''])
            writer.writerow([self.serial,'CC_scale_factor_chlorophyll_a', self.chl[0], ''])
            writer.writerow([self.serial,'CC_scale_factor_volume_scatter', self.vol[0], ''])
            writer.writerow([self.serial,'CC_scattering_angle', constants['CC_scattering_angle'],''])

def main():
    lookup = {}
    with open('flntua_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    os.chdir('Manufacturer Cal Files')
    for sheet in os.listdir(os.getcwd()):
        cal = FlntuaCalibration()
        cal.read_cal(sheet)
        cal.asset_tracking_number = lookup[cal.serial]
        os.chdir("../Cal Sheets")
        cal.write_cal_info()
        os.chdir("../Manufacturer Cal Files")
    os.chdir('..')


if __name__ == '__main__':
    main()

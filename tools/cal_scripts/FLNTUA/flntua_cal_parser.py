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
import copy
from dateutil.parser import parse

class FLNTUACalibration:
    def __init__(self):
        self.chl= None
        self.vol = None
        self.asset_tracking_number = None
        self.serial = None
        self.date = None
        self.coefficients = {'CC_angular_resolution':1.096, 'CC_depolarization_ratio':0.039, 'CC_measurement_wavelength':700, 'CC_scattering_angle':140}

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
                    self.coefficients['CC_scale_factor_volume_scatter'] = parts[1]
                    self.coefficients['CC_dark_counts_volume_scatter'] = parts[2]
                elif deconstruct[0] == 'Chl':
                    self.chl = (parts[1], parts[2])
                    self.coefficients['CC_scale_factor_chlorophyll_a'] = parts[1]
                    self.coefficients['CC_dark_counts_chlorophyll_a'] = parts[2]

    def write_cal_info(self):
        file_name = self.asset_tracking_number + '__' + self.date
        os.chdir("cal_sheets")
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name', 'value', 'notes'])
            for each in sorted(self.coefficients.items()):
                writer.writerow([self.serial] + list(each))
        os.chdir("..")

def main():
    lookup = {}
    with open('flntua_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    for path, directories, files in os.walk('manufacturer'):
        for file in files:
            cal = FLNTUACalibration()
            cal.read_cal(os.path.join(path, file))
            cal.asset_tracking_number = lookup[cal.serial]
            cal.write_cal_info()

if __name__ == '__main__':
    main()

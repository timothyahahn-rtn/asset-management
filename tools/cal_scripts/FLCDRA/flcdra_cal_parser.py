#!/usr/bin/env python

# SPKIR calibration parser
#
# Create the necessary CI calibration ingest information from an SPKIR calibration file

import csv
import os
import datetime
from dateutil.parser import parse

class FlntuaCalibration:
    def __init__(self):
        self.dark = 0
        self.scale = 0.0
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
                    self.date = datetime.datetime.strptime(parts[-1], '%m/%d/%Y').strftime('%Y%m%d')
                deconstruct = parts[0].split('=')
                if deconstruct[0] == 'CDOM':
                    self.dark = parts[-1]
                    self.scale = parts[1]

    def write_cal_info(self):
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name','value','notes'])
            writer.writerow([self.serial,'CC_dark_counts_cdom', self.dark, ''])
            writer.writerow([self.serial,'CC_scale_factor_cdom', self.scale, ''])

def main():
    lookup = {}
    with open('flcdra_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    os.chdir('manufacturer_cal_files')
    for sheet in os.listdir(os.getcwd()):
        cal = FlntuaCalibration()
        cal.read_cal(sheet)
        cal.asset_tracking_number = lookup[cal.serial]
        os.chdir("../cal_sheets")
        cal.write_cal_info()
        os.chdir("../manufacturer_cal_files")
    os.chdir('..')

if __name__ == '__main__':
    main()

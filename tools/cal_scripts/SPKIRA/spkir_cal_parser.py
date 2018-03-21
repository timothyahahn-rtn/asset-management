#!/usr/bin/env python

# SPKIR calibration parser
#
# Create the necessary CI calibration ingest information from an SPKIR calibration file
# These scripts are based on ones available

import csv
import json
import os
import sys
import datetime
import re
from dateutil.parser import parse

class SPKIRCalibration:
    def __init__(self):
        self.offset = []
        self.scale = []
        self.immersion_factor = []
        self.asset_tracking_number = None
        self.serial = None
        self.date = None

    def read_cal(self, filename):
        with open(filename) as fh:
            read_record = False  # indicates next line is record we want to read
            for line in fh:
                parts = line.split()
                if "OCR-507" in line:
                    self.serial = str(parts[-2]).lstrip('0')
                elif not len(parts):  # skip blank lines
                    continue
                elif '#' == parts[0]:
                    try:
                        parse(parts[1])
                    except ValueError:
                        continue
                    self.date = str(parts[1]).replace('-','')

                elif parts[0] == 'ED':
                    read_record = True
                    continue
                elif read_record:
                    if len(parts) == 3:  # only parse if we have all the data
                        offset, scale, factor = parts
                        self.offset.append(float(offset))
                        self.scale.append(float(scale))
                        self.immersion_factor.append(float(factor))
                        read_record = False

    def write_cal_info(self):
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name','value','notes'])
            writer.writerow([self.serial,'CC_immersion_factor', self.immersion_factor])
            writer.writerow([self.serial,'CC_offset', json.dumps(self.offset)])
            writer.writerow([self.serial,'CC_scale', json.dumps(self.scale)])

def main():
    lookup = {}
    with open('spkir_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    os.chdir('manufacturer')
    for sheet in os.listdir(os.getcwd()):
        cal = SPKIRCalibration()
        cal.read_cal(sheet)
        cal.asset_tracking_number = lookup[cal.serial]
        os.chdir("../cal_sheets")
        cal.write_cal_info()
        os.chdir("../manufacturer")
    os.chdir('..')

if __name__ == '__main__':
    main()

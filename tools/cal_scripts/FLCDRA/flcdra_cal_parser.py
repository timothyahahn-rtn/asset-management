#!/usr/bin/env python

# FLCDRA calibration parser
#
# Create the necessary CI calibration ingest information from an FLCDRA calibration file

import csv, datetime, os

class FLCDRACalibration:
    def __init__(self):
        self.dark = 0
        self.scale = 0.0
        self.asset_tracking_number = None
        self.serial = None
        self.date = None
        self.coefficients = {}

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
                    self.coefficients['CC_dark_counts_cdom'] = parts[-1]
                    self.coefficients['CC_scale_factor_cdom'] = parts[1]

    def write_cal_info(self):
        os.chdir("cal_sheets")
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name', 'value', 'notes'])
            for each in sorted(self.coefficients.items()):
                writer.writerow([self.serial] + list(each))
        os.chdir("..")

def main():
    lookup = {}
    with open('flcdra_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    for path, directories, files in os.walk('manufacturer'):
        for file in files:
            cal = FLCDRACalibration()
            cal.read_cal(os.path.join(path, file))
            cal.asset_tracking_number = lookup[cal.serial]
            cal.write_cal_info()


if __name__ == '__main__':
    main()

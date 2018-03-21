#!/usr/bin/env python

# CTD calibration parser
#
# Create the necessary CI calibration ingest information from an CTD calibration file

import csv
import os
import sys
import datetime

class SBE43Calibration:
    def __init__(self):
        self.coefficient_name_map = {
            'E': 'CC_residual_temperature_correction_factor_e',
            'C': 'CC_residual_temperature_correction_factor_c',
            'VOFFSET': 'CC_voltage_offset',  # note that this was previously called CC_frequency_offset
            'SOC': 'CC_oxygen_signal_slope',
            'A': 'CC_residual_temperature_correction_factor_a',
            'B': 'CC_residual_temperature_correction_factor_b',
        }
        # dictionary with calibration coefficient names and values
        self.coefficients = {}
        self.asset_tracking_number = None
        self.serial = None
        self.lookup_dict = None
        self.date = None

    def read_cal(self, filename):
        with open(filename) as fh:
            for line in fh:
                parts = line.split('=')

                if len(parts) != 2:
                    continue  # skip anything that is not key value paired

                key = parts[0]
                value = parts[1].strip()

                if key == 'INSTRUMENT_TYPE' and value != 'SBE43':
                    print 'Error - unexpected type calibration file (%s != SBE43)' % value
                    sys.exit(1)

                if self.coefficient_name_map.has_key(key):
                    name = self.coefficient_name_map.get(key)

                    self.coefficients[name] = value

                if key == "OCALDATE":
                    cal_date = value
                    cal_date = datetime.datetime.strptime(cal_date, "%d-%b-%y").strftime("%Y%m%d")
                    self.date = cal_date

                if key == "SERIALNO":
                    self.serial = "43-" + str(value)

    def write_cal_info(self):
        file_name = self.asset_tracking_number + "__" + self.date + ".csv"
        with open(file_name, 'w') as info:
            field_names = ['serial','name', 'value', 'notes']
            writer = csv.writer(info)
            writer.writerow(field_names)
            for each in sorted(self.coefficients.items()):
                writer.writerow([self.serial] + list(each))
                if each[0] == 'CC_voltage_offset':
                    put_in = [self.serial, 'CC_frequency_offset', each[-1]]
                    writer.writerow(put_in)

def main():
    # Starts in the directory with
    # Get corresponding mapping between serial number and uid
    lookup = {}
    with open('dofsta_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    #Begin writing files
    os.chdir('manufacturer_cal_files')
    for sheet in os.listdir(os.getcwd()):
        cal = SBE43Calibration()
        cal.read_cal(sheet)
        cal.asset_tracking_number = lookup[cal.serial]
        os.chdir("../cal_sheets")
        cal.write_cal_info()
        os.chdir("../manufacturer_cal_files")

    os.chdir("..")

if __name__ == '__main__':
    main()

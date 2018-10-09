#!/usr/bin/env python

# DOFSTA calibration parser
#
# Create the necessary CI calibration ingest information from a DOFSTA calibration file

import csv
import datetime
import os
import sys
import time
import xml.etree.ElementTree as et
from common_code.cal_parser_template import Calibration, get_uid_serial_mapping

class SBE43Calibration(Calibration):
    def __init__(self):
        super(SBE43Calibration, self).__init__()
        self.type = 'DOFSTA'
        self.serial = '43-'
        self.coefficient_name_map = {
            'E': 'CC_residual_temperature_correction_factor_e',
            'C': 'CC_residual_temperature_correction_factor_c',
            'VOFFSET': 'CC_voltage_offset',  # note that this was previously called CC_frequency_offset
            'OFFSET': 'CC_voltage_offset',
            'SOC': 'CC_oxygen_signal_slope',
            'A': 'CC_residual_temperature_correction_factor_a',
            'B': 'CC_residual_temperature_correction_factor_b',
        }

    def read_xml(self, filename):
        with open(filename) as fh:
            tree = et.parse(filename)
            root = tree.getroot()
            t_flag = False
            for child in tree.iter():
                key = child.tag.upper()
                print(child.tag)
                if key == '':
                    continue

                if child.tag == "SerialNumber" and child.text != None and self.serial == '43-':
                    self.serial = '43-' + child.text

                if child.tag == "CalibrationDate" and child.text != None and self.date == None:
                    self.date = datetime.datetime.strptime(child.text, "%d-%b-%y").strftime("%Y%m%d")
                name = self.coefficient_name_map.get(key)
                if name is None:
                    continue
                self.coefficients[name] = child.text

    def read_cal(self, filename):
        with open(filename) as fh:
            for line in fh:
                parts = line.split('=')

                if len(parts) != 2:
                    continue  # skip anything that is not key value paired

                key = parts[0]
                value = parts[1].strip()

                if key == 'INSTRUMENT_TYPE' and value != 'SBE43':
                    print('Error - unexpected type calibration file (%s != SBE43)' % value)
                    sys.exit(1)

                if self.coefficient_name_map.has_key(key):
                    name = self.coefficient_name_map.get(key)
                    self.coefficients[name] = value
                    if name == 'CC_voltage_offset':
                        self.coefficients['CC_frequency_offset'] = value

                if key == "OCALDATE":
                    cal_date = value
                    cal_date = datetime.datetime.strptime(cal_date, "%d-%b-%y").strftime("%Y%m%d")
                    self.date = cal_date

                if key == "SERIALNO":
                    self.serial = "43-" + str(value)

def main():
    # Starts in the directory with
    # Get corresponding mapping between serial number and uid
    lookup = get_uid_serial_mapping('DOFSTA/dofsta_lookup.csv')
    #Begin writing files
    for path, directories, files in os.walk('DOFSTA/manufacturer'):
        for file in files:
            # Skip hidden files
            if file[0] == '.':
                continue
            cal = SBE43Calibration()
            with open(os.path.join(path, file)) as unknown_file:
                c = unknown_file.read(1)
                if c == '<':
                    cal.read_xml(os.path.join(path, file))
                else:
                    cal.read_cal(os.path.join(path, file))
                cal.asset_tracking_number = lookup[cal.serial]
                cal.write_cal_info()
                cal.move_to_archive(cal.type, file)


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("DOFSTA: %s seconds" % (time.time() - start_time))

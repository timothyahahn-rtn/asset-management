#!/usr/bin/env python

# NUTNR calibration parser
#
# Create the necessary CI calibration ingest information from an NUTNR calibration file

import csv
import datetime
import os
import sys
import time
import json
from common_code.cal_parser_template import Calibration, get_uid_serial_mapping

class NUTNRCalibration(Calibration):
    def __init__(self, lower=217, upper=240):
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
        self.type = 'NUTNRA'
        self.coefficients = {'CC_lower_wavelength_limit_for_spectra_fit' : self.lower_limit,
                            'CC_upper_wavelength_limit_for_spectra_fit' : self.upper_limit}

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
                            self.coefficients['CC_cal_temp'] = self.cal_temp
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
                    self.coefficients['CC_wl'] = json.dumps(self.wavelengths)
                    self.coefficients['CC_eno3'] = json.dumps(self.eno3)
                    self.coefficients['CC_eswa'] = json.dumps(self.eswa)
                    self.coefficients['CC_di'] = json.dumps(self.di)

def main():
    lookup = get_uid_serial_mapping('NUTNRA/nutnr_lookup.csv')
    for path, directories, files in os.walk('NUTNRA/manufacturer'):
        for file in files:
            cal = NUTNRCalibration()
            cal.read_cal(os.path.join(path, file))
            cal.asset_tracking_number = lookup[cal.serial]
            cal.write_cal_info()


if __name__ == '__main__':
    start_time = time.time()
    main()
    print("NUTNR: %s seconds" % (time.time() - start_time))

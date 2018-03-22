#!/usr/bin/env python

##
# CTD Calibration Parser
# Create the necessary CI calibration ingest information from an CTD calibration file


import csv, datetime, os

class CTDCalibration:
    ## Class that stores calibration values for CTDs.
    # \param self
    def __init__(self):
        self.coefficient_name_map = {
            'TA0': 'CC_a0',
            'TA1': 'CC_a1',
            'TA2': 'CC_a2',
            'TA3': 'CC_a3',
            'CPCOR': 'CC_cpcor',
            'CTCOR': 'CC_ctcor',
            'CG': 'CC_g',
            'CH': 'CC_h',
            'CI': 'CC_i',
            'CJ': 'CC_j',
            'PA0': 'CC_pa0',
            'PA1': 'CC_pa1',
            'PA2': 'CC_pa2',
            'PTEMPA0': 'CC_ptempa0',
            'PTEMPA1': 'CC_ptempa1',
            'PTEMPA2': 'CC_ptempa2',
            'PTCA0': 'CC_ptca0',
            'PTCA1': 'CC_ptca1',
            'PTCA2': 'CC_ptca2',
            'PTCB0': 'CC_ptcb0',
            'PTCB1': 'CC_ptcb1',
            'PTCB2': 'CC_ptcb2',
            # additional types for series O
            'C1': 'CC_C1',
            'C2': 'CC_C2',
            'C3': 'CC_C3',
            'D1': 'CC_D1',
            'D2': 'CC_D2',
            'T1': 'CC_T1',
            'T2': 'CC_T2',
            'T3': 'CC_T3',
            'T4': 'CC_T4',
            'T5': 'CC_T5',
        }
        # dictionary with calibration coefficient names and values
        self.coefficients = {}
        self.asset_tracking_number = None
        self.serial = '52-'
        self.date = None

    def read_cal(self, filename):
        ## Reads the calibration files and extracts out the necessary calibration values needed for CI.
        with open(filename) as fh:
            for line in fh:
                parts = line.split('=')

                if len(parts) != 2:
                    continue  # skip anything that is not key value paired

                key = parts[0]
                value = parts[1].strip()

                if key == 'INSTRUMENT_TYPE' and value == 'SEACATPLUS':
                    self.serial = '16-'

                if key == 'SERIALNO':
                    self.serial += value

                if key == 'CCALDATE':
                    self.date = datetime.datetime.strptime(value, "%d-%b-%y").strftime("%Y%m%d")

                name = self.coefficient_name_map.get(key)
                if name is None:
                    continue

                self.coefficients[name] = value

    def write_cal_info(self):
        if self.asset_tracking_number.find('66662') != -1:
            os.chdir("cal_sheets/CTDPFA")
        elif self.asset_tracking_number.find('67627') != -1:
            os.chdir("cal_sheets/CTDPFB")
        elif self.asset_tracking_number.find('67977') != -1:
            os.chdir("cal_sheets/CTDPFL")
        elif self.asset_tracking_number.find('69827') != -1:
            os.chdir("cal_sheets/CTDBPN")
        elif self.asset_tracking_number.find('69828') != -1:
            os.chdir("cal_sheets/CTDBPO")
        ## Writes the calibration information to a comma-separated value file
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name', 'value', 'notes'])
            for each in sorted(self.coefficients.items()):
                writer.writerow([self.serial] + list(each))
        os.chdir("../..")

def main():
    lookup = {}
    with open('ctd_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    for path, directories, files in os.walk('manufacturer'):
        for file in files:
            cal = CTDCalibration()
            cal.read_cal(os.path.join(path, file))
            cal.asset_tracking_number = lookup[cal.serial]
            cal.write_cal_info()

if __name__ == '__main__':
    main()

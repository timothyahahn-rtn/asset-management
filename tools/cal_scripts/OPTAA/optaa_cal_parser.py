#!/usr/bin/env python

# OPTAA calibration parser
#
# Create the necessary CI calibration ingest information from an OPTAA calibration file

import csv
import json
import os
import sys
import string
import datetime


class OPTAACalibration:
    def __init__(self, serial):
        self.asset_tracking_number = None
        self.cwlngth = []
        self.awlngth = []
        self.tcal = None
        self.tbins = None
        self.ccwo = []
        self.acwo = []
        self.tcarray = []
        self.taarray = []
        self.nbins = None  # number of temperature bins
        self.serial = serial
        self.date = None

    def read_cal(self, filename):
        with open(filename) as fh:
            for line in fh:
                parts = line.split(';')
                if len(parts) != 2:
                    parts = line.split()
                    if parts[0] == '"tcal:':
                        self.tcal = parts[1]
                        cal_date = parts[-1:][0].strip(string.punctuation)
                        self.date = datetime.datetime.strptime(cal_date, "%m/%d/%y").strftime("%Y%m%d")
                    continue
                data, comment = parts

                if comment.startswith(' temperature bins'):
                    self.tbins = data.split()
                    self.tbins = [float(x) for x in self.tbins]

                elif comment.startswith(' number of temperature bins'):
                    self.nbins = int(data)

                elif comment.startswith(' C and A offset'):
                    if self.nbins is None:
                        print 'Error - failed to read number of temperature bins'
                        sys.exit(1)
                    parts = data.split()
                    self.cwlngth.append(float(parts[0][1:]))
                    self.awlngth.append(float(parts[1][1:]))
                    self.ccwo.append(float(parts[3]))
                    self.acwo.append(float(parts[4]))
                    tcrow = [float(x) for x in parts[5:self.nbins+5]]
                    tarow = [float(x) for x in parts[self.nbins+5:2*self.nbins+5]]
                    self.tcarray.append(tcrow)
                    self.taarray.append(tarow)

    def write_cal_info(self):
        file_name = self.asset_tracking_number + '__' + self.date
        with open('%s.csv' % file_name, 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name','value','notes'])
            writer.writerow([self.serial,'CC_acwo', json.dumps(self.acwo)])
            writer.writerow([self.serial,'CC_awlngth', json.dumps(self.awlngth)])
            writer.writerow([self.serial,'CC_ccwo', json.dumps(self.ccwo)])
            writer.writerow([self.serial,'CC_cwlngth', json.dumps(self.cwlngth)])
            writer.writerow([self.serial,'CC_taarray', 'SheetRef:CC_taarray'])
            writer.writerow([self.serial,'CC_tbins', json.dumps(self.tbins)])
            writer.writerow([self.serial,'CC_tcal', self.tcal])
            writer.writerow([self.serial,'CC_tcarray', 'SheetRef:CC_tcarray'])

        def write_array(filename, cal_array):
            with open(filename, 'w') as out:
                array_writer = csv.writer(out)
                array_writer.writerows(cal_array)

        write_array('%s__CC_tcarray.ext' % file_name, self.tcarray)
        write_array('%s__CC_taarray.ext' % file_name, self.taarray)

def main():
    lookup = {}
    with open('optaa_lookup.csv', 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']

    os.chdir('manufacturer')
    for sheet in os.listdir(os.getcwd()):
        sheet_name = os.path.basename(sheet).partition('.')[0].upper()
        sheet_name = sheet_name[:3] + '-' + sheet_name[3:]
        cal = OPTAACalibration(sheet_name)
        cal.read_cal(sheet)
        cal.asset_tracking_number = lookup[cal.serial]
        if cal.asset_tracking_number.find('58332') != -1:
            os.chdir("../cal_sheets/OPTAAD")
        elif cal.asset_tracking_number.find('69943') != -1:
            os.chdir("../cal_sheets/OPTAAC")
        cal.write_cal_info()
        os.chdir("../../manufacturer")
    os.chdir('..')

if __name__ == '__main__':
    main()

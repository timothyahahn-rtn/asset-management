#!/usr/bin/env python
'''
Common code shared between the different parsers in this file. Includes a Calibration object that
defines some default fields and functions. Also includes a function to parse through a csv that shows
the link between serial numbers and UIDs.
'''
import csv
import datetime
import os
import sqlite3
import sys
import time

class Calibration(object):
    def __init__(self):
        self.asset_tracking_number = None
        self.serial = None
        self.date = None
        self.coefficients = {}
        self.type = None

    def write_cal_info(self):
        if not self.get_uid():
            return
        complete_path = os.path.join(os.path.realpath('../..'), 'calibration', self.type)
        file_name = self.asset_tracking_number + '__' + self.date
        with open(os.path.join(complete_path, '%s.csv' % file_name), 'w') as info:
            writer = csv.writer(info)
            writer.writerow(['serial','name', 'value', 'notes'])
            for each in sorted(self.coefficients.items()):
                row = [self.serial] + list(each)
                row.append('')
                writer.writerow(row)

    def move_to_archive(self, inst_type, file):
        os.rename(os.path.join(os.getcwd(), inst_type, 'manufacturer', file), \
                    os.path.join(os.getcwd(), inst_type, 'manufacturer_ARCHIVE', file))
    
    def get_uid(self):
        sql = sqlite3.connect('instrumentLookUp.db')
        uid_query_result = sql.execute('select uid from INSTRUMENT_LOOKUP where serial=:sn',\
                                             {'sn':self.serial}).fetchone()
        if len(uid_query_result) != 1:
            return False
        self.asset_tracking_number = uid_query_result[0]
        return True

def get_uid_serial_mapping(csv_name):
    lookup = {}
    with open(csv_name, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=",")
        for row in reader:
            lookup[row['serial']] = row['uid']
    return lookup

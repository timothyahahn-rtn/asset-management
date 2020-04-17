#!/usr/bin/env python3

import sqlite3

new_serial = input('New Sensor serial #: ')
new_uid = input('New Sensor Asset ID: ')

proceed = input('Confirm ' + str(new_serial) + ', ' + str(new_uid) + ' will be added to the database: enter Y to proceed, N to cancel: ').upper()

if proceed == 'Y':
    sql = sqlite3.connect('instrumentLookUp.db')
    addString = 'INSERT INTO instrument_lookup (serial, uid) VALUES ("' + new_serial + '","' + new_uid + '")'
    insert_request = sql.execute(addString).fetchall()
    sql.commit()
    sql.close()

elif proceed == 'N':
    print('request canceled')

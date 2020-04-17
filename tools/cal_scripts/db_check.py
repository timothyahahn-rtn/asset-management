#!/usr/bin/env python

import os
import pandas as pd
import sqlite3

bulk_path = os.path.join(os.path.abspath('../..'),
                         'bulk/sensor_bulk_load-AssetRecord.csv')
bulk_df = pd.read_csv(bulk_path)
sql = sqlite3.connect('instrumentLookUp.db')
request = sql.execute('SELECT * FROM instrument_lookup').fetchall()

for query in request:
    print(query)
    try:
        results = bulk_df.loc[bulk_df['ASSET_UID'] == query[1]]['ASSET_UID']
    except KeyError:
        print('not found')

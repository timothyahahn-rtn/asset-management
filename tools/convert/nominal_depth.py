#!/usr/bin/env python

# Insert nominal depth (from preload_database/nominal_depths.csv) into deployment sheets
import csv
import fnmatch
import os

import sys


def get_nominal_depths(path):
    rdict = {}
    with open(path) as fh:
        reader = csv.reader(fh)
        next(reader)
        for des, depth in reader:
            rdict[des] = depth

    return rdict


def update_deployment_file(path, nominal_depths):
    out = []
    with open(path) as fh:
        reader = csv.reader(fh)
        out.append(next(reader) + ['notes'])
        for row in reader:
            refdes = row[4]
            depth = nominal_depths.get(refdes)
            if depth is None or depth == 'VAR':
                out.append(row[:-1] + ['', ''])
            else:
                out.append(row[:-1] + [depth, 'nominal_depth'])

    with open(path, 'w') as fh:
        writer = csv.writer(fh, lineterminator='\n')
        writer.writerows(out)


def update_deployments(deploy_dir, nominal_file):
    depths = get_nominal_depths(nominal_file)
    for path, _, files in os.walk(deploy_dir):
        for f in fnmatch.filter(files, '*.csv'):
            update_deployment_file(os.path.join(path, f), depths)


nominal_file = sys.argv[1]
deploy_dir = sys.argv[2]
update_deployments(deploy_dir, nominal_file)
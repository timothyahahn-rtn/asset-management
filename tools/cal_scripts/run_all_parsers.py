#!/usr/bin/env python
import os, glob, subprocess
import time

def main():
    for sub in os.listdir(os.getcwd()):
        if os.path.isdir(sub):
            os.chdir(sub)
            # Checks if there are any cal files in Manufacturer Cal Files and do not
            # redo sheets that have already been made.
            if len(os.listdir('manufacturer_cal_files')) != 0 and\
             len(os.listdir('manufacturer_cal_files')) != len(os.listdir('cal_sheets')):
                for file in glob.glob('*.py'):
                    command = ['python2.7', file]
                    p = subprocess.Popen(command)
            os.chdir("..")

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

#!/usr/bin/env python
import os, glob, subprocess
import time

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))

def main():
    for sub in os.listdir(os.getcwd()):
        if os.path.isdir(sub) and sub != 'common_code':
            os.chdir(sub)
            # Checks if there are any cal files in Manufacturer Cal Files
            # TODO: Find way of not running script on duplicate
            if len(os.listdir('manufacturer')) != 0:
                for file in glob.glob('*.py'):
                    command = ['python2.7', file]
                    p = subprocess.Popen(command)
            os.chdir("..")

if __name__ == '__main__':
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))

# OOI Instrument Parsers

 The following scripts extract calibration information from various manufacturer calibration sheets. These calibration sheets define the values that various instruments use to calibrate themselves for data acquisition.
 They allow for the automated creation of calibration files in the format requested by ooi-integration.
 Serial numbers and asset tracking numbers can be found in the [asset-management](
 https://github.com/ooi-integration/asset-management) repository.

These scripts are based on those written by Dan Mergens, who developed the original scripts which can still be found in the [ooi-tools](https://github.com/oceanobservatories/ooi-tools/tree/master/instrument/calibration) repository.

## Getting Started

Clone the repository into your local machine. In the repository, there are a set of directories of each of the supported instrument types.

### Prerequisites

* Python 2.7
* Linux terminal emulator

If you do not already have Python installed on your computer, you will need to install it to make this program work.
On Linux, run the following command.
```
sudo apt-get install python2.7
```
On MacOS, if you have Homebrew, call this command
```
brew install python2.7
```
On Windows, install Cygwin or preferred terminal emulator. Make sure to select python as part of the installation process.
Another method is to use the Linux Subsystem available on Windows 10.

## Running the code

Navigate to the repository and in whatever terminal. There are a series of folders which contain the parsers and subdirectories containing . Put the calibration files in the "manufacturer" directory.

Run the script by calling the corresponding parser.

```
./ctd_cal_parser.py
./dofsta_cal_parser.py
./flntua_cal_parser.py
./flor_cal_parser.py
./nutnr_cal_parser.py
./optaa_cal_parser.py
./spkir_cal_parser.py
```

These can also be run by calling the Python command and having the script be an argument to it.

```
python ctd_cal_parser.py
python dofsta_cal_parser.py
python flntua_cal_parser.py
python flor_cal_parser.py
python nutnr_cal_parser.py
python optaa_cal_parser.py
python spkir_cal_parser.py
```

The parsers will go through each file and add the completed files into the "Cal Sheets" folder in the respective instruments. If the number of files is equal

To run all scripts, call the script run_all_parsers.py.

```
./run_all_parsers.py
or
python run_all_parsers.py
```

## Authors

* **Dan Mergens** - *Initial work of writing the scripts* - [danmergens](https://github.com/danmergens)
* **Daniel Tran** - *Modifications and System Setup* - [funnyabc](https://github.com/funnyabc)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Dan Mergens for starting the calibration scripts

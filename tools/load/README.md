# Loading Asset Management

Instructions for performing a clean install of asset management data.

### Create python virtualenv with the necessary modules

with virtualenv / pip:

```
mkvirtualenv asset_load
pip install -U pip
pip install pandas xlsxwriter
```

with conda:

```
conda create -n asset_load pandas xlsxwriter
source activate asset_load
```

### Generate the XLSX files

These instructions assume you are using all the files located in this
repository, but these scripts can be pointed at any directory containing
files in the appropriate format.

```
mkdir cruise deploy cal
./load_cruises.py ../../cruise/*.csv cruise/.
./load_deploy.py ../../deployment/*.csv deploy/.
./load_cal.py ../../calibration cal
```

### Remove existing asset management data

Now that all the input files are prepared we can purge the existing
data from the system. Note that once we purge this data retrieval of
asset information and production derived products will be affected
until we have completed reloading this data.

#### Drop data

Open the asset management database using a SQL editor. For example:
```
$ source activate pgcli
$ pgcli metadata awips
```

Then execute the following commands to drop the asset management tables:
```
truncate table xacquisition cascade;
truncate table xarray cascade;
truncate table xasset cascade;
-- truncate table xasset_xevents cascade;  -- if exists
truncate table xasset_xremoteresource cascade;
truncate table xassetstatusevent cascade;
truncate table xatvendor cascade;
truncate table xcalibration cascade;
truncate table xcalibrationdata cascade;
truncate table xcruiseinfo cascade;
truncate table xdeployment cascade;
truncate table xevent cascade;
truncate table xinstrument cascade;
truncate table xintegrationevents cascade;
truncate table xlocationevent cascade;
truncate table xmooring cascade;
truncate table xnode cascade;
truncate table xremoteresource cascade;
truncate table xretirement cascade;
truncate table xstorage cascade;
```

#### Reset sequences

```
alter sequence xasset_m_seq restart;
alter sequence xevent_seq restart;
```

### Load the cruise data

```
export XAD=/path/to/uframes/ooi/uframe-1.0/edex/data/ooi/xasset_spreadsheet
mv cruise/* $XAD
```

Observe the edex log, completion is indicated as follows:

```
INFO  2017-02-10 16:23:59,756 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] CruiseInfoSheetParser: EDEX - Processing sheet [CruiseInformation]:complete
INFO  2017-02-10 16:23:59,761 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Completed processing file [/edex/data/ooi/xasset_spreadsheet/CruiseInformation.xlsx]
```

### Load the bulk asset data

Note, these files are located in the base of this repository in the folder
labeled "bulk"

```
cp *-AssetRecord.csv $XAD
```

Each record ingested from a bulk file will create a log message like this:

```
INFO  2017-02-10 16:27:33,233 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XAssetSheetParser: EDEX - Created asset record [XArray] for uid = N00296
```

And the complete ingestion of a file will result in this:

```
INFO  2017-02-10 16:27:33,446 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Completed processing file [/edex/data/ooi/xasset_spreadsheet/array_bulk_load-AssetRecord.csv]
```

Ensure that ALL bulk entries have been processed prior to proceeding.
This should take approximately one minute.

### Load the deployment and calibration data

Once the cruise and bulk information has been loaded the deployment
and calibration data can be loaded in any order.

```
mv deploy/* $XAD
mv cal/* $XAD
```

Deployment records produce log entries as follows:

```
INFO  2017-02-10 16:32:48,191 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XDeploymentDao: EDEX - Saving Deployment [CE07SHSP-SP001-09-PARADJ000:2:1]
INFO  2017-02-10 16:32:48,217 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XDeploymentDao: EDEX - Created Deployment [CE07SHSP-SP001-09-PARADJ000:2:1]
INFO  2017-02-10 16:32:48,218 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XDeploymentSheetParser: EDEX - Processing sheet [CE07SHSP_Deploy]:complete
INFO  2017-02-10 16:32:48,218 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Completed processing file [/edex/data/ooi/xasset_spreadsheet/CE07SHSP_Deploy.xlsx]
```

And calibration records:

```
INFO  2017-02-10 16:34:21,121 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Starting to process file [/edex/data/ooi/xasset_spreadsheet/ATAPL-58337-00003__20140929_Cal_Info.xlsx]
INFO  2017-02-10 16:34:21,133 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XCalibrationSheetParser: EDEX - Processing sheet [Asset_Cal_Info]:starting
INFO  2017-02-10 16:34:21,153 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XCalibrationSheetParser: EDEX - Calibration data added for sensor uid=ATAPL-58337-00003
INFO  2017-02-10 16:34:21,153 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XCalibrationSheetParser: EDEX - Processing sheet [Asset_Cal_Info]:complete
```

As files are processed they are removed from the ingest folder ($XAD).
Once this folder is empty ingestion is complete. This should take
approximately five minutes.

### Reset the UI Asset Management Cache

Enter the following commands from a terminal where Redis is installed:

```
redis-cli del "flask_cache_asset_list"
redis-cli del "flask_cache_assets_dict"
```

Navigate in Google Chrome to:
https://ooinet-dev-01.oceanobservatories.org/assets/management/

The cache keys will reload in 1-2 minutes.





# Loading Individual Deployments/Cruises/Calibrations for Testing (uft3 only)

Instructions for installing asset management data for a single instrument.

### Load the Conda Environemnt

```
source activate asset_load
```

### Generate the XLSX files

First, create a temporary folder somewhere (e.g. ~/sheets/), and within
that folder create folders for each type of asset mgmt. data and copy or
create the appropriate asset management .csv filese in those directories
(e.g. RS01SBPS_Deploy.csv; you can include more than one):
```
mkdir -p ~/sheets/cal ~/sheets/cruise ~/sheets/deploy
```

Then use the load tools to convert these to .xlsx files:

```
cd ~/uframes/repos/asset-management/tools/load
python load_cruises.py ~/sheets/cruise/ ./cruise/
python load_deploy.py ~/sheets/deploy/ ./deploy/
python load_cal.py ~/sheets/cal/ ./cal/
```
The resultant .xlsx filse will end up in the ./cruise, ./deploy, and ./cal
directories.


### Load the cruise data

```
export XAD=~/uframes/ooi/uframe-1.0/edex/data/ooi/xasset_spreadsheet/
mv cruise/* $XAD
```

Observe the edex log, completion is indicated as follows:

```
INFO  2017-02-10 16:23:59,756 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] CruiseInfoSheetParser: EDEX - Processing sheet [CruiseInformation]:complete
INFO  2017-02-10 16:23:59,761 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Completed processing file [/edex/data/ooi/xasset_spreadsheet/CruiseInformation.xlsx]
```

### Load the deployment and calibration data

Once the cruise and bulk information has been loaded the deployment
and calibration data can be loaded in any order.

```
mv deploy/* $XAD
mv cal/* $XAD
```

Deployment records produce log entries as follows:

```
INFO  2017-02-10 16:32:48,191 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XDeploymentDao: EDEX - Saving Deployment [CE07SHSP-SP001-09-PARADJ000:2:1]
INFO  2017-02-10 16:32:48,217 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XDeploymentDao: EDEX - Created Deployment [CE07SHSP-SP001-09-PARADJ000:2:1]
INFO  2017-02-10 16:32:48,218 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XDeploymentSheetParser: EDEX - Processing sheet [CE07SHSP_Deploy]:complete
INFO  2017-02-10 16:32:48,218 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Completed processing file [/edex/data/ooi/xasset_spreadsheet/CE07SHSP_Deploy.xlsx]
```

And calibration records:

```
INFO  2017-02-10 16:34:21,121 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XIngestor: EDEX - Starting to process file [/edex/data/ooi/xasset_spreadsheet/ATAPL-58337-00003__20140929_Cal_Info.xlsx]
INFO  2017-02-10 16:34:21,133 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XCalibrationSheetParser: EDEX - Processing sheet [Asset_Cal_Info]:starting
INFO  2017-02-10 16:34:21,153 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XCalibrationSheetParser: EDEX - Calibration data added for sensor uid=ATAPL-58337-00003
INFO  2017-02-10 16:34:21,153 [Camel (camel-1) thread #7 - file:///edex/data/ooi/xasset_spreadsheet] XCalibrationSheetParser: EDEX - Processing sheet [Asset_Cal_Info]:complete
```

As files are processed they are removed from the ingest folder ($XAD).
Once this folder is empty ingestion is complete. This should take
approximately five minutes.

### Reset the UI Asset Management Cache

Enter the following commands from a terminal where Redis is installed:

```
redis-cli del "flask_cache_asset_list"
redis-cli del "flask_cache_assets_dict"
```

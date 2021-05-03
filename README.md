# Metre_AppUI_v0.16

1) MainMetre.py is the installer/code launcher. **If the root directory (MetreiOS) already exists** on your device, it will look for metre_ios_install_config.json and launch the most current version of the app (from a subdirectory in MetreiOS) OR it will download the most current version of the app from GitHub, installed as a subdirectory in MetreiOS. If an older version of the app exists, the log files (for remembering the device, timezone, storage of previous data) will get copied over to the new app subdirectory. **If the MetreiOS subdirectory does not exist** it will download that root directory and make metre_ios_install_config.json (version # is hard-coded into a dictionary written in MainMetre.py). The script that "does stuff" and makes the UI is the script MetreUI.py

2) MetreUI.py makes the UI. Currently, as written, this version of the code expects to receive a json file (similar to the format in temp_resources). It looks for files that are located in the folder temp_resources. It processes the test by calling the script process_test.py, which does the mV rolling mean and various metadata calculations, adds the keys to the dictionary. The dietionary gets returned to MetreUI.py (the main script) and pushes it to the cloud function 'https://us-central1-metre3-1600021174892.cloudfunctions.net/metre-7500'.

3) The cloud function writes the metadata to a common log, saves the incoming (single) json file, runs the prediction, and returns the prediction to MetreUI.py

4) MetreUI.py receives the response from the cloud function, displays the result and writes it to the log.

5) If multiple files are present in temp_resources, multiple files will be uploaded.

## Updates from v0.15:

1) Add screen lockout to prevent phone from locking while app is running in the forefront (10 min max for running iin the background)
2) Increased timeout counter from 15 to 60 for a response (if files > 20, can take more than 30 seconds to get response from listdir)


## To add
1) File size check (for s2_sample generated files that don't terminate correctly and thus never finish transferring)
2) Check instrument state --when km3v11_32u4 comes out (i.e. check to see if instrument is "SET" before sending commands)
3) Check battery levels

# PrEWInputProduction

Python scripts which are used to extract the distribution from the ROOT TTrees that the processors produced and produce input for the PrEW fitting framework.

## Requirements

Make sure to load modern ROOT (e.g. 6.18) and Python (e.g. 3.8) versions. Some additional Python packages may be required (see the import statements at the top of the scripts).

## Usage

Each process has its own folder. The script that is named `[process].py` can be executed with Python to produce the PrEW input sample, e.g.:

```
  cd WW && python WW.py
```

(make sure you run them in their directory so all the local modules are found.)

### Output

The typical output is in the form of CSV files with a custom header which can be read by PrEW (or looked at directly by any text viewer). Standard CSV readers won't be able to read the output due to the custom header.
#!/bin/bash

echo "#########################################################################"
echo "### Loading needed software versions ####################################" 
echo "#########################################################################"

# Load up-to-date iLCSoft 
ilcsoft_dir="/cvmfs/ilc.desy.de/sw/x86_64_gcc82_sl6/v02-02"

if [[ "${ILCSOFT}" == *"${ilcsoft_dir}"* ]]; then
  echo "iLCSoft version is already loaded."
elif [ ! -z "${ILCSOFT}" ]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "ERROR: Another iLCSoft version is already loaded!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
else 
  source ${ilcsoft_dir}/init_ilcsoft.sh
fi
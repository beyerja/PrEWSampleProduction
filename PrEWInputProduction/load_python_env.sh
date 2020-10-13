#!/bin/bash

echo "#########################################################################"
echo "### Loading needed software versions ####################################" 
echo "#########################################################################"

# Load a modern LCG version (a full view including ROOT and Python3)
lcg_version=98python3

if [[ "${LCG_VERSION}" == "${lcg_version}" ]]; then 
  echo "LCG view already loaded."
elif [ ! -z "${LCG_VERSION}" ]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "ERROR: Another LCG view is already loaded!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
else 
  echo "Loading LCG view - version: ${lcg_version}" 
  source /cvmfs/sft.cern.ch/lcg/views/LCG_${lcg_version}/x86_64-centos7-gcc8-opt/setup.sh
fi  
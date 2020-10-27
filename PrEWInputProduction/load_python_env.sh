#!/bin/bash

echo "#########################################################################"
echo "### Loading needed software versions ####################################" 
echo "#########################################################################"

# Load the config to determine the LCG view (including ROOT and Python3)
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )" # this script
config_dir="${dir}/../scripts/config"
. ${config_dir}/software.config

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
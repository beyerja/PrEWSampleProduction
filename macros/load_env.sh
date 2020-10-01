#!/bin/bash

echo "#########################################################################"
echo "### Loading needed software versions ####################################" 
echo "#########################################################################"

# Load up-to-date iLCSoft 
ilcsoft_version="v02-02"
ilcsoft_dir="/cvmfs/ilc.desy.de/sw/x86_64_gcc82_sl6/${ilcsoft_version}"

if [[ "${ILCSOFT}" == *"${ilcsoft_dir}"* ]]; then
  echo "iLCSoft version is already loaded."
elif [ ! -z "${ILCSOFT}" ]; then
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
  echo "ERROR: Another iLCSoft version is already loaded!"
  echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
else 
  echo "Loading iLCSoft - version: ${ilcsoft_version}"
  source ${ilcsoft_dir}/init_ilcsoft.sh
fi

# Add the MarlinHelp package path
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/afs/desy.de/group/flc/pool/beyerjac/TGCAnalysis/SampleProduction/MarlinAnalysis/MarlinHelp/lib
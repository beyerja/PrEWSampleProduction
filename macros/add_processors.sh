#!/bin/bash

echo "#########################################################################"
echo "### Adding compiled processors to Marlin ################################" 
echo "#########################################################################"

# Directory of this script
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )"

# Adding processors
lib_name="libPrEWSampleProduction.so"
lib_path=${dir}/../lib/${lib_name}

if [[ "${MARLIN_DLL}" == *"${lib_name}"* ]]; then
  echo "Marlin knows processor already."
else
  export MARLIN_DLL=${MARLIN_DLL}:${lib_path}
fi


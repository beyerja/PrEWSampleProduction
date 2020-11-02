#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined

script_path=false
input_file=false
output_file=false
unboost_crossing_angle=""

# ------------------------------------------------------------------------------
# Read input
for i in "$@"
do
case $i in
  --script-path=*)
    script_path="${i#*=}"
    shift # past argument=value
  ;;
  --input-file=*)
    input_file="${i#*=}"
    shift # past argument=value
  ;;
  --output-file=*)
    output_file="${i#*=}"
    shift # past argument=value
  ;;
  --unboost-crossing-angle=*)
    unboost_crossing_angle="${i#*=}"
    shift # past argument=value
  ;;
  -h|--help)
    echo "usage: ./configure_script.sh --script-path=[...] [--input-file=...] [--output-file=...] [--unboost-crossing-angle=[true,false]]"
    shift # past argument=value
  ;;
  *)
    # unknown option
    shift
  ;;
esac
done

# ------------------------------------------------------------------------------
# Check input arguments:

if [ "$script_path" = false ]; then
  >&2 echo "No script path given!"; exit 1
fi

# ------------------------------------------------------------------------------
# Function that takes the script, searches for a given token, and replaces the 
# line of the token with the given replacement

replace_token() {
  sed -i "s|${token}|${replacement}|g" ${script_path}
}

# ------------------------------------------------------------------------------
# Replace whatever is requested using the appropriate token

if [ "$input_file" != false ]; then
  token=INPUT_FILE_TOKEN
  replacement=$input_file
  replace_token
fi

if [ "$output_file" != false ]; then
  token=OUTPUT_FILE_TOKEN
  replacement=$output_file
  replace_token
fi

# Crossing angle token must be set either way
if [ "$unboost_crossing_angle" != "" ]; then
  token=UNBOOST_CROSSINGANGLE_TOKEN
  replacement=$unboost_crossing_angle
  replace_token
else 
  >&2 echo "Need to knew if crossing angle should be unboosted! Must be given in input config using unboost_crossing_angle variable."; exit 1
fi

# ------------------------------------------------------------------------------
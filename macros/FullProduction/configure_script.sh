#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined

script_path=false
input_file=false
output_file=false

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
  -h|--help)
    echo "usage: ./configure_script.sh --script-path=[...] [--input-file=...] [--output-file=...]"
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

# ------------------------------------------------------------------------------
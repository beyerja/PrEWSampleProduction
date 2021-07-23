#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined

script_path=false
input_file=false
tgc_config=false
tgc_points_file=false

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
  --tgc-config=*)
    tgc_config="${i#*=}"
    shift # past argument=value
  ;;
  --tgc-points-file=*)
    tgc_points_file="${i#*=}"
    shift # past argument=value
  ;;
  -h|--help)
    echo "usage: ./configure_script.sh --script-path=[...] --input-file=[...] --tgc-config=[...] --tgc-points-file=[...]"
    shift # past argument=value
  ;;
  *)
    # unknown option
    shift
  ;;
esac
done

# ------------------------------------------------------------------------------
# Directoy of this script
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )"

# ------------------------------------------------------------------------------
# Check input arguments:

if [ "$script_path" = false ]; then
  >&2 echo "No script path given!"; exit 1
fi

if [ "$input_file" = false ]; then
  >&2 echo "No input file given!"; exit 1
fi

if [ "$tgc_config" = false ]; then
  >&2 echo "No TGC config given!"; exit 1
fi

if [ "$tgc_points_file" = false ]; then
  >&2 echo "No TGC points given!"; exit 1
fi

# ------------------------------------------------------------------------------
# Determine the process ID and the intial chirality from the file name

chirality=$(python ${dir}/InterpretFilename.py --file {$input_file} --chirality)
process_ID=$(python ${dir}/InterpretFilename.py --file {$input_file} --process-ID)

# ------------------------------------------------------------------------------
# Get the TGC points in sindarin language

TGC_points=$(python ${dir}/TGCs2Sindarin.py --config-path ${tgc_config} --points-path ${tgc_points_file})

# ------------------------------------------------------------------------------
# Strip input file of ".slcio"

input_file="${input_file%.*}"

# ------------------------------------------------------------------------------
# Function that takes the script, searches for a given token, and replaces the 
# line of the token with the given replacement

replace_token() {
  sed -i "s|${token}|${replacement}|g" ${script_path}
}

# ------------------------------------------------------------------------------
# Replace all tokens
token=BEAM_CHIRALITY_TOKEN
replacement=$chirality
replace_token

token=PROCESS_ID_TOKEN
replacement=$process_ID
replace_token

token=INPUT_PATH_TOKEN
replacement=$input_file
replace_token

token=TGC_POINTS_TOKEN
replacement="$TGC_points"
replace_token

# ------------------------------------------------------------------------------
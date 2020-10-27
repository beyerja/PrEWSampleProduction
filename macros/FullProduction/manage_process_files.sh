#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined
process=false
e_pol=false
p_pol=false
action=false
input_config=false
output_config=false

# ------------------------------------------------------------------------------
# Read input
for i in "$@"
do
case $i in
  --set-steeringfiles)
    action="set"
    shift # past argument=value
  ;;
  --combine-output)
    action="combine"
    shift # past argument=value
  ;;
  --clean-up)
    action="clean"
    shift # past argument=value
  ;;
  --process=*)
    process="${i#*=}"
    shift # past argument=value
  ;;
  --e-Pol=*)
    e_pol="${i#*=}"
    shift # past argument=value
  ;;
  --e+Pol=*)
    p_pol="${i#*=}"
    shift # past argument=value
  ;;
  --input-config=*)
    input_config="${i#*=}"
    shift # past argument=value
  ;;
  --output-config=*)
    output_config="${i#*=}"
    shift # past argument=value
  ;;
  -h|--help)
    echo "usage: ./manage_process_files.sh [--set-steeringfiles/--combine-output/--clean-up] --process=[4f_WW_sl/4f_sW_sl/...] --e-Pol=[eL/eR] --e+Pol=[pL/pR] --input-config=[...] --output-config=[...]"
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

if [ "$action" = false ]; then
  >&2 echo "No action given!"; exit 1
fi

if [ "$process" = false ]; then
  >&2 echo "No final state given!"; exit 1
fi

if [ "$e_pol" = false ]; then
  >&2 echo "No e- polarisation given!"; exit 1
fi

if [ "$p_pol" = false ]; then
  >&2 echo "No e+ polarisation given!"; exit 1
fi

if [ "$input_config" = false ]; then
  >&2 echo "No input config file given!"; exit 1
fi

if [ "$output_config" = false ]; then
  >&2 echo "No output config file given!"; exit 1
fi

# ------------------------------------------------------------------------------
# Directoy of this script
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )"

# ------------------------------------------------------------------------------
# Get input and output paths
. ${input_config}
. ${output_config}

# ------------------------------------------------------------------------------
# Directory structure for the Marlin XML scripts
scripts_dir=${dir}/../../scripts

# The template Marlin script
template_path=${scripts_dir}/templates/${process}.xml

# Base name and steering directory for specific to the input variables
base_name=${process}_${e_pol}_${p_pol}
tmp_base_name=tmp_${base_name}
tmp_steering_directory=${scripts_dir}/${tmp_base_name}

# ------------------------------------------------------------------------------
# Determine output process-dependent output directories
process_output_directory=${output_dir}/${process}
tmp_output_directory=${process_output_directory}/tmp

# ------------------------------------------------------------------------------
# Perform the requested action

if  [[ ${action} == "set" ]]; then
  cd ${input_dir} # From the input config

  # Do case-insensitive (`-iname`) search in directory (and subdirectories) for relevant DST files 
  # according to convention of DST file naming and print complete paths (->`pwd`).
  files=$(find `pwd` -iname "*P${process}*${e_pol}.${p_pol}*.slcio" -print)
  file_steering_paths=() # Collect paths of steering files for job starting
  
  file_index=0
  for file in ${files[@]}; do
    if [[ $file == "" ]]; then
      exit 1 # If empty nofile found -> exit subprocess
    fi
    
    file_index=$((file_index + 1))
    
    tmp_steering_file=${tmp_steering_directory}/${tmp_base_name}_${file_index}_steering.xml
    tmp_output_file=${tmp_output_directory}/${tmp_base_name}_${file_index}.root
    
    if [[ ! -d ${tmp_steering_directory} ]] ; then # Create if not existing
      mkdir -p ${tmp_steering_directory}
    fi
    
    cp ${template_path} ${tmp_steering_file}
    ${dir}/configure_script.sh --script-path=${tmp_steering_file} --input-file=${file} --output-file=${tmp_output_file}
    
    file_steering_paths+="${tmp_steering_file} " # Keep track of steering file for job starting
  done
  
  echo ${file_steering_paths} # Echo steering files that need to be run
  
elif [[ ${action} == "combine" ]]; then
  hadd -k -f ${process_output_directory}/${base_name}.root ${tmp_output_directory}/${tmp_base_name}_*.root
  
elif [[ ${action} == "clean" ]]; then
  rm -r ${tmp_steering_directory}
  rm ${tmp_output_directory}/${tmp_base_name}_*.root
  
else   
  >&2 echo "In manage_process_files.sh: Unknown action '"${action}"' requested."
  >&2 echo "Options are: --set-steeringfiles --combine-output --clean-up"
  >&2 echo "Exiting."
  exit
fi
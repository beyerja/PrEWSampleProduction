#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined
process=false
e_pol=false
p_pol=false
action=false
input_config=false
output_config=false
tgc_config=false
tgc_points_file=false

# ------------------------------------------------------------------------------
# Read input
for i in "$@"
do
case $i in
  --set-rescanfiles)
    action="set"
    shift # past argument=value
  ;;
  --print-topdir)
    action="print"
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
  --tgc-config=*)
    tgc_config="${i#*=}"
    shift # past argument=value
  ;;
  --tgc-points-file=*)
    tgc_points_file="${i#*=}"
    shift # past argument=value
  ;;
  -h|--help)
    >&2 echo "usage: ./manage_rescan_files.sh [--set-rescanfiles/--clean-up] --process=[4f_WW_sl/4f_sW_sl/...] --e-Pol=[eL/eR] --e+Pol=[pL/pR] --input-config=[...] --output-config=[...] [--tgc-config=...] [--tgc-points-file=...]"
    exit 1 
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
elif [ "$process" = false ]; then
  >&2 echo "No final state given!"; exit 1
elif [ "$e_pol" = false ]; then
  >&2 echo "No e- polarisation given!"; exit 1
elif [ "$p_pol" = false ]; then
  >&2 echo "No e+ polarisation given!"; exit 1
elif [ "$input_config" = false ]; then
  >&2 echo "No input config file given!"; exit 1
elif [ "$output_config" = false ]; then
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
# Directory structures

# The template rescan script
scripts_dir=${dir}/../../scripts
template_name=${process}_rescan.sin
template_path=${scripts_dir}/templates/${template_name}

# ------------------------------------------------------------------------------
# Determine output process-dependent output directories
process_output_directory=${output_base}/${process} # output_base from config
rescan_topdir=${process_output_directory}/WhizardRescan/${e_pol}${p_pol}

# ------------------------------------------------------------------------------
# Perform the requested action

if [[ ${action} == "set" ]] || [[ ${action} == "print" ]]; then
  # Check if all necessary configs are given
  if [ "$tgc_config" = false ]; then
    >&2 echo "No TGC config given!"; exit 1
  elif [ "$tgc_points_file" = false ]; then
    >&2 echo "No TGC points given!"; exit 1
  fi
  
  cd ${input_dir} # From the input config

  # Do case-insensitive (`-iname`) search in directory (and subdirectories) for relevant DST files 
  # according to convention of DST file naming and print complete paths (->`pwd`).
  files=$(find `pwd` -iname "*P${process}*${e_pol}.${p_pol}*.slcio" -print)
  
  if [[ $files == "" ]]; then
    exit 1 # If empty no file found -> exit subprocess
  fi
  
  if [[ ${action} == "set" ]]; then
    # Setup up the rescan scripts if that was requested
    if [[ ! -d ${rescan_topdir} ]] ; then # Create if not existing
      mkdir -p ${rescan_topdir}
    fi
    cd ${rescan_topdir}
    
    for file in ${files[@]}; do
    
      file_number=$(python ${dir}/InterpretFilename.py --file ${file} --file-number)
      file_subdir=${rescan_topdir}/${file_number}
    
      if [[ ! -d ${file_subdir} ]] ; then # Create if not existing
        mkdir -p ${file_subdir}
      fi
    
      cp ${template_path} ${file_subdir}/.
      ${dir}/configure_script.sh --script-path=${file_subdir}/${template_name} --input-file=${file} --tgc-config=${tgc_config} --tgc-points-file=${tgc_points_file}
    done
  fi
  
  echo ${rescan_topdir}
  
elif [[ ${action} == "clean" ]]; then
  rm -f ${rescan_topdir}/*/{default_*,*.mod,*.f90,*.lo,*.o,*.la,*.makefile,*.phs} 
else   
  >&2 echo "In manage_rescan_files.sh: Unknown action '"${action}"' requested."
  >&2 echo "Exiting."
  exit
fi
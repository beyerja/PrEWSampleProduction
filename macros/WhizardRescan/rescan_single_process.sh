#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined
process=false
input_config=false
output_config=false
tgc_config=false
tgc_points_file=false
failed_only=false

# ------------------------------------------------------------------------------
# Read input
for i in "$@"
do
case $i in
  --process=*)
    process="${i#*=}"
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
  --failed-only)
    failed_only=true
    shift # past argument=value
  ;;
  -h|--help)
    echo "usage: ./rescan_single_process.sh --process=[4f_WW_sl/4f_sW_sl/...] --input-config=[...] --output-config=[...] --tgc-config=[...] --tgc-points-file=[...] [--failed-only]"
    echo "The optional --failed-only argument allows rerunning only previously failed rescans."
    exit
  ;;
  *)
    # unknown option
    shift
  ;;
esac
done

# ------------------------------------------------------------------------------
# Check input arguments:

if [ "$process" = false ]; then
  >&2 echo "No final state given!"; exit 1
elif [ "$input_config" = false ]; then
  >&2 echo "No input config file given!"; exit 1
elif [ "$output_config" = false ]; then
  >&2 echo "No output config file given!"; exit 1
elif [ "$tgc_config" = false ]; then
  >&2 echo "No TGC config given!"; exit 1
elif [ "$tgc_points_file" = false ]; then
  >&2 echo "No TGC points given!"; exit 1
fi

# ------------------------------------------------------------------------------
# Script environment
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )" # path of this macro

# Standard HTCondor environment
condor_directory=${dir}/../SubmitScripts
submit_script=${condor_directory}/submit_script_8h.submit

# Condor logging output 
. ${output_config}
condor_output_dir=${output_base}/CondorOutput/${process}

# ------------------------------------------------------------------------------
# Arrays with possible polarizations for looping
e_polarizations=("eL" "eR")
p_polarizations=("pL" "pR")

# ------------------------------------------------------------------------------
# Run each individual process / polarisation / process-file

echo "Start initalizing process ${process} rescanning."

for e_pol in "${e_polarizations[@]}"; do
  for p_pol in "${p_polarizations[@]}"; do
    echo "Initializing polarization ${e_pol} ${p_pol}."
      
    # Array to collect condor job IDs so that I can keep track of if any are still running
    condor_job_IDs=()
    
    # Get all steering files for process
    setup_command="--set-rescanfiles"
    if [ "$failed_only" = true ]; then
      # No need to set up scripts again if only failed rescans are to be re-run
      setup_command="--print-topdir"
    fi
    rescan_topdir=$( ${dir}/manage_rescan_files.sh ${setup_command} --process=${process} --e-Pol=${e_pol} --e+Pol=${p_pol} --input-config=${input_config} --output-config=${output_config} --tgc-config=${tgc_config} --tgc-points-file=${tgc_points_file})
    
    if [[ $rescan_topdir == "" ]]; then
      echo "No files found for process ${process} ${e_pol} ${p_pol}."
      continue  # If empty no steering file found -> next polarization
    else 
      echo "Found files for ${process} ${e_pol} ${p_pol}, send Marlin jobs to BIRD cluster."
    fi
    
    # Start jobs for each steering file
    cd ${condor_directory}
    
    # HTCondor log file directory (-> Make sure it exists)
    condor_output_subdir="${condor_output_dir}/${e_pol}${p_pol}"
    if [[ ! -d ${condor_output_subdir} ]] ; then # Create if not existing
      mkdir -p ${condor_output_subdir}
    fi
    
    # Loop over each subdir and rescan the corresponding event file
    for rescan_subdir in ${rescan_topdir}/*/; do
      if [ "$failed_only" = true ]; then
        # Requested that only previously failed rescans are rerun
        # -> Check if the directory contains a weight file, skip if it does
        if ls ${rescan_subdir}/*.weights.dat 1> /dev/null 2>&1; then
          continue
        fi
      fi 
      
      # The command to be executed: 
      # Load the needed software and start the rescan
      command_string="cd ${dir}/.. \&\& . load_env.sh \&\& cd ${rescan_subdir} \&\& whizard ${process}_rescan.sin \&\& cd ${dir}"
    
      # Submit job to HTCondor using standard submitting setup
      # -> Start Marlin job and keep track of job ID to know when it's done
      condor_job_output=$(condor_submit ${submit_script} log_dir=${condor_output_subdir} arguments="${command_string}")
    
      # Split output up by spaces and only read last part (which is cluster ID).
      # Details at: https://stackoverflow.com/questions/3162385/how-to-split-a-string-in-shell-and-get-the-last-field
      condor_job_IDs+="${condor_job_output##* } "
    
      # Wait a little to not overload the condor scheduler
      sleep 0.05s
    done
    cd ${dir}
    
    { # Use this scope for parallization of loop, don't include condor_submit in this to avoid spamming the local machine
    echo "Waiting for jobs of ${process} ${e_pol} ${p_pol} to finish."
    for job_ID in ${condor_job_IDs[@]}; do
      job_log_path=$(ls ${condor_output_subdir}/${job_ID}*.log)
    
      # Write into variable to suppress spammy output.
      # Timeout after 15 seconds to restart command, else it gets stuck sometimes.
      status=124 # Start with error code to get into loop
      while [ $status -eq 124 ]; do
        wait_output=$(timeout 15 condor_wait ${job_log_path}) 
        status=$? # Update status -> 124 means timeout, else success
      done
    done
    echo "Jobs of ${process} ${e_pol} ${p_pol} finished!"
    
    echo "Clean up whizard files that aren't needed."
    ${dir}/manage_process_files.sh --clean-up --process=${process} --e-Pol=${e_pol} --e+Pol=${p_pol} --input-config=${input_config} --output-config=${output_config}
    
    echo "Done with ${process} ${e_pol} ${p_pol}!"
    } &
  done
done
wait
echo "Done with process ${process}!"

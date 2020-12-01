#!/bin/bash

# ------------------------------------------------------------------------------
# Input parameters to be defined
process=false
input_config=false
output_config=false

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
  -h|--help)
    echo "usage: ./run_single_process.sh --process=[4f_WW_sl/4f_sW_sl/...] --input-config=[...] --output-config=[...]"
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

if [ "$process" = false ]; then
  >&2 echo "No final state given!"; exit 1
fi

if [ "$input_config" = false ]; then
  >&2 echo "No input config file given!"; exit 1
fi

if [ "$output_config" = false ]; then
  >&2 echo "No output config file given!"; exit 1
fi

# ------------------------------------------------------------------------------
# Script environment
dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )" # path of this macro

# Standard HTCondor environment
condor_directory=${dir}/../SubmitScripts
submit_script=${condor_directory}/submit_script.submit

# Condor logging output 
. ${output_config}
condor_output_dir=${output_base}/CondorOutput
if [[ ! -d ${condor_output_dir} ]] ; then # Create if not existing
  mkdir -p ${condor_output_dir}
fi

# ------------------------------------------------------------------------------
# Arrays with possible polarizations for looping
e_polarizations=("eL" "eR")
p_polarizations=("pL" "pR")

# ------------------------------------------------------------------------------
# Run each individual process / polarisation / process-file

echo "Start initalizing process ${process} running."

for e_pol in "${e_polarizations[@]}"; do
  for p_pol in "${p_polarizations[@]}"; do
    echo "Initializing polarization ${e_pol} ${p_pol}."
      
    # Array to collect condor job IDs so that I can keep track of if any are still running
    condor_job_IDs=()
    
    # Get all steering files for process, then loop to create job for each file
    steering_files=$( ${dir}/manage_process_files.sh --set-steeringfiles --process=${process} --e-Pol=${e_pol} --e+Pol=${p_pol} --input-config=${input_config} --output-config=${output_config} )
    
    if [[ $steering_files == "" ]]; then
      echo "No files found for process ${process} ${e_pol} ${p_pol}."
      continue  # If empty no steering file found -> next polarization
    else 
      echo "Found files for ${process} ${e_pol} ${p_pol}, send Marlin jobs to BIRD cluster."
    fi
    
    # Start jobs for each steering file
    cd ${condor_directory}
    
    for steering_file in ${steering_files[@]}; do
      # The command to be executed: 
      # Load the needed software and start the Marlin run
      command_string="cd ${dir}/.. \&\& . load_env.sh \&\& . add_processors.sh \&\& Marlin ${steering_file}"
      
      # Submit job to HTCondor using standard submitting setup
      # -> Start Marlin job and keep track of job ID to know when it's done
      condor_job_output=$(condor_submit ${submit_script} log_dir=${condor_output_dir} arguments="${command_string}")
      
      # Split output up by spaces and only read last part (which is cluster ID).
      # Details at: https://stackoverflow.com/questions/3162385/how-to-split-a-string-in-shell-and-get-the-last-field
      condor_job_IDs+="${condor_job_output##* } "
      
      # Wait a little to not overload the condor scheduler
      sleep 0.01s
    done
    cd ${dir}
    
    { # Use this scope for parallization of loop, don't include condor_submit in this to avoid spamming the local machine
    echo "Waiting for jobs of ${process} ${e_pol} ${p_pol} to finish."
    for job_ID in ${condor_job_IDs[@]}; do
      job_log_path=$(ls ${condor_output_dir}/${job_ID}*.log)
      
      # Write into variable to suppress spammy output.
      # Timeout after 15 seconds to restart command, else it gets stuck sometimes.
      status=124 # Start with error code to get into loop
      while [ $status -eq 124 ]; do
        wait_output=$(timeout 15 condor_wait ${job_log_path}) 
        status=$? # Update status -> 124 means timeout, else success
      done
    done
    echo "Jobs of ${process} ${e_pol} ${p_pol} finished!"
    
    echo "Combine individual files of ${process} ${e_pol} ${p_pol} and clean up temporary stuff."
    ${dir}/manage_process_files.sh --combine-output --process=${process} --e-Pol=${e_pol} --e+Pol=${p_pol} --input-config=${input_config} --output-config=${output_config}
    ${dir}/manage_process_files.sh --clean-up --process=${process} --e-Pol=${e_pol} --e+Pol=${p_pol} --input-config=${input_config} --output-config=${output_config}
    
    echo "Done with ${process} ${e_pol} ${p_pol}!"
    } &
  done
done
wait
echo "Done with process ${process}!"

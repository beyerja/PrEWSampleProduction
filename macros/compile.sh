#!/bin/bash

# -------------------------------------------------#
# Bash script for compiling the source code.
# To be run simply by using: ./compile.sh [--rebuild] [--jobs=n_jobs]
# Be sure a modern software is sourced! (E.g. sourcing load_env.sh)
# -------------------------------------------------#

# -------------------------------------------------#
# Check for input arguments to script

# Default parameters
REBUILD=false
N_JOBS=1

# Help message
USAGE="Usage: ./compile.sh [-h/--help/-H] [--rebuild] [--jobs=n_jobs]"

for i in "$@"
do
case $i in
  --jobs=*)
    N_JOBS="${i#*=}"
    echo "Main compilation will use ${N_JOBS} jobs."
    shift # past argument=value
  ;;
  --rebuild)
    REBUILD=true
    shift
  ;;
  -h|--help|-H)
    echo ""
    echo "Macro to compile the source code"
    echo "${USAGE}"
    echo ""
    echo "Arguments:"
    echo "  -h/--help/-H  : Help information (this)." 
    echo "  --rebuild     : Delete previous build folder for clean rebuild." 
    echo "  --jobs=n_jobs : Set a number of cores to use in compilation." 
    echo ""
    exit
  ;;
  *)
    # unknown option
    echo ""
    echo "Unknown argument: ${1}"
    echo "${USAGE}"
    echo ""
    exit
  ;;
esac
done

# -------------------------------------------------#
# Check if necessary directories are in place

dir="$( cd "$( dirname "${BASH_SOURCE[0]}"  )" && pwd  )"
home_folder=${dir}/..

if [ -d "${home_folder}"/build  ] ; then
	echo "Already have  --build-- directory to compile"
  # If requested remove build folder content
  if [ "${REBUILD}" = true ]; then 
    echo "Rebuild requested => Recreating build directory"
    rm -r "${home_folder}"/build
    mkdir "${home_folder}"/build
  fi
else
	echo "no build directory => Recreating build directory"
	mkdir "${home_folder}"/build
fi

# -------------------------------------------------#
# Move to build directory and to build framework
# (cmake + make)

cd "${home_folder}"/build

echo "begin to config"
echo
cmake -C $ILCSOFT/ILCSoft.cmake .. 
wait 
echo
echo "begin to make" 
make --jobs="${N_JOBS}"
wait
echo
echo "begin to make install" 
make install # >> make.output  2>&1
wait
echo 
echo "done!"
# -------------------------------------------------#

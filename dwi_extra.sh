#!/usr/bin/env bash
# 
# -*- coding: utf-8 -*-
# title           : dwi_extra.sh
# description     : [description]
# author          : Adebayo B. Braimah
# e-mail          : adebayo.braimah@cchmc.org
# date            : 2020 12 04 18:06:21
# version         : 0.0.x
# usage           : dwi_extra.sh [-h,--help]
# notes           : [notes]
# bash_version    : 4.3.48
#==============================================================================

#
# Define Usage & (Miscellaneous) Function(s)
#==============================================================================

Usage() {
  cat << USAGE

  Usage: $(basename $(realpath ${0})) --wm-fod <wmFOD.mif> --gm <GM.mif> --csf <CSF.mif> --out-vf <VF.mif>

Computes vf (vector field) file provided a white matter fiber orientation 
distrubution (wmFOD) file and its corresponding grey matter and CSF response
images. All input and output images are in MIF format (.mif/.mif.gz)

Required:

-wm,--wm-fod        Input wmFOD image file. 
-gm,--gm            Input gm response image file.
-csf,--csf          Input csf response image file.
-vf,--out-vf        Output vf file image.

----------------------------------------

-h,-help,--help     Prints usage and exits.

NOTE: 

  * All input and output images are in MIF format (.mif/.mif.gz)

----------------------------------------

Adebayo B. Braimah - 2020 12 04 18:06:21

----------------------------------------

  Usage: $(basename $(realpath ${0})) --wm-fod <wmFOD.mif> --gm <GM.mif> --csf <CSF.mif> --out-vf <VF.mif>

USAGE
  exit 1
}

#
# Define Logging Function(s)
#==============================================================================

# Echoes status updates to the command line
echo_color(){
  msg='\033[0;'"${@}"'\033[0m'
  # echo -e ${msg} >> ${stdOut} 2>> ${stdErr}
  echo -e ${msg} 
}
echo_red(){
  echo_color '31m'"${@}"
}
echo_green(){
  echo_color '32m'"${@}"
}
echo_blue(){
  echo_color '36m'"${@}"
}

exit_error(){
  echo_red "${@}"
  exit 1
}

# log function for completion
run()
{
  # log=${outDir}/LogFile.txt
  # err=${outDir}/ErrLog.txt
  echo "${@}"
  "${@}" >>${log} 2>>${err}
  if [ ! ${?} -eq 0 ]; then
    echo "failed: see log files ${log} ${err} for details"
    exit 1
  fi
  echo "-----------------------"
}

if [[ ${#} -lt 1 ]]; then
  Usage >&2
  exit 1
fi

#
# Parse Command Line Options
#==============================================================================

# Run time switches native to bash
scripts_dir=$(dirname $(realpath ${0}))

# Set defaults

# Parse options
while [[ ${#} -gt 0 ]]; do
  case "${1}" in
    -wm|--wm-fod) shift; wmfod=${1} ;;
    -gm|--gm) shift; gm=${1} ;;
    -csf|--csf) shift; csf=${1} ;;
    -vf|--out-vf) shift; out_vf=${1} ;;
    -h|-help|--help) Usage; ;;
    -*) echo_red "$(basename ${0}): Unrecognized option ${1}" >&2; Usage; ;;
    *) break ;;
  esac
  shift
done

#
# File checks
#==============================================================================

if [[ ! -f ${wmfod} ]] || [[ -z ${wmfod} ]]; then
  echo_red "Input Error: White matter FOD image file. Please check. Exiting..."
  exit 1
else
  wmfod=$(realpath ${wmfod})
fi

if [[ ! -f ${gm} ]] || [[ -z ${gm} ]]; then
  echo_red "Input Error: grey matter response image file. Please check. Exiting..."
  exit 1
else
  gm=$(realpath ${gm})
fi

if [[ ! -f ${csf} ]] || [[ -z ${csf} ]]; then
  echo_red "Input Error: CSF response image file. Please check. Exiting..."
  exit 1
else
  csf=$(realpath ${csf})
fi

if [[ -z ${out_vf} ]]; then
  echo_red "Error: Required - Output image name. Please check. Exiting..."
  exit 1
fi

#
# Compute Vector Field
#==============================================================================

mrconvert -coord 3 0 ${wmfod} - | mrcat ${csf} ${gm} - ${out_vf}


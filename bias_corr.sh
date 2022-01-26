#!/usr/bin/env bash
# -*- coding: utf-8 -*-


#######################################
# Prints usage to the command line interface.
# Arguments:
#   None
#######################################
Usage(){
  cat << USAGE
  Usage: 
      
      $(basename ${0}) <--options>
  
  Performs N4 bias field correction of a 3D MR image file.

  Required arguments
    -i, --input                       Input 3D image file.
    -o, --outdir                      Output directory.
  
  Optional arguments
    -h, -help, --help               Prints the help menu, then exits.
USAGE
  exit 1
}


#######################################
# N4 retrospective bias correction algorithm.
# Arguments:
#   Same arguments as N4BiasFieldCorrection.
# Returns
#   0 if no errors, non-zero on error.
#######################################
if ! hash realpath 2>/dev/null; then
  # realpath function substitute
  # if it does not exist.
  # NOTE: Requires FSL to be 
  # installed
  realpath () { fsl_abspath ${1} ; }
fi


#######################################
# N4 retrospective bias correction algorithm.
# Arguments:
#   Same arguments as N4BiasFieldCorrection.
# Returns
#   0 if no errors, non-zero on error.
#######################################
N4(){
  N4BiasFieldCorrection "${@}"
}

# Parse options
[[ ${#} -eq 0 ]] && Usage;
while [[ ${#} -gt 0 ]]; do
  case "${1}" in
    -i|--input) shift; input=${1} ;;
    -o|--outdir) shift; outdir=${1} ;;
    -h|-help|--help) Usage; ;;
    -*) echo_red "$(basename ${0}): Unrecognized option ${1}" >&2; Usage; ;;
    *) break ;;
  esac
  shift
done

tmp_dir=${outdir}/tmp_dir_${RANDOM}

if [[ ! -d ${tmp_dir} ]]; then
  mkdir -p ${tmp_dir}
fi

outdir=$(realpath ${outdir})
tmp_dir=$(realpath ${tmp_dir})
input=$(realpath ${input})

cd ${tmp_dir}

# Create mask
bet ${input} tmp -R -f 0.1 -m

N4 -i ${input} \
-x tmp_mask.nii.gz \
-o "[restore.nii.gz,bias.nii.gz]" \
-c "[50x50x50,0.001]" \
-s 2 \
-b "[100,3]" \
-t "[0.15,0.01,200]"

cp restore.nii.gz ${outdir}
cp bias.nii.gz ${outdir}

cd ${outdir}

rm -rf ${tmp_dir}

#!/usr/bin/env bash

# Export MRtrix path
scripts_dir=/mnt/c/Users/smart/Desktop/IRC317H_NAS/dti/data.dti

# add MRtrix to path
MRTRIX_PATH_BIN=${scripts_dir}/MRtrix3Tissue-3Tissue_v5.2.9/bin
export PATH=${PATH}:${MRTRIX_PATH_BIN}

file=../sub-C01/ses-001/dwi/bval-b2000_run-01/sub-C01_ses-001_bval-b2000_run-01_dwi

dwi=$(realpath ${file}.nii.gz)
bval=$(realpath ${file}.bval)
bvec=$(realpath ${file}.bvec)
json=$(realpath ${file}.json)

template=$(realpath ../UNC_AAL/infant-neo_1mm.nii)
template_brain=$(realpath ../UNC_AAL/infant-neo_1mm_brain.nii)
labels=$(realpath ../UNC_AAL/infant-neo-aal.nii)

out_dir=$(pwd)/sub-C01/bval-b2000

log=${out_dir}/sub-C01-bval-b2000.log

./xfm_tck.py \
-d ${dwi} \
-b ${bval} \
-e ${bvec} \
-j ${json} \
-t ${template} \
-tb ${template_brain} \
-l ${labels} \
-o ${out_dir} \
--log ${log} \
--FA --MD --AD --RD 

# Clear python cache
rm -rf __pycache__


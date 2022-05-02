
# Data
data=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.nii.gz
bval=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.bval
bvec=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.bvec
json=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/import/dwi.json
tensor=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_tensor.nii.gz

# mask=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/nodif_brain_mask.nii.gz
mask=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_FA.nii.gz

test_data=test_dtk/DTK_test/test_data
test_out=test_dtk/DTK_test/test.1

if [[ ! -d ${test_data} ]]; then
  mkdir -p ${test_data}
  mkdir -p ${test_out}

  files=( ${data} ${bval} ${bvec} ${json} )

  for file in ${files[@]}; do

    if [[ ${file} == *.nii.gz* ]]; then
      ext=nii.gz
    elif [[ ${file} == *.bval* ]]; then
      ext=bval
    elif [[ ${file} == *.bvec* ]]; then
      ext=bvec
    elif [[ ${file} == *.json* ]]; then
      ext=json
    fi

    cp ${file} ${test_data}/dwi.${ext}
  done

  # cp ${mask} ${test_data}/dwi_mask.nii.gz
  cp ${mask} ${test_data}/dwi_fa.nii.gz
  cp ${tensor} ${test_data}/dwi_tensor.nii.gz
fi

data=$(realpath ${test_data}/dwi.nii.gz)
bval=$(realpath ${test_data}/dwi.bval)
bvec=$(realpath ${test_data}/dwi.bvec)
json=$(realpath ${test_data}/dwi.json)
# mask=$(realpath ${test_data}/dwi_mask.nii.gz)
mask=$(realpath ${test_data}/dwi_fa.nii.gz)
tensor=$(realpath ${test_data}/dwi_tensor.nii.gz)

cd ${test_out}

# Reconstruction
dti_tracker \
$(remove_ext ${data}) \
file.trk \
-it nii.gz \
--fact \
--mask ${mask} 0 0.2


# TEST RECON - NO DTK PREPROC
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

if [[ ! -d ${test_out} ]]; then
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

# Tractography
dti_tracker \
$(remove_ext ${data}) \
file.trk \
-it nii.gz \
--fact \
--mask ${mask} 0 0.2

# DTK TEST - DTI_RECON DTK PREPROC
# Data
data=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.nii.gz
bval=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.bval
bvec=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.bvec
json=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/import/dwi.json
tensor=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_tensor.nii.gz

# mask=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/nodif_brain_mask.nii.gz
mask=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_FA.nii.gz

test_data=test_dtk/DTK_test/test_data
test_out=test_dtk/DTK_test/test.2

if [[ ! -d ${test_out} ]]; then
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

# Diffusion Reconstruction
dti_recon \
${data} \
data \
--output_type nii.gz \
--gradient_matrix /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/test_dtk/grad_table.txt # \
# -b 800 \
# --number_of_b0 4

# dti_recon \
# /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/import/dwi.nii.gz \
# dwi_recon \
# --output_type nii.gz \
# --gradient_matrix /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/test_dtk/grad_table.txt \
# -b 800 \
# --number_of_b0 4

# dti_tracker \
# dwi_recon \
# file.trk \
# -it nii.gz \
# --fact \
# --mask dwi_recon_fa.nii.gz 0 0.2

dti_tracker \
dwi_recon \
file.trk \
-it nii.gz \
--fact \
--mask /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/nodif_brain_mask.nii.gz 1 1 \
--mask2 /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_FA.nii.gz 0 0.2


# DTK TEST - ODF_RECON DTK PREPROC
# Data
data=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.nii.gz
bval=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.bval
bvec=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dwi.bvec
json=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/import/dwi.json
tensor=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_tensor.nii.gz

# mask=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/nodif_brain_mask.nii.gz
mask=/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_FA.nii.gz

test_data=test_dtk/DTK_test/test_data
test_out=test_dtk/DTK_test/test.3

if [[ ! -d ${test_out} ]]; then
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

hardi_mat \
/Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/test_dtk/grad_table.txt \
recon_mat.dat \
--order 4


# Diffusion Reconstruction
odf_recon \
$(remove_ext ${data}) \
32 \
181 \
dwi_recon \
--output_type nii.gz \
-b0 4 \
--matrix recon_mat.dat

odf_tracker \
dwi_recon \
file.trk \
--input_type nii.gz \
--mask /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/nodif_brain_mask.nii.gz 1 1 \
--mask2 /Users/adebayobraimah/Desktop/projects/xfm_tck/DTK_test/sub-130/run-01/preprocessed_data/dtifit/data_FA.nii.gz 0 0.2

spline_filter file.trk 0.5 file_spline.trk 


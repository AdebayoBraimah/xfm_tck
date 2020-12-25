# xfm_tck

Applies linear and non-linear transforms of atlas labels, and performs fiber tract reconstruction.

* External software dependencies:
  * `FSL` v6.0+
  * `MRtrix` v3+
    * Specifically this version found here: [SS3T-beta](https://3tissue.github.io/doc/ss3t-csd.html)

```
usage: xfm_tck.py [-h] -d <DWI.nii> -b <DWI.bval> -e <DWI.bvec> -t
                  <template.nii> -tb <template_brain.nii> -l <labels.nii> -o
                  </path/to/out_dir> [-j <DWI.json>] [--log <file.log>]
                  [--cwd] [--no-cleanup] [--force] [--gzip] [--vox VOX]
                  [--erode ERODE] [--fa-thresh FA_THRESH] [--dof DOF]
                  [--frac-int FRAC_INT] [--QIT] [--stream-lines STREAM_LINES]
                  [--cut-off CUTOFF] [--filter-tracks] [--term TERM]
                  [--symmetric] [--zero-diagonal] [--FA] [--MD] [--AD] [--RD]

Constructs a structural connectome given a diffusion weighted image file, and
an integer labeled atlas. NOTE: absolute paths must be passed as arguments.

optional arguments:
  -h, --help            show this help message and exit

Required arguments:
  -d <DWI.nii>, --dwi <DWI.nii>
                        Input preprocessed NIFTI-2 diffusion weighted image
                        file.
  -b <DWI.bval>, --bval <DWI.bval>
                        Corresponding FSL bval file.
  -e <DWI.bvec>, --bvec <DWI.bvec>
                        Corresponding FSL bvec file.
  -t <template.nii>, --template <template.nii>
                        Template NIFTI-2 file.
  -tb <template_brain.nii>, --template-brain <template_brain.nii>
                        Corresponding skull-stripped template.
  -l <labels.nii>, --labels <labels.nii>
                        Corresponding NIFTI-2 integer labeled atlas.
  -o </path/to/out_dir>, --out-dir </path/to/out_dir>
                        Output directory path.

Optional arguments:
  -j <DWI.json>, --json <DWI.json>
                        Corresponding JSON sidecar file.
  --log <file.log>      Log file output filename.
  --cwd                 Use current working directory as parent to working
                        directory [default: False].
  --no-cleanup          Do not remove temporary files [default: False].

Pipeline specific arguments:
  --force               Force overwrite of existing files [default: False].
  --gzip                Gzip processed files in the processing pipeline
                        [default: False].
  --vox VOX             Voxel size for DWI and corresponding files to be
                        upsampled to (in mm) [default: 1.5].
  --erode ERODE         Number of erosion passes for (whole brain) mask
                        [default: 0].
  --fa-thresh FA_THRESH
                        fa_thresh: FA threshold for crude WM vs GM-CSF
                        separation [default: 0.20].
  --dof DOF             Degrees of freedom for linear transforms. Valid
                        values: 6, 9, 12. [default: 12].
  --frac-int FRAC_INT   Fractional intensity threshold. Smaller values give
                        larger brain outline estimates. [default: 0.5].
  --QIT                 Rename output track (.tck) files so that they can be
                        opened in QIT [default: False].

Tractography specific arguments:
  --stream-lines STREAM_LINES
                        Maximum number of streamlines to generate for global
                        brain tractography [default: 1e5 | 100,000].
  --cut-off CUTOFF      FOD track termination threshold. [default: 0.07].
  --filter-tracks       Perform track filtering [default: False].
  --term TERM           Number of streamlines to remain after filtering.

Connectome specific arguments:
  --symmetric           Output symmetric structural connectivity matrices
                        [default: False].
  --zero-diagonal       Output structural connectivity matrices with zeroes
                        along the diagonal [default: False].
  --FA                  Output FA weighted structural connectome. [default:
                        False].
  --MD                  Output MD weighted structural connectome. [default:
                        False].
  --AD                  Output AD weighted structural connectome. [default:
                        False].
  --RD                  Output RD weighted structural connectome. [default:
                        False].
```

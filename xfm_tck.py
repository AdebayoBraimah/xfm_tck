#!/usr/bin/env python

'''Constructs a structural connectome given a DWI file, and an integer labeled atlas.

The classes and functions used here have dependencies found in MRtrix v3+ (SS3T-beta) and FSL v6+.

MRtrix (SS3T-beta): https://3tissue.github.io/doc/ss3t-csd.html
FSL: https://fsl.fmrib.ox.ac.uk/fsl/fslwiki

This program/script assumes that the input diffusion data has already undergone initial pre-processing.

TODO:
    * Write QC functions to generate QC images.
    * Add verbose options and statements.

Adebayo B. Braimah - 23 Dec. 2020
'''

# Import modules/packages
import os
import platform
import numpy as np
from shutil import copy, rmtree, which
from typing import List, Optional, Union, Tuple

# Import third-party modules/packages
from utils import File, Command, NiiFile, LogFile, TmpDir, DependencyError

# Import modules/packages for argument parsing
import argparse

# Main function
def main() -> None:
    '''Main function's responsiblies:
    * Checking system dependencies.
    * Checking required external software dependencies outside of python
    * Parses arguments
    '''
    # Check system
    if platform.system().lower() == 'windows':
        print("")
        FSLError("The required FSL dependencies cannot be installed on Windows platforms.")

    # Check for external dependencies
    if not which("flirt"):
        print("")
        FSLError("The required software (FSL) is not installed or on the system path.")

    if not which("ss3t_csd_beta1"):
        print("")
        MRtrixError("The required software (MRtrix, SS3T-beta) is not installed or on the system path.")

    parser = argparse.ArgumentParser(description="Constructs a structural connectome given a diffusion weighted image file, and an integer labeled atlas. NOTE: absolute paths must be passed as arguments.")

    # Parse Arguments
    # Required Arguments
    reqoptions = parser.add_argument_group('Required arguments')
    reqoptions.add_argument('-d', '--dwi',
                            type=str,
                            dest="dwi",
                            metavar="<DWI.nii.gz>",
                            required=True,
                            help="Input preprocessed NIFTI-2 diffusion weighted image file.")
    reqoptions.add_argument('-b', '--bval',
                            type=str,
                            dest="bval",
                            metavar="<DWI.bval>",
                            required=True,
                            help="Corresponding FSL bval file.")
    reqoptions.add_argument('-e', '--bvec',
                            type=str,
                            dest="bvec",
                            metavar="<DWI.bvec>",
                            required=True,
                            help="Corresponding FSL bvec file.")
    reqoptions.add_argument('-t', '--template',
                            type=str,
                            dest="template",
                            metavar="<template.nii>",
                            required=True,
                            help="Template NIFTI-2 file.")
    reqoptions.add_argument('-tb', '--template-brain',
                            type=str,
                            dest="template_brain",
                            metavar="<template_brain.nii>",
                            required=True,
                            help="Corresponding skull-stripped template.")
    reqoptions.add_argument('-l', '--labels',
                            type=str,
                            dest="labels",
                            metavar="<labels.nii>",
                            required=True,
                            help="Corresponding NIFTI-2 integer labeled atlas.")
    reqoptions.add_argument('-o', '--out-dir',
                            type=str,
                            dest="out_dir",
                            metavar="</path/to/out_dir>",
                            required=True,
                            help="Output directory path.")

     # Optional Arguments
    optoptions = parser.add_argument_group('Optional arguments')
    optoptions.add_argument('-j', '--json',
                            type=str,
                            dest="json",
                            metavar="<DWI.json>",
                            default=None,
                            required=False,
                            help="Corresponding JSON sidecar file.")
    optoptions.add_argument('--log',
                            type=str,
                            dest="log",
                            metavar="<file.log>",
                            default="file.log",
                            required=False,
                            help="Log file output filename.")
    # optoptions.add_argument('-w', '--work-dir',
    #                         type=str,
    #                         dest="work_dir",
    #                         metavar="</path/to/work_dir>",
    #                         default=None,
    #                         required=False,
    #                         help="Working directory path [default: 'work.tmp' directory in current working directory].")
    optoptions.add_argument('--cwd',
                            action="store_true",
                            dest="cwd",
                            default=False,
                            required=False,
                            help="Use current working directory as parent to working directory [default: False].")
    optoptions.add_argument('--no-cleanup',
                            action="store_false",
                            dest="no_cleanup",
                            default=False,
                            required=False,
                            help="Do not remove temporary files [default: False].")
    
    # Pipeline specific arguments
    pipeoptions = parser.add_argument_group('Pipeline specific arguments')
    pipeoptions.add_argument('--force',
                            action="store_true",
                            dest="force",
                            default=False,
                            required=False,
                            help="Force overwrite of existing files [default: False].")
    pipeoptions.add_argument('--gzip',
                            action="store_true",
                            dest="gzip",
                            default=False,
                            required=False,
                            help="Gzip processed files in the processing pipeline [default: False].")
    pipeoptions.add_argument('--vox',
                            type=float,
                            dest="vox",
                            default=1.5,
                            required=False,
                            help="Voxel size for DWI and corresponding files to be upsampled to (in mm) [default: 1.5].")
    pipeoptions.add_argument('--erode',
                            type=int,
                            dest="erode",
                            default=0,
                            required=False,
                            help="Number of erosion passes for (whole brain) mask [default: 0].")
    pipeoptions.add_argument('--fa-thresh',
                            type=float,
                            dest="fa_thresh",
                            default=0.20,
                            required=False,
                            help="fa_thresh: FA threshold for crude WM vs GM-CSF separation [default: 0.20].")
    pipeoptions.add_argument('--dof',
                            type=int,
                            dest="dof",
                            default=12,
                            required=False,
                            help="Degrees of freedom for linear transforms. Valid values: 6, 9, 12. [default: 12].")
    pipeoptions.add_argument('--frac-int',
                            type=float,
                            dest="frac_int",
                            default=0.5,
                            required=False,
                            help="Fractional intensity threshold. Smaller values give larger brain outline estimates. [default: 0.5].")

    # Tractography specific arguments
    tractoptions = parser.add_argument_group('Tractography specific arguments')
    tractoptions.add_argument('--stream-lines',
                            type=int,
                            dest="stream_lines",
                            default=1e5,
                            required=False,
                            help="Maximum number of streamlines to generate for global brain tractography [default: 1e5 | 100,000].")
    tractoptions.add_argument('--cut-off',
                            type=float,
                            dest="cutoff",
                            default=0.07,
                            required=False,
                            help="FOD track termination threshold. [default: 0.07].")
    tractoptions.add_argument('--filter-tracks',
                            
                            action="store_true",
                            dest="filter_tracts",
                            default=False,
                            required=False,
                            help="Perform track filtering [default: False].")
    tractoptions.add_argument('--term',
                            type=int,
                            dest="term",
                            default=None,
                            required=False,
                            help="Number of streamlines to remain after filtering.")

    # Connectome specific arguments
    conoptions = parser.add_argument_group('Connectome specific arguments')
    conoptions.add_argument('--symmetric',
                            action="store_true",
                            dest="symmetric",
                            default=False,
                            required=False,
                            help="Output symmetric structural connectivity matrices [default: False].")
    conoptions.add_argument('--zero-diagonal',
                            action="store_true",
                            dest="zero_diagonal",
                            default=False,
                            required=False,
                            help="Output structural connectivity matrices with zeroes along the diagonal [default: False].")
    conoptions.add_argument('--FA',
                            action="store_true",
                            dest="fa",
                            default=False,
                            required=False,
                            help="Output FA weighted structural connectome.  [default: False].")
    conoptions.add_argument('--MD',
                            action="store_true",
                            dest="md",
                            default=False,
                            required=False,
                            help="Output MD weighted structural connectome.  [default: False].")
    conoptions.add_argument('--AD',
                            action="store_true",
                            dest="ad",
                            default=False,
                            required=False,
                            help="Output AD weighted structural connectome.  [default: False].")
    conoptions.add_argument('--RD',
                            action="store_true",
                            dest="rd",
                            default=False,
                            required=False,
                            help="Output RD weighted structural connectome.  [default: False].")

    args = parser.parse_args()

    # Print help message in the case
    # of no arguments
    try:
        args = parser.parse_args()
    except SystemExit as err:
        if err.code == 2:
            parser.print_help()

    # Clean-up check
    if args.no_cleanup:
        cleanup = False
    else:
        cleanup = True

    # Create output directory
    if os.path.exists(args.out_dir):
        pass
    else:
        os.makedirs(args.out_dir)

    # Construct working directory path
    work_tmp_dir = os.path.join(args.out_dir,"work.tmp")

    os.chdir(args.out_dir)

    [connectome, \
    fa_connectome, \
    md_connectome, \
    ad_connectome, \
    rd_connectome, \
    labels_native, \
    head,
    work_tmp] = create_structural_connectome(dwi=args.dwi,
                                             bval=args.bval,
                                             bvec=args.bvec,
                                             template=args.template,
                                             template_brain=args.template_brain,
                                             labels=args.labels,
                                             json=args.json,
                                             log=args.log,
                                             work_dir=work_tmp_dir,
                                             use_cwd=args.cwd,
                                             force=args.force,
                                             gzip=args.gzip,
                                             erode=args.erode,
                                             fa_thresh=args.fa_thresh,
                                             vox=args.vox,
                                             dof=args.dof,
                                             frac_int=args.frac_int,
                                             stream_lines=args.stream_lines,
                                             cutoff=args.cutoff,
                                             filter_tracts=args.filter_tracts,
                                             term=args.term,
                                             symmetric=args.symmetric,
                                             zero_diagonal=args.zero_diagonal,
                                             fa=args.fa,
                                             md=args.md,
                                             ad=args.ad,
                                             rd=args.rd,
                                             cleanup=cleanup)

    # Copy files to output directories
    out_con = os.path.join(args.out_dir, os.path.basename(connectome.file))
    out_labels = os.path.join(args.out_dir, os.path.basename(labels_native.file))
    out_head = os.path.join(args.out_dir, os.path.basename(head.file))
    
    copy(connectome.file,out_con)
    copy(labels_native.file,out_labels)
    copy(head.file,out_head)

    if os.path.exists(fa_connectome.file):
        out_con_fa = os.path.join(args.out_dir, os.path.basename(fa_connectome.file))
        copy(fa_connectome.file,out_con_fa)

    if os.path.exists(md_connectome.file):
        out_con_md = os.path.join(args.out_dir, os.path.basename(md_connectome.file))
        copy(md_connectome.file,out_con_md)

    if os.path.exists(ad_connectome.file):
        out_con_ad = os.path.join(args.out_dir, os.path.basename(ad_connectome.file))
        copy(ad_connectome.file,out_con_ad)

    if os.path.exists(rd_connectome.file):
        out_con_rd = os.path.join(args.out_dir, os.path.basename(rd_connectome.file))
        copy(rd_connectome.file,out_con_rd)

    if cleanup:
        work_tmp.rm_tmp_dir(rm_parent=True)

    return None

# Scripts directory
scripts_dir = os.path.dirname(os.path.realpath(__file__))

# Class exceptions
class MRtrixError(Exception):
    pass

class FSLError(Exception):
    pass

# Classes
class ReconMRtrix (object):
    '''Class that contains the associated wrapper functions for performing
    tractography using MRtrix v3.x.
    
    Attributes:
        nii_file: Input NIFTI-2 DWI file.
        bval: Corresponding FSL bval file.
        bvec: Corresponding FSL bvec file.
        json_file: Corresponding JSON (sidecar) file.
        log: Log file name
    
    To-do:
        * Write general purpose mif to nifti and (nifti to mif) conversion function(s).
        * Investigate ACT (anatomically constrained tractography) in neonates.
    '''
    
    nii_file: NiiFile = ""
    bval: File = ""
    bvec: File = ""
    json_file: File = ""
    log: LogFile = ""
    
    def __init__(self,
                 nii_file: str,
                 bval: str,
                 bvec: str,
                 json_file: Optional[str] = None,
                 log: Optional[str] = None
                ) -> None:
        '''Init doc string for ReconMRtrix class.
        
        Usage example:
            >>> dwi_obj = ReconMRtrix("file.nii",
            >>>                       "file.bval",
            >>>                       "file.bvec",
            >>>                       "file.json",
            >>>                       "file.log")
            >>> dwi_obj.nii_file
            "file.nii"
        
        Args:
            nii_file: Input file path to DWI NIFTI file.
            bval: Input file path to corresponding bval file.
            bvec: Input file path to corresponding bvec file.
            json_file: Input file path to corresponding JSON (sidecar) file.
            log: Log filename for output log file (, need not exist at runtime).
        '''
        self.nii_file: str = nii_file
        self.bval: str = bval
        self.bvec: str = bvec
        
        self.nii_file = NiiFile(self.nii_file)
        self.bval = File(self.bval)
        self.bvec = File(self.bvec)
        
        if json_file:
            self.json_file: str = json_file
            self.json_file = File(self.json_file)
        else:
            self.json_file = ""
            self.json_file = File(self.json_file)
            
        if log:
            self.log: str = log
            self.log = LogFile(self.log)
        else:
            self.log: str = ""
            self.log = LogFile(self.log)
        
    class Mif(File):
        '''Creates MIF files for use with MRtrix executables. Inherits 
        methods and properties from the File class.
        
        Attributes:
            * 
        '''
        
        def __init__(self,
                     file: File,
                     gzip: bool = False
                    ) -> None:
            '''Init doc string for Mif class. Inherits methods and properties
            from the File class. The MIF file can also be gzipped if desired.
            
            Usage example:
                >>> dwi_obj = ReconMRtrix("file.nii",
                >>>                       "file.bval",
                >>>                       "file.bvec",
                >>>                       "file.json",
                >>>                       "file.log")
                >>> dwi_obj.Mif(dwi_obj.nii_file)
                >>> dwi_obj.Mif.file
                >>> 'file.mif'
                >>>
                >>> # To gzip the MIF file
                >>> dwi_obj.Mif(dwi_obj.nii_file,gzip=True)
            
            Args:
                file: Input filename of MIF file (need not exist).
                gzip: Gzips output MIF file
            '''
            self.file = file
            
            if '.gz' in self.file:
                if gzip:
                    self.ext: str = self.file[-(7):]
                    self.file = self.file[:-(7)] + ".mif.gz"
                else:
                    self.ext: str = self.file[-(7):]
                    self.file = self.file[:-(7)] + ".mif"
            else:
                if gzip:
                    self.ext: str = self.file[-(4):]
                    self.file = self.file[:-(4)] + ".mif.gz"
                else:
                    self.ext: str = self.file[-(4):]
                    self.file = self.file[:-(4)] + ".mif"
            File.__init__(self,self.file,self.ext)
    
    def nifti_to_mif(self,
                     force: bool = False,
                     gzip: bool = False
                    ) -> Mif:
        '''Converts DWI NIFTI file and its associated files to MIF files.
        
        Usage example:
            >>> dwi_obj = ReconMRtrix("file.nii",
            >>>                       "file.bval",
            >>>                       "file.bvec",
            >>>                       "file.json",
            >>>                       "file.log")
            >>> dwi_mif = dwi_obj.nifti_to_mif()
            >>> dwi_mif.file
            'file.mif'
        
        Args:
            force: Force overwrite of existing MIF file.
            gzip: Gzip output MIF file.
        
        Returns:
            mif_file: Mif file object.
        '''
        mif_file: str = self.nii_file.abs_path()
        mif_file: Mif = self.Mif(mif_file,gzip=gzip)
        
        mr_convert = Command("mrconvert")
        if force:
            mr_convert.cmd_list.append("-force")
        if self.json_file:
            mr_convert.cmd_list.append("-json_import")
            mr_convert.cmd_list.append(self.json_file.file)
        mr_convert.cmd_list.append("-fslgrad")
        mr_convert.cmd_list.append(f"{self.bvec.file}")
        mr_convert.cmd_list.append(f"{self.bval.file}")
        mr_convert.cmd_list.append(f"{self.nii_file.file}")
        mr_convert.cmd_list.append(f"{mif_file.file}")
        
        mr_convert.run(self.log)
        return mif_file
    
    def estimate_response(self,
                          mif: Mif,
                          method: str = "dhollander",
                          erode: int = 0,
                          fa_thresh: float = 0.2,
                          force: bool = False,
                          gzip: bool = False
                         ) -> Tuple[File,File,File]:
        '''Performs response function estimation provided a diffusion weighted
        image file, and the algorithm/method to use.

        Usage example:
            >>> dwi_obj = ReconMRtrix("file.nii",
            >>>                       "file.bval",
            >>>                       "file.bvec",
            >>>                       "file.json",
            >>>                       "file.log")
            >>> dwi_mif = dwi_obj.nifti_to_mif()
            >>>
            >>> [wm, gm, csf] = dwi_obj.estimate_response(mif=dwi_mif)

        Args:
            mif: Input DWI MIF file object.
            method: Algorithm/method to estimate the response function.
                Only the 'dhollander' algorithm/method is supported.
            erode: Number of erosion passes for (whole brain) mask.
            fa_thresh: FA threshold for crude WM vs GM-CSF separation.
            force: Force overwrite of existing MIF file.
            gzip: Gzip output MIF file
        
        Returns:
            wm_res: WM response function.
            gm_res: GM response function.
            csf_res: CSF response function.
        '''
        [path, filename, ext] = self.nii_file.file_parts()
        
        wm_res: str = os.path.join(path,filename + "_response_wm.txt")
        gm_res: str = os.path.join(path,filename + "_response_gm.txt")
        csf_res: str = os.path.join(path,filename + "_response_csf.txt")
            
        wm_res: File = File(wm_res)
        gm_res: File = File(gm_res)
        csf_res: File = File(csf_res)
        
        dwi_response = Command("dwi2response")
        if force:
            dwi_response.cmd_list.append("-force")
        dwi_response.cmd_list.append(method)
        dwi_response.cmd_list.append(mif.file)
        dwi_response.cmd_list.append(wm_res.file)
        dwi_response.cmd_list.append(gm_res.file)
        dwi_response.cmd_list.append(csf_res.file)
        
        dwi_response.run(self.log)
        
        return wm_res, gm_res, csf_res
    
    def mr_upsample(self,
                    mif: Mif,
                    vox: float,
                    interp: Optional[str] = "cubic",
                    gzip: bool = False
                   ) -> Mif:
        '''Upsamples a NIFTI-2 or MIF image file by some arbitrary voxel size.

        Usage example:
            >>> dwi_obj = ReconMRtrix("file.nii",
            >>>                       "file.bval",
            >>>                       "file.bvec",
            >>>                       "file.json",
            >>>                       "file.log")
            >>> dwi_mif = dwi_obj.nifti_to_mif()
            >>>
            >>> new_mif = dwi_obj.mr_upsample(mif=dwi_mif,
            >>>                               vox=1.5,
            >>>                               interp = "nearest")

        Args:
            mif: Input MIF file object.
            vox: Desired output voxel size (in mm).
            interp: Interpolation method to use.
            gzip: Gzip output file.

        Returns:
            upsampled_mif: Upsampled image MIF file object.
        '''
        # [path, filename, _ext] = self.nii_file.file_parts()
        # [_path, _filename, ext] = mif.file_parts() # Keep original file extension
        
        if ".mif" in mif.file:
            if ".gz" in mif.file:
                gzip = True
                _ext = ".mif.gz"
            else:
                _ext = ".mif"
        elif ".nii" in mif.file:
            if ".gz" in mif.file:
                gzip = True
                _ext = ".nii.gz"
            else:
                _ext = ".nii"
            
        # if gzip:
        #     ext = ".mif.gz"
        # else:
        #     ext = ".mif"
        ext = ".mif"
        
        
        [path, filename, _ext] = mif.file_parts(ext=_ext) # Keep original file extension
        
        filename = filename + f"_upsampled"
        upsampled_mif = os.path.join(path,filename + ext)
        upsampled_mif: Mif = self.Mif(upsampled_mif,gzip=gzip)
        
        try:
            upsample = Command("mrresize")
            upsample.check_dependency()
            upsample.cmd_list.append(mif.file)
            upsample.cmd_list.append("-vox")
            upsample.cmd_list.append(f"{vox}")
            upsample.cmd_list.append(upsampled_mif.file)
            if interp:
                upsample.cmd_list.append("-interp")
                upsample.cmd_list.append(interp)
            upsample.run(self.log)
            return upsampled_mif
        except DependencyError:
            upsample = Command("mrgrid")
            upsample.check_dependency()
            upsample.cmd_list.append(mif.file)
            upsample.cmd_list.append("regrid")
            upsample.cmd_list.append(upsampled_mif.file)
            upsample.cmd_list.append("-voxel")
            upsample.cmd_list.append(f"{vox}")
            if interp:
                upsample.cmd_list.append("-interp")
                upsample.cmd_list.append(interp)
            upsample.run(self.log)
            return upsampled_mif
    
    def create_mask(self,
                    mif: Mif,
                    frac_int: float = 0.5,
                    gzip: bool = False,
                    cleanup: bool = True
                   ) -> Tuple[Mif,Mif,Mif]:
        '''Creates an image file mask for an input DWI MIF file.

        Usage example:
            >>> dwi_obj = ReconMRtrix("file.nii",
            >>>                       "file.bval",
            >>>                       "file.bvec",
            >>>                       "file.json",
            >>>                       "file.log")
            >>> dwi_mif = dwi_obj.nifti_to_mif()
            >>>
            >>> [mask_mif,brain_mif,head_mif] = dwi_obj.create_mask(mif=dwi_mif,
            >>>                                                     frac_int=0.5)

        Args:
            mif: Input DWI MIF file object.
            frac_int: Fractional intensity threshold. Smaller values give larger brain outline estimates.
            gzip: Gzip output file.
            cleanup: Perform cleanup.

        Returns:
            mask_mif: Binary mask image MIF file object.
            brain_mif: Brain iamge MIF file object.
            head_mif: Whole head image MIF file object.
        '''
        [path, _filename, _ext] = self.nii_file.file_parts()
        [_path, filename, ext] = mif.file_parts() # Keep original file extension
        
        if ".gz" in mif.file:
            gzip = True
        
        file_head = filename + "_head"
        filename = filename + "_brain"
        file_mask = filename + "_mask"
        
        brain_mif = os.path.join(path,filename + ext)
        mask_mif = os.path.join(path,file_mask + ext)
        head_mif = os.path.join(path,file_head + ext)
        
        brain_mif = self.Mif(brain_mif,gzip=gzip)
        mask_mif: Mif = self.Mif(mask_mif,gzip=gzip)
        head_mif: Mif = self.Mif(head_mif,gzip=gzip)
            
        # Create temporary directory
        work_dir: TmpDir = TmpDir(tmp_dir=path,use_cwd=False)
        work_dir.mk_tmp_dir()
        
        tmp_b0s: TmpFile = work_dir.TmpFile(tmp_file="tmp_B0s" + _ext,
                                            tmp_dir=work_dir.tmp_dir)
        
        tmp_b0: TmpFile = work_dir.TmpFile(tmp_file="tmp_B0" + _ext,
                                           tmp_dir=work_dir.tmp_dir)
        
        tmp_mask: TmpFile = work_dir.TmpFile(tmp_file=tmp_b0.rm_ext(ext=_ext) + 
                                             "_brain" + _ext,
                                             tmp_dir=work_dir.tmp_dir)
        
        # Extract B0s
        extract_b0s = Command("dwiextract")
        extract_b0s.cmd_list.append("-bzero")
        extract_b0s.cmd_list.append(mif.file)
        extract_b0s.cmd_list.append(tmp_b0s.file)
        extract_b0s.run(self.log)
        
        # Merge B0s, by obtaining mean of images
        merge_b0s = Command("fslmaths")
        merge_b0s.cmd_list.append(tmp_b0s.file)
        merge_b0s.cmd_list.append("-Tmean")
        merge_b0s.cmd_list.append(tmp_b0.file)
        merge_b0s.run(self.log)
        
        # Create brain mask
        bet = Command("bet")
        bet.cmd_list.append(tmp_b0.file)
        bet.cmd_list.append(tmp_mask.file)
        bet.cmd_list.append("-R")
        bet.cmd_list.append("-m")
        bet.cmd_list.append("-f")
        bet.cmd_list.append(f"{frac_int}")
        bet.run(self.log)
        
        # Convert NIFTI to MIF
        mr_convert = Command("mrconvert")
        mr_convert.cmd_list.append(tmp_mask.rm_ext(ext=_ext) + "_mask.nii.gz")
        mr_convert.cmd_list.append(mask_mif.file)
        mr_convert.run(self.log)
        
        mr_convert = Command("mrconvert")
        mr_convert.cmd_list.append(tmp_mask.file)
        mr_convert.cmd_list.append(brain_mif.file)
        mr_convert.run(self.log)
        
        mr_convert = Command("mrconvert")
        mr_convert.cmd_list.append(tmp_b0.file)
        mr_convert.cmd_list.append(head_mif.file)
        mr_convert.run(self.log)
        
        # Clean-up
        if cleanup:
            work_dir.rm_tmp_dir(rm_parent=False)
        
        return mask_mif,brain_mif,head_mif
        
    def ss3t_csd(self,
                 mif: Mif,
                 mask: Mif,
                 wm_res: File,
                 gm_res: File,
                 csf_res: File,
                 gzip: bool = False) -> Tuple[Mif,Mif,Mif]:
        '''Computes the CSD (constrained spherical deconvolution) of 3 tissues types 
        from the corresponding input response functions using single-shelled MR diffusion
        data.

        NOTE:  This function takes quite some time to run.
        
        See this link for further details: 
            https://3tissue.github.io/doc/ss3t-csd.html

        Usage example:
            >>> dwi_obj = ReconMRtrix("file.nii",
            >>>                       "file.bval",
            >>>                       "file.bvec",
            >>>                       "file.json",
            >>>                       "file.log")
            >>> dwi_mif = dwi_obj.nifti_to_mif()
            >>>
            >>> [wm, gm, csf] = dwi_obj.estimate_response(mif=dwi_mif)
            >>>
            >>> [mask_mif] = dwi_obj.create_mask(mif=dwi_mif,
            >>>                                  frac_int=0.5)
            >>>
            >>> [wm_fod, gm_tis, csf_tis] = dwi_obj.ss3t_csd(mif=dwi_mif,
            >>>                                              mask=mask,
            >>>                                              wm_res=wm,
            >>>                                              gm_res=gm,
            >>>                                              csf_res=csf)

        Args:
            mif: Input DWI MIF file object
            mask: Corresponding mask MIF file object
            wm_res: WM response function.
            gm_res: GM response function.
            csf_res: CSF response function.
            gzip: Gzip output file.

        Returns:
            wm_fod: WM FOD (fiber orientation-distrubtion) MIF file object.
            gm_tis: GM tissue MIF file object.
            csf_tis: CSF tissue MIF file object.
        '''
        [path, _filename, _ext] = self.nii_file.file_parts()
        [_path, filename, ext] = mif.file_parts() # Keep original file extension
        
        if ".gz" in mif.file:
            gzip = True
        
        wm_fod = filename + "_wm_fod"
        gm_tis = filename + "_gm_tis"
        csf_tis = filename + "_csf_tis"
        
        wm_fod: str = os.path.join(path,wm_fod + ext)
        gm_tis: str = os.path.join(path,gm_tis + ext)
        csf_tis: str = os.path.join(path,csf_tis + ext)
        
        wm_fod: Mif = self.Mif(wm_fod,gzip=gzip)
        gm_tis: Mif = self.Mif(gm_tis,gzip=gzip)
        csf_tis: Mif = self.Mif(csf_tis,gzip=gzip)
        
        # Compute WM FOD
        ss3t = Command("ss3t_csd_beta1")
        ss3t.cmd_list.append(mif.file)
        ss3t.cmd_list.append(wm_res.file)
        ss3t.cmd_list.append(wm_fod.file)
        ss3t.cmd_list.append(gm_res.file)
        ss3t.cmd_list.append(gm_tis.file)
        ss3t.cmd_list.append(csf_res.file)
        ss3t.cmd_list.append(csf_tis.file)
        ss3t.cmd_list.append("-mask")
        ss3t.cmd_list.append(mask.file)
        ss3t.run(self.log)
        return wm_fod, gm_tis, csf_tis
    
    def bias_field_correction(self,
                              wm_fod: Mif,
                              gm_tis: Mif,
                              csf_tis: Mif,
                              mask: Mif, 
                              gzip: bool = False
                             ) -> Tuple[Mif,Mif,Mif]:
        '''Performs joint bias-field correction of the WM FOD, and the GM and CSF
        tissue files.

        Args:
            wm_fod: WM FOD (fiber orientation-distrubtion) MIF file object.
            gm_tis: GM tissue MIF file object.
            csf_tis: CSF tissue MIF file object.
            mask: Corresponding mask MIF file object.
            gzip: Gzip output file.

        Returns:
            wm_fod_norm: Bias corrected WM FOD MIF file object.
            gm_tis_norm: Bias corrected GM tissue file MIF file object.
            csf_tis_norm: Bias corrected CSF tissue file MIF file object.
        '''
        [path, filename, _ext] = self.nii_file.file_parts()
        
        if ".gz" in wm_fod.file:
            gzip = True
            ext = ".mif.gz"
        else:
            ext = ".mif"
        
        wm_fod_norm = filename + "_wm_fod_norm"
        gm_tis_norm = filename + "_gm_tis_norm"
        csf_tis_norm = filename + "_csf_tis_norm"
        
        wm_fod_norm: str = os.path.join(path,wm_fod_norm + ext)
        gm_tis_norm: str = os.path.join(path,gm_tis_norm + ext)
        csf_tis_norm: str = os.path.join(path,csf_tis_norm + ext)
        
        wm_fod_norm: Mif = self.Mif(wm_fod_norm,gzip=gzip)
        gm_tis_norm: Mif = self.Mif(gm_tis_norm,gzip=gzip)
        csf_tis_norm: Mif = self.Mif(csf_tis_norm,gzip=gzip)
            
        # Perform joint bias field correction
        bias_correct = Command("mtnormalise")
        bias_correct.cmd_list.append(wm_fod.file)
        bias_correct.cmd_list.append(wm_fod_norm.file)
        bias_correct.cmd_list.append(gm_tis.file)
        bias_correct.cmd_list.append(gm_tis_norm.file)
        bias_correct.cmd_list.append(csf_tis.file)
        bias_correct.cmd_list.append(csf_tis_norm.file)
        bias_correct.cmd_list.append("-mask")
        bias_correct.cmd_list.append(mask.file)
        bias_correct.run(self.log)
        return wm_fod_norm, gm_tis_norm, csf_tis_norm
    
    def compute_dec_map(self,
                        wm_fod: Mif,
                        gm_tis: Mif,
                        csf_tis: Mif,
                        mask: Mif,
                        gzip: bool = False) -> Tuple[Mif,Mif]:
        '''Computes DEC (directionally-encoded color) and VF (vector field) maps.

        NOTE: This is a wrapper function for the shell script `dwi_extra.sh`.

        Args:
            wm_fod: WM FOD MIF file object.
            gm_tis: GM tissue MIF file object.
            csf_tis: CSF tissue MIF file object.
            mask: Corresponding mask image MIF file object.
            gzip: Gzip output file.

        Returns:
            dec: DEC map MIF file object
            vf: VF map MIF file object.
        '''
        [path, filename, _ext] = self.nii_file.file_parts()
        
        if ".gz" in wm_fod.file:
            gzip = True
            ext = ".mif.gz"
        else:
            ext = ".mif"
        
        # Create output filenames
        dec = os.path.join(path,filename + "_dec" + ext)
        dec: Mif = self.Mif(dec,gzip=gzip)
        
        vf = os.path.join(path,filename + "_vf" + ext)
        vf: Mif = self.Mif(vf,gzip=gzip)
            
        # Compute DEC map
        fod2dec = Command("fod2dec")
        fod2dec.cmd_list.append(wm_fod.file)
        fod2dec.cmd_list.append(dec.file)
        fod2dec.cmd_list.append("-mask")
        fod2dec.cmd_list.append(mask.file)
        fod2dec.run(self.log)
        
        # Compute RGB tissue (signal contribution) maps
        vf_calc = os.path.join(scripts_dir,"dwi_extra.sh")
        rgb = Command(vf_calc)
        rgb.cmd_list.append("--wm-fod")
        rgb.cmd_list.append(wm_fod.file)
        rgb.cmd_list.append("--gm")
        rgb.cmd_list.append(gm_tis.file)
        rgb.cmd_list.append("--csf")
        rgb.cmd_list.append(csf_tis.file)
        rgb.cmd_list.append("--out-vf")
        rgb.cmd_list.append(vf.file)
        rgb.run(self.log)
        
        return dec, vf
    
    def mr_tck_global(self,
                      wm_fod: Mif,
                      mask: Mif,
                      stream_lines: int = 100000, 
                      cutoff: float = 0.07) -> File:
        '''Performs global tractography (in the case of a whole brain mask) or tractography of 
        select regions (in the case of a binary mask that contains regions of interest) via `tckgen` in
        MRtrix.

        Args:
            wm_fod: WM FOD MIF file object.
            mask: Corresponding mask MIF file object.
            stream_lines: Number of streamlines to generate for the tck file.
            cutoff: FOD track termination threshold.

        Returns:
            tck: Track (tck) file object.
        '''
        [path, filename, _ext] = self.nii_file.file_parts()
        
        # Create output filenames
        tck: str = os.path.join(path,filename + f".{int(stream_lines)}.streamlines" + ".tck")
        tck: File = File(tck)
        
        # Construct tracts
        tckgen = Command("tckgen")
        tckgen.cmd_list.append(wm_fod.file)
        tckgen.cmd_list.append(tck.file)
        tckgen.cmd_list.append("-seed_image")
        tckgen.cmd_list.append(mask.file)
        tckgen.cmd_list.append("-select")
        tckgen.cmd_list.append(f"{stream_lines}")
        tckgen.cmd_list.append("-cutoff")
        tckgen.cmd_list.append(f"{cutoff}")
        tckgen.run(self.log)
        
        return tck
    
    def mr_tck_sift(self,
                   tck: File,
                   wm_fod: Mif,
                   term: Optional[int] = None,
                   mask: Mif = "") -> File:
        '''Performs track filtering of some input tck file (object) using
        SIFT (spherical-deconvolution informed filtering of tractograms) in
        MRtrix v3.x.

        Args:
            tck: Input tck file object.
            wm_fod: Input WM FOD MIF file object.
            term: optoptions.add_argument('--force',
                            type=bool,
                            action="store_true",
                            dest="force",
                            default=False,
                            required=False,
                            help="Force overwrite of existing files [default: False].")
            mask: Corresponding input mask image MIF file object.

        Returns:
            tck_filt: Filtered output tck file object.
        '''
        [path, filename, _ext] = self.nii_file.file_parts()
        
        # Create output filenames
        if term:
            tck_filt: str = os.path.join(path,filename + f".{int(term)}.streamlines.filtered" + ".tck")
            tck_filt: File = File(tck_filt)
        else:
            tck_filt: str = os.path.join(path,filename + ".streamlines.filtered" + ".tck")
            tck_filt: File = File(tck_filt)
        
        # Filter tracks
        filt = Command("tcksift")
        filt.cmd_list.append(tck.file)
        filt.cmd_list.append(wm_fod.file)
        filt.cmd_list.append(tck_filt.file)
        
        if mask:
            filt.cmd_list.append("-proc_mask")
            filt.cmd_list.append(mask.file)
        
        if term:
            filt.cmd_list.append("-term_number")
            filt.cmd_list.append(f"{term}")
        
        filt.run(self.log)
        
        return tck_filt
    
    def compute_diff_metrics(self,
                             dwi: Mif,
                             mask: Optional[Mif] = None,
                             fa: bool = True,
                             md: bool = True,
                             ad: bool = True,
                             rd: bool = True,
                             cleanup = True,
                             force: bool = False
                            ) -> Tuple[Mif,Mif,Mif,Mif]:
        '''Computes diffusion metrics for some input DWI MIF file object.

        Args:
            dwi: Input DWI MIF file object.
            mask: Corresponding mask MIF file object.
            fa: Compute FA map.
            md: Compute MD (ADC) map.
            ad: Compute AD map.
            rd: Compute RD map.
            cleanup: Perform clean-up.
            force: Force overwrite of existing file.

        Returns:
            fa_mif: FA map MIF file object.
            md_mif: MD map MIF file object.
            ad_mif: AD map MIF file object.
            rd_mif: RD map MIF file object.
        '''
        [path, filename, _ext] = self.nii_file.file_parts()
        
        if ".gz" in dwi.file:
            ext = ".mif.gz"
        else:
            ext = ".mif"
        
        # Output file names
        tensor: str = os.path.join(path,filename + f".diff_tensor" + ext)
        md_mif: str = os.path.join(path,filename + f".md" + ext)
        fa_mif: str = os.path.join(path,filename + f".fa" + ext)
        ad_mif: str = os.path.join(path,filename + f".ad" + ext)
        rd_mif: str = os.path.join(path,filename + f".rd" + ext)
        
        tensor: Mif = self.Mif(tensor)
        md_mif: Mif = self.Mif(md_mif)
        fa_mif: Mif = self.Mif(fa_mif)
        ad_mif: Mif = self.Mif(ad_mif)
        rd_mif: Mif = self.Mif(rd_mif)
        
        # Compute tensors
        tens = Command("dwi2tensor")
        tens.cmd_list.append(dwi.file)
        tens.cmd_list.append(tensor.file)
        
        if mask:
            tens.cmd_list.append("-mask")
            tens.cmd_list.append(mask.file)
        
        if force:
            tens.cmd_list.append("-force")
        
        tens.run(self.log)
        
        # Compute diffusion tensor metrics
        metric = Command("tensor2metric")
        metric.cmd_list.append(tensor.file)
        
        if md:
            metric.cmd_list.append("-adc")
            metric.cmd_list.append(md_mif.file)
        
        if fa:
            metric.cmd_list.append("-fa")
            metric.cmd_list.append(fa_mif.file)
        
        if ad:
            metric.cmd_list.append("-ad")
            metric.cmd_list.append(ad_mif.file)
            
        if rd:
            metric.cmd_list.append("-rd")
            metric.cmd_list.append(rd_mif.file)
        
        metric.run(self.log)
        
        # Clean-up
        if cleanup:
            os.remove(tensor.file)
        
        return fa_mif,md_mif,ad_mif,rd_mif
    
    def structural_connectome(self,
                              tck: File,
                              labels: File,
                              dwi: Optional[Mif] = None,
                              mask: Optional[Mif] = None,
                              symmetric: bool = False,
                              zero_diagonal: bool = False,
                              fa: bool = False,
                              md: bool = False,
                              ad: bool = False,
                              rd: bool = False,
                              cleanup:bool = True,
                              force: bool = False
                             ) -> Tuple[File,File,File,File,File]:
        '''Constructs the structural connectome of an input DWI MIF file object, and an atlas/label 
        NIFTI/MIF file object.

        Args:
            tck: Input tck file object.
            labels: Input label NIFTI/MIF file object.
            dwi: Corresponding DWI MIF file object (if metric weighting is to be performed).
            mask: Corresponding mask image MIF file object. 
            symmetric: Output symmetric matrices.
            zero_diagonal: Output zeroed diagonal matrices.
            fa: Perform FA weighting of the structural connectome.
            md: Perform MD weighting of the structural connectome.
            ad: Perform AD weighting of the structural connectome.
            rd: Perform RD weighting of the structural connectome.
            cleanup: Perform clean-up.
            force: Force overwrite of existing file.

        Returns:
            connectome: Structural connectome file object.
            fa_connectome: FA weighted structural connectome file object.
            md_connectome: MD weighted structural connectome file object.
            ad_connectome: AD weighted structural connectome file object.
            rd_connectome: RD weighted structural connectome file object.
        '''
        [path, filename, _ext] = self.nii_file.file_parts()
        
        # Create output filenames
        connectome: str = os.path.join(path,filename + f".structural_connectome" + ".txt")
        fa_connectome: str = os.path.join(path,filename + f".structural_connectome.fa_weighted" + ".txt")
        md_connectome: str = os.path.join(path,filename + f".structural_connectome.md_weighted" + ".txt")
        ad_connectome: str = os.path.join(path,filename + f".structural_connectome.ad_weighted" + ".txt")
        rd_connectome: str = os.path.join(path,filename + f".structural_connectome.rd_weighted" + ".txt")
        tmp_metric: str = os.path.join(path,filename + f"metric.vertex.mean.csv")
        
        connectome: File = File(connectome)
        fa_connectome: File = File(fa_connectome)
        md_connectome: File = File(md_connectome)
        ad_connectome: File = File(ad_connectome)
        rd_connectome: File = File(rd_connectome)
        tmp_metric: File = File(tmp_metric)
            
        if fa or md or ad or rd:
            if dwi:
                [fa_mif, \
                 md_mif, \
                 ad_mif, \
                 rd_mif] = self.compute_diff_metrics(dwi=dwi,
                                                     mask=mask,
                                                     fa=fa,
                                                     md=md,
                                                     ad=ad,
                                                     rd=rd,
                                                     cleanup=cleanup,
                                                     force=force)
            else:
                MRtrixError("Input DWI mif file was not present.")
            
        # Compute structural connectome
        ctm = Command("tck2connectome")
        ctm.cmd_list.append(tck.file)
        ctm.cmd_list.append(labels.file)
        ctm.cmd_list.append(connectome.file)
        if symmetric:
            ctm.cmd_list.append("-symmetric")
        if zero_diagonal:
            ctm.cmd_list.append("-zero_diagonal")
        if force:
            ctm.cmd_list.append("-force")
        ctm.run(self.log)
        del ctm
        
        # Construct list of metrics
        metrics: List[Mif] = []
        out_files: List[File] = []
            
        if fa:
            metrics.append(fa_mif)
            out_files.append(fa_connectome)
        if md:
            metrics.append(md_mif)
            out_files.append(md_connectome)
        if ad:
            metrics.append(ad_mif)
            out_files.append(ad_connectome)
        if rd:
            metrics.append(rd_mif)
            out_files.append(rd_connectome)
        
        # Compute weighted structural connectome(s)
        if fa or md or ad or rd:
            for item in zip(metrics,out_files):
                # Sample mean vertex value
                tck_smp = Command("tcksample")
                tck_smp.cmd_list.append(tck.file)
                tck_smp.cmd_list.append(item[0].file)
                tck_smp.cmd_list.append(tmp_metric.file)
                tck_smp.cmd_list.append("-stat_tck")
                tck_smp.cmd_list.append("mean")
                # tck_smp.cmd_list.append("-force")
                tck_smp.run(self.log)
                del tck_smp

                # Compute weighted connectome
                ctm = Command("tck2connectome")
                ctm.cmd_list.append(tck.file)
                ctm.cmd_list.append(labels.file)
                ctm.cmd_list.append(item[1].file)
                ctm.cmd_list.append("-scale_file")
                ctm.cmd_list.append(tmp_metric.file)
                ctm.cmd_list.append("-stat_edge")
                ctm.cmd_list.append("mean")
                if symmetric:
                    ctm.cmd_list.append("-symmetric")
                if zero_diagonal:
                    ctm.cmd_list.append("-zero_diagonal")
                if force:
                    ctm.cmd_list.append("-force")
                ctm.run(self.log)
                del ctm
                
                os.remove(tmp_metric.file)
        
        return connectome,fa_connectome,md_connectome,ad_connectome,rd_connectome

class DWIxfm(object):
    '''Class that contains the associated wrapper functions for performing linear and
    non-linear transformations of NIFTI-2 and MIF files using FSL.

    Attributes:
        dwi_file: Input NIFTI-2 DWI file.
        dwi_bval: Corresponding FSL bval file.
        dwi_bvec: Corresponding FSL bvec file.
        dwi_json: Corresponding JSON (sidecar) file.
        template: NIFTI-2 template.
        template_brain: NIFTI-2 brain template.
        labels: NIFTI-2 brain template (integer) labels.
        log: Log file name.
    '''
    
    dwi_file: NiiFile = ""
    dwi_bval: File = ""
    dwi_bvec: File = ""
    dwi_json: File = ""
    
    template: NiiFile = ""
    template_brain:NiiFile = ""
    labels: NiiFile = ""
    
    log: LogFile = ""
    
    def __init__(self,
                 dwi_file: str,
                 dwi_bval: str,
                 dwi_bvec: str,
                 template: str,
                 template_brain: str,
                 labels: str,
                 log:str,
                 dwi_json: Optional[str] = None
                 ) -> None:
        '''Init doc-string for DWIxfm class.

        Usage example:
            >>> dwi_obj = DWIxfm("file.nii",
            >>>                  "file.bval",
            >>>                  "file.bvec",
            >>>                  "template.nii",
            >>>                  "template_brain.nii",
            >>>                  "labels.nii",
            >>>                  "file.log")
            >>> dwi_obj.dwi_file
            "file.nii"

        Args:
            dwi_file: Input NIFTI-2 DWI file.
            dwi_bval: Corresponding FSL bval file.
            dwi_bvec: Corresponding FSL bvec file.
            template: NIFTI-2 template.
            template_brain: NIFTI-2 brain template.
            labels: NIFTI-2 brain template (integer) labels.
            log: Log file name.
            dwi_json: Corresponding JSON (sidecar) file.
        '''
        self.dwi_file: str = dwi_file
        self.dwi_bval: str = dwi_bval
        self.dwi_bvec: str = dwi_bvec
        self.dwi_json: str = dwi_json
        self.template: str = template
        self.template_brain: str = template_brain
        self.labels: str = labels
        self.log: str = log

        self.dwi_file: NiiFile = NiiFile(self.dwi_file)
        self.dwi_bval: File = File(self.dwi_bval)
        self.dwi_bvec: File = File(self.dwi_bvec)
        self.dwi_json: File = File(self.dwi_json)
        self.template: NiiFile = NiiFile(self.template)
        self.template_brain: NiiFile = NiiFile(self.template_brain)
        self.labels: NiiFile = NiiFile(self.labels)
        self.log: LogFile = LogFile(self.log)
            
    def mask_dwi(self,
                frac_int: float = 0.5
                ) -> Tuple[NiiFile,NiiFile,NiiFile]:
        '''Creates an image file mask for an input DWI NIFTI-2 file object.

        Usage example:
            >>> dwi_obj = DWIxfm("file.nii",
            >>>                  "file.bval",
            >>>                  "file.bvec",
            >>>                  "template.nii",
            >>>                  "template_brain.nii",
            >>>                  "labels.nii",
            >>>                  "file.log")
            >>>
            >>> [mask,brain,head] = mask_dwi(frac_int=0.5)

        Args:
            frac_int: Fractional intensity threshold. Smaller values give larger brain outline estimates.

        Returns:
            mask: Binary mask image NIFTI-2 file object.
            brain: Brain iamge NIFTI-2 file object.
            head: Whole head image NIFTI-2 file object.
        '''
        [path, filename, ext] = self.dwi_file.file_parts()
        
        brain: str = os.path.join(path,filename + "_brain" + ext)
        mask: str = os.path.join(path,filename + "_brain_mask" + ext)
        head: str = os.path.join(path,filename + "_head" + ext)
        
        brain: NiiFile = NiiFile(brain)
        mask: NiiFile = NiiFile(mask)
        head: NiiFile = NiiFile(head)
        
        dwi = ReconMRtrix(self.dwi_file.file,
                         self.dwi_bval.file,
                         self.dwi_bvec.file,
                         self.dwi_json.file,
                         self.log)
        
        mif_file = dwi.nifti_to_mif()
        
        [mask_mif,brain_mif,head_mif] = dwi.create_mask(mif_file,frac_int)
        
        # Convert NIFTI to MIF
        mr_convert = Command("mrconvert")
        mr_convert.cmd_list.append(mask_mif.file)
        mr_convert.cmd_list.append(mask.file)
        mr_convert.run(self.log)
        
        mr_convert = Command("mrconvert")
        mr_convert.cmd_list.append(brain_mif.file)
        mr_convert.cmd_list.append(brain.file)
        mr_convert.run(self.log)
        
        mr_convert = Command("mrconvert")
        mr_convert.cmd_list.append(head_mif.file)
        mr_convert.cmd_list.append(head.file)
        mr_convert.run(self.log)
        
        # Clean-up
        os.remove(mask_mif.file)
        os.remove(brain_mif.file)
        os.remove(head_mif.file)
        
        return mask,brain,head
    
    def compute_linear_xfm(self,
                           dwi_brain: NiiFile,
                           dof: int = 12
                          ) -> Tuple[File,NiiFile]:
        '''Computes linear transform of the template_brain class member variable to the
        input skull-stripped DWI NIFTI-2 image file object. This is a wrapper
        function for FSL's `FLIRT`.

        Args:
            dwi_brain: Input skull-stripped DWI NIFTI-2 image file object.
            dof: Degrees of freedom. Valid values include: 6, 9, 12.
        
        Returns:
            xfm_mat: Output linear transormation matrix file object.
            xfm_out: Output linearly transormed NIFTI-2 image file object.
        '''
        [path, filename, ext] = self.dwi_file.file_parts()
        
        xfm_mat: str = os.path.join(path,filename + f".lin_xfm_{dof}_dof" + ".mat")
        xfm_out: str = os.path.join(path,filename + f".lin_xfm_{dof}_dof" + ext)
            
        xfm_mat: File = File(xfm_mat)
        xfm_out: NiiFile = NiiFile(xfm_out)
        
        if not dwi_brain.file:
            FSLError("DWI file not present.")
        
        lin_xfm = Command("flirt")
        lin_xfm.cmd_list.append("-in")
        lin_xfm.cmd_list.append(self.template_brain.abs_path())
        lin_xfm.cmd_list.append("-ref")
        lin_xfm.cmd_list.append(dwi_brain.abs_path())
        lin_xfm.cmd_list.append("-omat")
        lin_xfm.cmd_list.append(xfm_mat.file)
        lin_xfm.cmd_list.append("-out")
        lin_xfm.cmd_list.append(xfm_out.file)
        
        lin_xfm.run(self.log)
        
        return xfm_mat,xfm_out
    
    def compute_non_linear_xfm(self,
                               xfm_mat: File,
                               dwi_head: NiiFile
                              ) -> Tuple[NiiFile,NiiFile,NiiFile]:
        '''Computes non-linear transform of the template class member variable to the
        input whole head of the DWI NIFTI-2 image file object. This is a wrapper
        function for FSL's `FNIRT`.

        Args:
            xfm_mat: Input linear transormation matrix file object.
            dwi_head: Input whole head DWI NIFTI-2 image file object.
        
        Returns:
            nl_out: Output non-linearly transormed (stanard -> native) NIFTI-2 image file object.
            nl_warp: Corresponding non-linear warp field, stored as NIFTI-2 image file object.
            nl_wpcf: Corresponding non-linear warp field coefficients, stored as NIFTI-2 image file object.
        '''
        [path, filename, ext] = self.dwi_file.file_parts()
        
        nl_out: str = os.path.join(path,filename + f".non-lin_xfm" + ext)
        nl_warp: str = os.path.join(path,filename + f".non-lin_xfm.warp_field" + ext)
        nl_wpcf: str = os.path.join(path,filename + f".non-lin_xfm.warp_field_coeff" + ext)
        
        nl_out: NiiFile = NiiFile(nl_out)
        nl_warp: NiiFile = NiiFile(nl_warp)
        nl_wpcf: NiiFile = NiiFile(nl_wpcf)
        
        if not xfm_mat.file:
            FSLError("Linear transformation matrix not present.")
        
        if not dwi_head.file:
            FSLError("DWI file not present.")
        
        non_lin = Command("fnirt")
        non_lin.cmd_list.append(f"--in={self.template.abs_path()}")
        non_lin.cmd_list.append(f"--ref={dwi_head.abs_path()}")
        non_lin.cmd_list.append(f"--aff={xfm_mat.file}")
        non_lin.cmd_list.append(f"--iout={nl_out.file}")
        non_lin.cmd_list.append(f"--fout={nl_warp.file}")
        non_lin.cmd_list.append(f"--cout={nl_wpcf.file}")
        non_lin.run(self.log)
        
        return nl_out,nl_warp,nl_wpcf
    
    def applywarp(self,
                  dwi_head: NiiFile,
                  non_lin_warp: NiiFile,
                  interp: str = "nn",
                  rel: bool = True,
                  premat: Optional[File] = None,
                 ) -> NiiFile:
        '''Applies pre-computed non-linear transform to the labels class member variable in reference to
        some input input whole head DWI NIFTI-2 file object. This is a wrapper function for FSL's `applywarp`.

        Args:
            dwi_head: Input whole head DWI NIFTI-2 image file object.
            non_lin_warp: Input non-linear warp field (coefficients), stored as NIFTI-2 image file object.
            interp: Interpolation method to use. Valid options include:
                * "nn" (nearest neighbour)
                * "trilinear"
                * "sinc"
                * "spline"
            rel: Treat warp field as relative, rather than absolute.
            premat: Input linear transormation matrix file object.

        Returns:
            out: Output non-linearly transormed (stanard -> native) labels NIFTI-2 image file object.
        '''
        [path, filename, ext] = self.dwi_file.file_parts()
        
        out: str = os.path.join(path,filename + f".labels.non-linear" + ext)
        out: NiiFile = NiiFile(out)
        
        if not dwi_head.file:
            FSLError("DWI file not present.")
        
        if not non_lin_warp.file:
            FSLError("Warp file not present.")
        
        warp = Command("applywarp")
        warp.cmd_list.append(f"--in={self.labels.abs_path()}")
        warp.cmd_list.append(f"--ref={dwi_head.abs_path()}")
        warp.cmd_list.append(f"--warp={non_lin_warp.abs_path()}")
        warp.cmd_list.append(f"--out={out.file}")
        
        if premat:
            warp.cmd_list.append(f"--premat={premat.abs_path()}")
        
        if interp:
            warp.cmd_list.append(f"--interp={interp}")
        
        if rel:
            warp.cmd_list.append("--rel")
        else:
            warp.cmd_list.append("--abs")
        
        warp.run(self.log)
        
        return out

def compute_xfm(dwi: str,
                bval: str,
                bvec: str,
                template: str,
                template_brain: str,
                labels: str,
                json: Optional[str] = None,
                log: Optional[str] = "file.log",
                work_dir: Optional[str] = None,
                use_cwd: bool = False,
                dof: int = 12,
                frac_int: float = 0.5
               ) -> Tuple[NiiFile,NiiFile]:
    '''Computes and applies linear and non-linear transforms to some input NIFTI-2 image template 
    and its corresponding NIFTI-2 integer label file.

    Args:
        dwi: Input NIFTI-2 DWI file.
        bval: Corresponding FSL bval file.
        bvec: Corresponding FSL bvec file.
        template: NIFTI-2 template.
        template_brain: NIFTI-2 brain template.
        labels: NIFTI-2 brain template (integer) labels.
        json: Corresponding JSON (sidecar) file.
        log: Log file name.
        work_dir: Working directory path. If not specified, then the current working directory (cwd)
            is used as the parent directory, the working directory is named 'work.tmp'.
        use_cwd: Use current working directory as parent directory.
        dof: Degrees of freedom for linear transformations. Valid values include: 6, 9, 12.
        frac_int: Fractional intensity threshold. Smaller values give larger brain outline estimates.

    Returns:
        labels_native: Output NIFTI-2 image file object of template labels in subject native space.
        nl_out: Output NIFTI-2 image file object of template in subject native space.
    '''
    # Create temporary working directory
    if work_dir:
        pass
    else:
        work_dir = "work.tmp"
        use_cwd = True
        
    work_tmp: TmpDir = TmpDir(work_dir,use_cwd=use_cwd)
    work_tmp.mk_tmp_dir()
        
    # Copy over the required data
    f_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(dwi),work_tmp.tmp_dir)
    b_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(bval),work_tmp.tmp_dir)
    e_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(bvec),work_tmp.tmp_dir)

    copy(dwi,f_tmp.file)
    copy(bval,b_tmp.file)
    copy(bvec,e_tmp.file)
    
    if json:
        j_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(json),work_tmp.tmp_dir)
        copy(json,j_tmp.file)
    
    # Create Diffusion image transformation object
    dwi = DWIxfm(dwi_file=f_tmp.file,
                 dwi_bval=b_tmp.file,
                 dwi_bvec=e_tmp.file,
                 template=template,
                 template_brain=template_brain,
                 labels=labels,
                 log=log,
                 dwi_json=j_tmp.file)
    
    # Perform brain extraction of B0s
    [mask, brain, head] = dwi.mask_dwi(frac_int=frac_int)
    
    # Compute linear transform
    [xfm_mat, xfm_out] = dwi.compute_linear_xfm(dwi_brain=brain,
                                                dof=12)
    
    # Compute non-linear transform
    [nl_out, nl_warp, nl_wpcf] = dwi.compute_non_linear_xfm(xfm_mat=xfm_mat,
                                                            dwi_head=head)
    
    # Apply non-linear transform to atlas/template labels
    labels_native = dwi.applywarp(dwi_head=head,
                                  non_lin_warp=nl_warp,
                                  interp="nn",
                                  rel=True,
                                  premat=None)
    return labels_native, nl_out

def create_structural_connectome(dwi: str,
                                 bval: str,
                                 bvec: str,
                                 template: str,
                                 template_brain: str,
                                 labels: str,
                                 json: Optional[str] = None,
                                 log: Optional[str] = "file.log",
                                 work_dir: Optional[str] = None,
                                 use_cwd: bool = False,
                                 force: bool = False,
                                 gzip: bool = False,
                                 erode: int = 0,
                                 fa_thresh: float = 0.2,
                                 vox: float = 1.5,
                                 dof: int = 12,
                                 frac_int: float = 0.5,
                                 stream_lines: int = 1e5,
                                 cutoff: float = 0.07,
                                 filter_tracts: bool = False,
                                 term: Optional[int] = None,
                                 symmetric: bool = False,
                                 zero_diagonal: bool = False,
                                 fa: bool = True,
                                 md: bool = True,
                                 ad: bool = True,
                                 rd: bool = True,
                                 cleanup: bool = True
                                ) -> Tuple[File,File,File,File,File,NiiFile,NiiFile,TmpDir]:
    '''Constructs a structural connectome given a DWI file, and a set of an integer labeled atlas.

    Args:
        dwi: Input NIFTI-2 DWI file.
        bval: Corresponding FSL bval file.
        bvec: Corresponding FSL bvec file.
        template: NIFTI-2 template.
        template_brain: NIFTI-2 brain template.
        labels: NIFTI-2 brain template (integer) labels.
        json: Corresponding JSON (sidecar) file.
        log: Log file name.
        work_dir: Working directory path. If not specified, then the current working directory (cwd)
            is used as the parent directory, the working directory is named 'work.tmp'.
        use_cwd: Use current working directory as parent directory.
        force: Force overwrite of existing MIF file.
        gzip: Gzip output file.
        erode: Number of erosion passes for (whole brain) mask.
        fa_thresh: FA threshold for crude WM vs GM-CSF separation.
        vox: Desired output voxel size (in mm) to use when upsampling images.
        dof: Degrees of freedom for linear transformations. Valid values include: 6, 9, 12.
        frac_int: Fractional intensity threshold. Smaller values give larger brain outline estimates.
        stream_lines: Number of streamlines to generate for the tck file.
        cutoff: FOD track termination threshold.
        filter_tracts: Enable track filtering.
        term: Number of streamlines to remain after filtering.
        symmetric: Output symmetric matrices.
        zero_diagonal: Output zeroed diagonal matrices.
        fa: Perform FA weighting of the structural connectome.
        md: Perform MD weighting of the structural connectome.
        ad: Perform AD weighting of the structural connectome.
        rd: Perform RD weighting of the structural connectome.
        cleanup: Perform clean-up.
        
    Returns:
        connectome: Structural connectome file object.
        fa_connectome: FA weighted structural connectome file object.
        md_connectome: MD weighted structural connectome file object.
        ad_connectome: AD weighted structural connectome file object.
        rd_connectome: RD weighted structural connectome file object.
        labels_native: labels_native: Output NIFTI-2 image file object of template labels in subject native space.
        head: Output NIFTI-2 image file object of template in subject native space.
        work_tmp: Temporary (working) directory object.
    
    TODO:
        * Implement functions to create QC images for tracks and iamge transforms.
    '''
    # Create temporary working directory
    if work_dir:
        pass
    else:
        work_dir = "work.tmp"
        use_cwd = True
        
    work_tmp: TmpDir = TmpDir(work_dir,use_cwd=use_cwd)
    work_tmp.mk_tmp_dir()
        
    # Copy over the required data
    f_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(dwi),work_tmp.tmp_dir)
    b_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(bval),work_tmp.tmp_dir)
    e_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(bvec),work_tmp.tmp_dir)

    copy(dwi,f_tmp.file)
    copy(bval,b_tmp.file)
    copy(bvec,e_tmp.file)
    
    if json:
        j_tmp: TmpFile = work_tmp.TmpFile(os.path.basename(json),work_tmp.tmp_dir)
        copy(json,j_tmp.file)
    else:
        j_tmp = None
    
    # Transform atlas labels to subject space
    [labels_native, non_lin_out] = compute_xfm(dwi=f_tmp.file, 
                                               bval=b_tmp.file,
                                               bvec=e_tmp.file,
                                               template=template,
                                               template_brain=template_brain,
                                               labels=labels,
                                               json=j_tmp.file,
                                               log=log,
                                               work_dir=work_dir,
                                               use_cwd=use_cwd,
                                               dof=dof,
                                               frac_int=frac_int)
    
    # Create MRtrix difussion image processing object
    mr_diff = ReconMRtrix(nii_file=f_tmp.file,
                          bval=b_tmp.file,
                          bvec=e_tmp.file,
                          json_file=j_tmp.file,
                          log=log)
    
    # Convert NIFTI file to MIF file
    dwi_miff = mr_diff.nifti_to_mif(force=force,
                                   gzip=gzip)
    
    # Estimate response function(s)
    [wm_res, gm_res, csf_res] = mr_diff.estimate_response(mif=dwi_miff,
                                                          erode=erode,
                                                          fa_thresh=fa_thresh,
                                                          force=force)
    
    # Upsample dwi and native space labels
    up_dwi_mif = mr_diff.mr_upsample(mif=dwi_miff,
                                     vox=vox)
    
    up_labels_native = mr_diff.mr_upsample(mif=labels_native,
                                           vox=vox,
                                           interp="nearest")
    
    # Perform brain extraction of B0s
    [mask, brain, head] = mr_diff.create_mask(mif=up_dwi_mif,
                                              frac_int=frac_int,
                                              cleanup=True)
    
    # Compute single-shell 3-tissue CSD
    [wm_fod, gm, csf] = mr_diff.ss3t_csd(mif=up_dwi_mif, 
                                         mask=mask, 
                                         wm_res=wm_res, 
                                         gm_res=gm_res, 
                                         csf_res=csf_res)
    
    # Perform joint bias-field correction
    [wm_fod_norm, gm_norm, csf_norm] = mr_diff.bias_field_correction(wm_fod=wm_fod, 
                                                                     gm_tis=gm, 
                                                                     csf_tis=csf, 
                                                                     mask=mask)
    
    # Compute DEC and VF maps [for QC purposes]
    [dec, vf] = mr_diff.compute_dec_map(wm_fod=wm_fod_norm, 
                                        gm_tis=gm_norm,
                                        csf_tis=csf_norm,
                                        mask=mask)
    
    # Reconstruct Fiber tracts
    if filter_tracts:
        tmp_tcks = mr_diff.mr_tck_global(wm_fod=wm_fod_norm,
                                         mask=mask,
                                         stream_lines=stream_lines,
                                         cutoff=cutoff)
        tcks = mr_diff.mr_tck_sift(tck=tmp_tcks,
                                   wm_fod=wm_fod_norm,
                                   term=term,
                                   mask=mask)
    else:
        tcks = mr_diff.mr_tck_global(wm_fod=wm_fod_norm,
                                     mask=mask,
                                     stream_lines=stream_lines,
                                     cutoff=cutoff)
    
    # Compute structural connectome
    [connectome, \
     fa_connectome, \
     md_connectome, \
     ad_connectome, \
     rd_connectome] = mr_diff.structural_connectome(tck=tcks,
                                                    labels=up_labels_native,
                                                    dwi=up_dwi_mif,
                                                    mask=mask,
                                                    symmetric=symmetric,
                                                    zero_diagonal=zero_diagonal,
                                                    fa=fa,
                                                    md=md,
                                                    ad=ad,
                                                    rd=rd,
                                                    force=force,
                                                    cleanup=cleanup)
    
    return connectome, fa_connectome, md_connectome, ad_connectome, rd_connectome, labels_native, head, work_tmp

if __name__ == "__main__":
    main()

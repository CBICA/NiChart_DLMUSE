# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

import argparse
import os
import sys

import pkg_resources  # part of setuptools
import Structural

VERSION = pkg_resources.require("spare_scores")[0].version

def main():
    prog = "niCHARTPipelines"
    description = "niCHART Data Preprocessing Pipelines"
    usage = """
    niCHARTPipelines v{VERSION}
    ICV calculation, brain segmentation, and ROI extraction pipelines for 
    structural MRI data.
    required arguments:
        [INDIR]         The filepath of the directory containing the input. The 
        [-i, --inDir]   input can be a single .nii.gz (or .nii) file or a  
                        directory containing .nii.gz files (or .nii files). 

        [OUTDIR]        The filepath of the directory where the output will be
        [-o, --outdir]  saved.

        [DLICVMDL]      The filepath of the DLICV model will be. In case the
                        model to be used is an nnUNet model, the filepath of
                        the model's parent directory should be given. Example: 
                        /path/to/nnUNetTrainedModels/nnUNet/
        
        [DLMUSEMDL]     The filepath of the DLMUSE model will be. In case the
                        model to be used is an nnUNet model, the filepath of
                        the model's parent directory should be given. Example:
                        /path/to/nnUNetTrainedModels/nnUNet/

        [PIPELINETYPE]  Specify type of pipeline[structural, dti, fmri]. 
                        Currently only structural pipeline is supported.

        [SCANID]        Scan ID of the subject, if only one scan is given. If
                        multiple scans are given, this argument will be 
                        ignored, and the scan ID will be extracted from the
                        filename of the input file(s).

        [DERIVED_ROI_MAPPINGS_FILE] The filepath of the derived MUSE ROI 
                                    mappings file.

        [MUSE_ROI_MAPPINGS_FILE]    The filepath of the MUSE ROI mappings file.
                        
    optional arguments: 
        [NNUNET_RAW_DATA_BASE]  The filepath of the base directory where the 
                                raw data of are saved.  This argument is only 
                                required if the DLICVMDL and DLMUSEMDL 
                                arguments are corresponding to a  nnUNet model 
                                (v1 needs this currently).

        [NNUNET_PREPROCESSED]   The filepath of the directory where the 
                                intermediate preprocessed data are saved. This
                                argument is only required if the DLICVMDL and
                                DLMUSEMDL arguments are corresponding to a
                                nnUNet model (v1 needs this currently).

        [DLICV_TASK]            The task number of the DLICV model. This 
                                argument is only required if the DLICVMDL is a 
                                nnUNet model.

        [DLMUSE_TASK]           The task number of the DLMUSE model. This 
                                argument is only required if the DLMUSEMDL is a 
                                nnUNet model.

        [DLICV_FOLD]            The fold number of the DLICV model. This 
                                argument is only required if the DLICVMDL is a
                                nnUNet model.

        [DLMUSE_FOLD]           The fold number of the DLMUSE model. This
                                argument is only required if the DLMUSEMDL is a
                                nnUNet model.
    
        [-h, --help]    Show this help message and exit.
        
        [-v, --version] Show program's version number and exit.
    """.format(VERSION=VERSION)

    parser = argparse.ArgumentParser(prog=prog,
                                     usage=usage,
                                     description=description,
                                     add_help=False)
    
    # INDIR argument
    parser.add_argument('-i',
                        '--indir', 
                        type=str, 
                        help='Input T1 image file path.', 
                        default=None, 
                        required=True)
    
    # OUTDIR argument
    parser.add_argument('-o',
                        '--outdir', 
                        type=str,
                        help='Output file name with extension.', 
                        default=None, required=True)
    
    # DLICVMDL argument
    parser.add_argument('--DLICVmdl', 
                        type=str, 
                        help='DLICV model path.', 
                        default=None, 
                        required=True)
    
    # DLMUSEMDL argument
    parser.add_argument('--DLMUSEmdl', 
                        type=str, 
                        help='DLMUSE Model path.', 
                        default=None, 
                        required=True)
    
    # PIPELINETYPE argument
    parser.add_argument('-p',
                        '--pipelinetype', 
                        type=str, 
                        help='Specify type of pipeline.', 
                        choices=['structural', 'dti', 'fmri'],
                        default='structural', 
                        required=True)
    
    # SCANID argument
    parser.add_argument('-s',
                        '--scanID', 
                        type=str, 
                        help='scan id.', 
                        default=None, 
                        required=True)
    
    # DERIVED_ROI_MAPPINGS_FILE argument
    parser.add_argument('--derived_ROI_mappings_file', 
                        type=str, 
                        help='derived MUSE ROI mappings file.', 
                        default=None, 
                        required=True)
    
    # MUSE_ROI_MAPPINGS_FILE argument
    parser.add_argument('--MUSE_ROI_mappings_file', 
                        type=str, 
                        help='MUSE ROI mappings file.', 
                        default=None, 
                        required=True)

    # NNUNET_RAW_DATA_BASE argument
    parser.add_argument('--nnUNet_raw_data_base',
                        type=str, 
                        help='nnUNet raw data base.', 
                        default=None)
    
    # NNUNET_PREPROCESSED argument
    parser.add_argument('--nnUNet_preprocessed',
                        type=str, 
                        help='nnUNet preprocessed.', 
                        default=None)
    
    # DLICV_TASK argument
    parser.add_argument('--DLICV_task',
                        type=int, 
                        help='DLICV task.', 
                        default=None)
    
    # DLMUSE_TASK argument
    parser.add_argument('--DLMUSE_task',
                        type=int, 
                        help='DLMUSE task.', 
                        default=None)
    
    # DLICV_FOLD argument
    parser.add_argument('--DLICV_fold',
                        type=int, 
                        help='DLICV fold.', 
                        default=None)
    
    # DLMUSE_FOLD argument
    parser.add_argument('--DLMUSE_fold',
                        type=int, 
                        help='DLMUSE fold.', 
                        default=None)
        
    # VERSION argument
    help = "Show the version and exit"
    parser.add_argument("-V", 
                        "--version", 
                        action='version',
                        version=prog+ ": v{VERSION}.".format(VERSION=VERSION),
                        help=help)

    # HELP argument
    help = 'Show this message and exit'
    parser.add_argument('-h', 
                        '--help',
                        action='store_true', 
                        help=help)
    
        
    args = parser.parse_args(sys.argv[1:])

    indir = args.indir
    outdir = args.outdir
    DLICVmdl = args.DLICVmdl
    DLMUSEmdl = args.DLMUSEmdl
    pipelinetype = args.pipelinetype
    scanID = args.scanID
    derived_ROI_mappings_file = args.derived_ROI_mappings_file
    MUSE_ROI_mappings_file = args.MUSE_ROI_mappings_file
    nnUNet_raw_data_base = args.nnUNet_raw_data_base
    nnUNet_preprocessed = args.nnUNet_preprocessed
    DLICV_task = args.DLICV_task
    DLMUSE_task = args.DLMUSE_task
    DLICV_fold = args.DLICV_fold
    DLMUSE_fold = args.DLMUSE_fold



    if(pipelinetype == "structural"):
        Structural.run_structural_pipeline(indir,
                                           DLICVmdl,
                                           DLMUSEmdl,
                                           outdir,
                                           MUSE_ROI_mappings_file,
                                           scanID,
                                           derived_ROI_mappings_file,
                                           nnUNet_raw_data_base,
                                           nnUNet_preprocessed,
                                           DLICV_task,
                                           DLMUSE_task,
                                           DLICV_fold,
                                           DLMUSE_fold)

    elif(pipelinetype == "fmri"):
        print("Coming soon.")
        exit()
    elif(pipelinetype == "dti"):
        print("Coming soon.")
        exit()
    else:
        print("Only [structural, dti and fmri] pipelines are supported.")
        exit()


if __name__ == '__main__':
    main()

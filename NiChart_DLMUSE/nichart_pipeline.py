import os
import shutil
from pathlib import Path
from typing import Any
import pandas as pd

from NiChart_DLMUSE import (
    utils,
    ReorientImage,
    CalculateROIVolume,
    CombineMasks,
    MaskImage,
    ROIRelabel
)

out_suff_LPS = '_LPS.nii.gz'

def run_pipeline(in_data, out_dir):
    '''
    NiChart pipeline
    '''

    # Detect input images
    df_img = make_img_list(in_data)

    # Set init paths and envs
    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Create working dir (FIXME: in output dir for now)
    basedir = os.path.join(out_dir, "working_dir")
    if os.path.exists(basedir):
        shutil.rmtree(basedir)
    os.makedirs(basedir, exist_ok=True)

    ## Reorient image to LPS
    apply_reorient(df_img, out_dir, ref_orient = 'LPS', out_suffix = out_suff_LPS)
    
    ### Apply DLICV
    #apply_dlicv(df_img, in_dir, out_dir):

    ### Create Mask
    #apply_mask(df_img, in_dir, out_dir):

    ### Create MUSE Node
    #apply_dlmuse(df_img, in_dir, out_dir):

    ### create muse relabel Node
    #apply_relabel_dlmuse(df_img, in_dir, out_dir):

    ### Create CombineMasks Node
    #apply_combine_masks(df_img, in_dir, out_dir):

    ### Create ReorientToOrg Node
    #apply_reorient_to_init(df_img, in_dir, out_dir):

    ### Create roi csv creation Node
    #apply_create_csv(df_img, in_dir, out_dir):

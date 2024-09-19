import os
import shutil
from pathlib import Path
from typing import Any
import pandas as pd

from NiChart_DLMUSE import utils as utils
from NiChart_DLMUSE import ReorientImage as reorient
    #CalculateROIVolume,
    #CombineMasks,
    #MaskImage,
    #ROIRelabeler
#)

out_suff_LPS = '_LPS.nii.gz'

def run_pipeline(in_data, out_dir):
    '''
    NiChart pipeline
    '''

    # Detect input images
    df_img = utils.make_img_list(in_data)

    # Set init paths and envs
    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    # Create working dir (FIXME: in output dir for now)
    working_dir = os.path.join(out_dir, "temp_working_dir")
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.makedirs(working_dir, exist_ok=True)

    ## Reorient image to LPS
    tmp_dir = os.path.join(out_dir, "s1_reorient")
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    reorient.apply_reorient(df_img, tmp_dir, ref_orient = 'LPS', out_suffix = out_suff_LPS)
    
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

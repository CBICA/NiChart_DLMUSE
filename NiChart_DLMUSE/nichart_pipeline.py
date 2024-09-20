import os
import shutil
from pathlib import Path
from typing import Any
import pandas as pd

from NiChart_DLMUSE import utils as utils
from NiChart_DLMUSE import ReorientImage as reorient
from NiChart_DLMUSE import RunDLICV as rundlicv
from NiChart_DLMUSE import MaskImage as maskimg
from NiChart_DLMUSE import RunDLMUSE as rundlmuse
from NiChart_DLMUSE import ROIRelabeler as relabelimg
from NiChart_DLMUSE import CalculateROIVolume as calcroi

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

    # Create working dir (FIXME: created within the output dir for now)
    working_dir = os.path.join(out_dir, "temp_working_dir")
    if os.path.exists(working_dir):
        shutil.rmtree(working_dir)
    os.makedirs(working_dir, exist_ok=True)

    ## Reorient image to LPS
    tmp_out_dir = os.path.join(working_dir, "s1_reorient_lps")
    if not os.path.exists(tmp_out_dir):
        os.makedirs(tmp_out_dir)
    reorient.apply_reorient(df_img, tmp_out_dir, ref_orient = 'LPS', out_suffix = out_suff_LPS)

    input('next ...')

    ### Apply DLICV
    tmp_in_dir = tmp_out_dir
    tmp_out_dir = os.path.join(working_dir, "s2_dlicv")
    if not os.path.exists(tmp_out_dir):
        os.makedirs(tmp_out_dir)
    rundlicv.apply_dlicv(df_img, tmp_in_dir, tmp_out_dir)

    input('next ...')

    ### Mask image
    tmp_in_dir = tmp_out_dir
    tmp_out_dir = os.path.join(working_dir, "s3_masked")
    if not os.path.exists(tmp_out_dir):
        os.makedirs(tmp_out_dir)
    maskimg.apply_mask_img(df_img, tmp_in_dir, tmp_out_dir)

    input('next ...')

    ### Apply DLMUSE
    tmp_in_dir = tmp_out_dir
    tmp_out_dir = os.path.join(working_dir, "s4_dlmuse")
    if not os.path.exists(tmp_out_dir):
        os.makedirs(tmp_out_dir)
    rundlmuse.apply_dlmuse(df_img, tmp_in_dir, tmp_out_dir)

    input('next ...')

    ### Relabel DLMUSE
    tmp_in_dir = tmp_out_dir
    tmp_out_dir = os.path.join(working_dir, "s5_relabeled")
    if not os.path.exists(tmp_out_dir):
        os.makedirs(tmp_out_dir)
    rundlmuse.apply_dlmuse(df_img, tmp_in_dir, tmp_out_dir)

    input('next ...')

    ### Combine DLICV and MUSE masks
    tmp_in_dir = tmp_out_dir
    tmp_out_dir = os.path.join(working_dir, "s6_combined")
    if not os.path.exists(tmp_out_dir):
        os.makedirs(tmp_out_dir)
    maskimg.apply_combine_masks(df_img, tmp_in_dir, tmp_out_dir)

    input('next ...')

    ### Reorient to initial orientation
    tmp_in_dir = tmp_out_dir
    reorient.apply_reorient_to_init(df_img, tmp_in_dir, out_dir)

    input('next ...')

    ### Create roi csv
    tmp_in_dir = tmp_out_dir
    calcroi.apply_create_roi_csv(df_img, tmp_in_dir, tmp_out_dir)
    calcroi.combine_roi_csvs(df_img, tmp_in_dir, tmp_out_dir)


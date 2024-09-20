import csv as csv
from pathlib import Path
from typing import Any

import nibabel as nib
import numpy as np
import pandas as pd


def calc_roi_volumes(MRID, in_img, label_indices):
    '''
    Creates a dataframe with the volumes of rois
    '''

    # Keep input lists as arrays
    label_indices = np.array(label_indices)

    # Read image
    nii = nib.load(in_img)
    img_vec = nii.get_fdata().flatten().astype(int)

    # Get counts of unique indices (excluding 0)
    img_vec = img_vec[img_vec != 0]
    u_ind, u_cnt = np.unique(img_vec, return_counts=True)

    # Get label indices
    if label_indices.shape[0] == 0:
        # logger.warning('Label indices not provided, generating from data')
        label_indices = u_ind

    label_names = label_indices.astype(str)

    # Get voxel size
    vox_size = np.prod(nii.header.get_zooms()[0:3])

    # Get volumes for all rois
    tmp_cnt = np.zeros(np.max([label_indices.max(), u_ind.max()]) + 1)
    tmp_cnt[u_ind] = u_cnt

    # Get volumes for selected rois
    sel_cnt = tmp_cnt[label_indices]
    sel_vol = (sel_cnt * vox_size).reshape(1, -1)

    # Create dataframe
    df_out = pd.DataFrame(index=[mrid], columns=label_names, data=sel_vol)
    df_out = df_out.reset_index().rename({"index": "MRID"}, axis=1)

    # Return output dataframe
    return df_out


def append_derived_rois(df_in, derived_roi_map):
    '''
    Calculates a dataframe with the volumes of derived rois.
    '''

    # Read derived roi map file to a dictionary
    roi_dict = {}
    with open(derived_roi_map) as roi_map:
        reader = csv.reader(roi_map, delimiter=",")
        for row in reader:
            key = str(row[0])
            val = [str(x) for x in row[2:]]
            roi_dict[key] = val

    # Calculate volumes for derived rois
    label_names = np.array(list(roi_dict.keys())).astype(str)
    label_vols = np.zeros(label_names.shape[0])
    for i, key in enumerate(roi_dict):
        key_vals = roi_dict[key]
        key_vol = df_in[key_vals].sum(axis=1)
        label_vols[i] = key_vol

    # Create dataframe
    mrid = df_in["MRID"][0]
    df_out = pd.DataFrame(
        index=[mrid], columns=label_names, data=label_vols.reshape(1, -1)
    )
    df_out = df_out.reset_index().rename({"index": "MRID"}, axis=1)

    # Return output dataframe
    return df_out

def create_roi_csv(mrid, in_roi, list_single_roi, map_derived_roi, out_csv)
    '''
    Creates a csv file with the results of the roi calculations
    '''

    # Calculate MUSE ROIs
    df_map = pd.read_csv(list_single_roi)

    # Add ROI for cortical CSF with index set to 1
    df_map = df_map.append(
        {"IndexMUSE": 1, "ROINameMUSE": "Cortical CSF"}, ignore_index=True
    )
    df_map = df_map.sort_values("IndexMUSE")

    list_roi = df_map.IndexMUSE.tolist()[1:]
    df_muse = calc_roi_volumes(scan_id, in_roi, list_roi)

    # Calculate Derived ROIs
    df_dmuse = append_derived_rois(df_muse, map_derived_roi)

    # Write out csv
    df_dmuse.to_csv(out_csv, index=False)

def apply_create_roi_csv(df_img, dlmuse_dir, dlicv_dir, out_dir,
                        dlmuse_suff = '_LPS.nii.gz',
                        dlicv_suffix = '_LPS.nii.gz',
                        out_suffix = '_LPS.nii.gz'):
    '''
    Apply reorientation to all images
    '''
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.MRID
        dlmuse_mask = os.path.join(in_dir, img_prefix + in_suffix)
        dlicv_mask = os.path.join(mask_dir, img_prefix + mask_suffix)
        out_img = os.path.join(out_dir, img_prefix + out_suffix)

        create_roi_csv(mrid, in_roi, list_single_roi, map_derived_roi, out_csv)

def combine_roi_csvs(df_img, dlmuse_dir, dlicv_dir, out_dir):
    '''
    Combine csv files
    '''
    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.MRID


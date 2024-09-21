import csv as csv
import os
from typing import Any

import nibabel as nib
import numpy as np
import pandas as pd


def calc_roi_volumes(mrid: Any, in_img: Any, label_indices: Any) -> pd.DataFrame:
    """
    Creates a dataframe with the volumes of rois
    """

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


def append_derived_rois(df_in: pd.DataFrame, derived_roi_map: Any) -> pd.DataFrame:
    """
    Calculates a dataframe with the volumes of derived rois.
    """

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
        key_vol = df_in[key_vals].sum(axis=1).values[0]
        label_vols[i] = key_vol

    # Create dataframe
    mrid = df_in["MRID"][0]
    df_out = pd.DataFrame(
        index=[mrid], columns=label_names, data=label_vols.reshape(1, -1)
    )
    df_out = df_out.reset_index().rename({"index": "MRID"}, axis=1)

    # Return output dataframe
    return df_out


def create_roi_csv(
    mrid: Any, in_roi: Any, list_single_roi: Any, map_derived_roi: Any, out_csv: str
) -> None:
    """
    Creates a csv file with the results of the roi calculations
    """

    # Calculate MUSE ROIs
    df_map = pd.read_csv(list_single_roi)
    df_map = df_map[["IndexMUSE", "ROINameMUSE"]]

    # Add ROI for cortical CSF with index set to 1
    df_map.loc[len(df_map)] = [1, "Cortical CSF"]
    df_map = df_map.sort_values("IndexMUSE")

    list_roi = df_map.IndexMUSE.tolist()[1:]
    df_muse = calc_roi_volumes(mrid, in_roi, list_roi)

    # Calculate Derived ROIs
    df_dmuse = append_derived_rois(df_muse, map_derived_roi)

    # Write out csv
    df_dmuse.to_csv(out_csv, index=False)


def apply_create_roi_csv(
    df_img: pd.DataFrame,
    in_dir: str,
    in_suff: str,
    dict_single_roi: str,
    dict_derived_roi: str,
    out_dir: str,
    out_suff: str,
) -> None:
    """
    Apply roi volume calc to all images
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.img_prefix
        mrid = tmp_row.MRID
        in_img = os.path.join(in_dir, img_prefix + in_suff)
        out_csv = os.path.join(out_dir, img_prefix + out_suff)

        create_roi_csv(mrid, in_img, dict_single_roi, dict_derived_roi, out_csv)


def combine_roi_csv(
    df_img: pd.DataFrame, in_dir: str, in_suff: str, out_dir: str, out_name: str
) -> None:
    """
    Combine csv files
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_csv = os.path.join(out_dir, out_name)

    dfs = []
    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.img_prefix
        in_csv = os.path.join(in_dir, img_prefix + in_suff)
        try:
            df_tmp = pd.read_csv(in_csv)
            dfs.append(df_tmp)
        except:
            print("Skip subject, out csv missing: " + in_csv)
    if len(dfs) > 0:
        df_out = pd.concat(dfs)
    df_out.to_csv(out_csv, index=False)

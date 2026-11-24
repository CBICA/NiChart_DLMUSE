import csv as csv
import logging
import os
from typing import Any, Optional

import nibabel as nib
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pipeline.log", encoding="utf-8", level=logging.DEBUG)


def calc_roi_volumes(mrid: Any, in_img: Any, label_indices: np.ndarray) -> pd.DataFrame:
    """
    Creates a dataframe with the volumes of rois

    :param mrid: the input mrid
    :type mrid: Any
    :param in_img: the input image
    :type in_img: niftii image
    :param label_indices: passed label indices
    :type label_indices: np.ndarray

    :return: Dataframe with details of images
    :rtype: pd.DataFrame
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

    :param df_in: the passed dataframe
    :type df_in: pd.DataFrame
    :param derived_roi_map: derived roi map file
    :type derived_roi_map: Any

    :return: ROI dataframe
    :rtype: pd.DataFrame
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

    :param mrid: the input mrid
    :type mrid: Any
    :param in_roi: the input ROI
    :type in_roi: Any
    :param map_derived_roi: derived roi map file
    :type map_derived_roi: Any
    :param out_csv: output csv filename
    :type out_csv: str

    :rtype: None
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

    :param df_img: the passed dataframe
    :type df_img: pd.DataFrame
    :param in_dir: the input directory
    :type in_dir: str
    :param in_suff: the input suffix
    :type in_suff: str
    :param out_dir: the output directory
    :type out_dir: str
    :param out_suff: the output suffix
    :type out_suff: str

    :rtype: None
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.img_prefix
        mrid = tmp_row.MRID
        in_img = os.path.join(in_dir, img_prefix + in_suff)
        out_csv = os.path.join(out_dir, img_prefix + out_suff)

        create_roi_csv(mrid, in_img, dict_single_roi, dict_derived_roi, out_csv)


def get_roi_columns(dict_derived_roi: str) -> list:
    """
    Column names of a per-scan ROI csv (MRID + derived ROIs, as written by create_roi_csv)

    :param dict_derived_roi: derived roi dictionary file

    :return: list of column names, starting with MRID
    :rtype: list
    """
    with open(dict_derived_roi) as roi_map:
        derived_cols = [str(row[0]) for row in csv.reader(roi_map, delimiter=",")]
    return ["MRID"] + derived_cols


def combine_roi_csv(
    df_img: pd.DataFrame,
    in_dir: str,
    in_suff: str,
    out_dir: str,
    out_name: str,
    dict_derived_roi: Optional[str] = None,
) -> None:
    """
    Combine csv files

    Every MRID in df_img gets a row in the output. Scans without a per-scan csv
    (e.g. dropped by QC) are kept with empty volumes.

    :param df_img: passed dataframe
    :type df_img: pd.DataFrame
    :param in_dir: the input directory
    :type in_dir: str
    :param in_suff: the input suffix
    :type in_suff: str
    :param out_dir: the output directory
    :type out_dir: str
    :param out_name: the desired output filename
    :type out_name: str
    :param dict_derived_roi: derived roi dictionary (used for the header if no csv exists)

    :rtype: None
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_csv = os.path.join(out_dir, out_name)

    dfs = []
    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.img_prefix
        in_csv = os.path.join(in_dir, img_prefix + in_suff)
        if not os.path.isfile(in_csv):
            logging.info("Scan has no volumes (out csv missing): " + in_csv)
            continue
        try:
            dfs.append(pd.read_csv(in_csv))
        except Exception as e:
            logging.info(f"Skip subject, could not read csv {in_csv}: {e}")

    if len(dfs) > 0:
        df_out = pd.concat(dfs)
    elif dict_derived_roi is not None:
        df_out = pd.DataFrame(columns=get_roi_columns(dict_derived_roi))
    else:
        df_out = pd.DataFrame(columns=["MRID"])

    # Keep one row per input MRID, in input order
    df_out["MRID"] = df_out["MRID"].astype(str)
    df_out = df_out.drop_duplicates("MRID", keep="last").set_index("MRID")
    df_out = df_out.reindex(df_img.MRID.astype(str).tolist())
    df_out.index.name = "MRID"
    df_out = df_out.copy()
    df_out = df_out.reset_index()

    df_out.to_csv(out_csv, index=False)

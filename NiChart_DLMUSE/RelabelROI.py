import os
from typing import Any

import nibabel as nib
import numpy as np
import pandas as pd


def relabel_rois(
    in_img: Any, roi_map: str, label_from: Any, label_to: Any, out_img: str
) -> None:
    """
    Convert labels in input roi image to new labels based on the mapping
    The mapping file should contain numeric indices for the mapping
    between the input roi image (from) and output roi image (to)

    :param in_img: the passed image
    :type in_img: niftii image
    :param roi_map: the passed roi map
    :type roi_map: str
    :param label_from: input roi image
    :type label_from: Any
    :param label_to: output roi image
    :type label_to: Any
    :param out_img: the desired filename for the output image
    :type out_img: str

    :rtype: None
    """

    # Read image
    in_nii = nib.load(in_img)
    img_mat = in_nii.get_fdata().astype(int)

    # Read dictionary with roi index mapping
    df_dict = pd.read_csv(roi_map)

    # Convert mapping dataframe to dictionaries
    v_from = df_dict[label_from].astype(int)
    v_to = df_dict[label_to].astype(int)

    # Create a mapping with consecutive numbers from dest to target values
    tmp_map = np.zeros(np.max([v_from, v_to]) + 1).astype(int)
    tmp_map[v_from] = v_to

    # Replace each value v in data by the value of tmp_map with the index v
    out_mat = tmp_map[img_mat].astype(np.uint8)

    # Write updated img
    out_nii = nib.Nifti1Image(out_mat, in_nii.affine, in_nii.header)
    nib.save(out_nii, out_img)


def apply_relabel_rois(
    df_img: pd.DataFrame,
    in_dir: str,
    in_suff: str,
    out_dir: str,
    out_suff: str,
    roi_map: Any,
    label_from: Any,
    label_to: Any,
) -> None:
    """
    Apply relabeling to all images

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
    :param roi_map: the roi map
    :type roi_map: Any
    :param label_from: input roi image
    :type label_from: Any
    :param label_to: output roi image
    :type label_to: Any

    :rtype: None
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        img_prefix = tmp_row.img_prefix
        in_img = os.path.join(in_dir, img_prefix + in_suff)
        out_img = os.path.join(out_dir, img_prefix + out_suff)

        relabel_rois(in_img, roi_map, label_from, label_to, out_img)

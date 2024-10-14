import logging
import os
from typing import Any

import nibabel as nib
import pandas as pd
from nibabel.orientations import axcodes2ornt, ornt_transform

IMG_EXT = ".nii.gz"

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pipeline.log", encoding="utf-8", level=logging.DEBUG)


def reorient_img(in_img: Any, ref: Any, out_img: Any) -> None:
    """
    Reorient image
    """
    if os.path.exists(out_img):
        logging.info("Out file exists, skip reorientation ...")

    else:
        # Read input img
        nii_in = nib.load(in_img)

        # Detect target orient
        if len(ref) == 3:
            ref_orient = ref
        else:
            nii_ref = nib.load(ref)
            ref_orient = nib.aff2axcodes(nii_ref.affine)
            ref_orient = "".join(ref_orient)

        # Find transform from current (approximate) orientation to
        # target, in nibabel orientation matrix and affine forms
        orient_in = nib.io_orientation(nii_in.affine)
        orient_out = axcodes2ornt(ref_orient)
        transform = ornt_transform(orient_in, orient_out)
        # affine_xfm = inv_ornt_aff(transform, nii_in.shape)

        # Apply transform
        reoriented = nii_in.as_reoriented(transform)

        # Write to out file
        reoriented.to_filename(out_img)


def apply_reorient_img(
    df_img: pd.DataFrame, ref_orient: Any, out_dir: str, out_suffix: str
) -> None:
    """
    Apply reorientation to all images
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        in_img = tmp_row.img_path
        out_img = os.path.join(out_dir, tmp_row.img_prefix + out_suffix)
        reorient_img(in_img, ref_orient, out_img)


def apply_reorient_to_init(
    df_img: pd.DataFrame, in_dir: str, in_suff: Any, out_dir: str, out_suff: str
) -> None:
    """
    Apply reorientation to init img to all images
    """
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        ref_img = tmp_row.img_path
        img_prefix = tmp_row.img_prefix
        in_img = os.path.join(in_dir, img_prefix + in_suff)
        out_img = os.path.join(out_dir, img_prefix + out_suff)

        reorient_img(in_img, ref_img, out_img)

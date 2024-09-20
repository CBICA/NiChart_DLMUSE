from pathlib import Path
from typing import Union

import nibabel as nib
from nibabel.orientations import axcodes2ornt, ornt_transform
import os
from pathlib import Path

IMG_EXT = ".nii.gz"

def reorient_img(in_img, out_img, ref_orient = 'LPS'):
    '''
    Reorient image
    :param in_img: input image name
    :param out_img: output image name
    :param ref_orient: orientation of output image
    '''
    
    # Read input img
    nii_in = nib.load(in_img)

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

def apply_reorient_img(df_img, out_dir, ref_orient = 'LPS', out_suffix = '_LPS.nii.gz'):
    '''
    Apply reorientation to all images
    '''
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    
    for i, tmp_row in df_img.iterrows():
        in_img = tmp_row.img_path
        out_img = os.path.join(out_dir, tmp_row.img_prefix + out_suffix)
        
        reorient_img(in_img, out_img, ref_orient = ref_orient)

def apply_reorient_to_init(df_img, out_dir, ref_orient = 'LPS', out_suffix = '_LPS.nii.gz'):
    '''
    Apply reorientation to all images
    '''
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for i, tmp_row in df_img.iterrows():
        in_img = tmp_row.img_path
        out_img = os.path.join(out_dir, tmp_row.img_prefix + out_suffix)

        reorient_img(in_img, out_img, ref_orient = ref_orient)

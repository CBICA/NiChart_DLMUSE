import nibabel as nib


###---------mask image-----------
def apply_mask(in_img_name, mask_img_name, out_img_name):
    ## Read input image and mask
    nii_in = nib.load(in_img_name)
    nii_mask = nib.load(mask_img_name)

    img_in = nii_in.get_fdata()
    img_mask = nii_mask.get_fdata()

    ## Mask image
    img_in[img_mask == 0] = 0

    ## Save out image
    nii_out = nib.Nifti1Image(img_in, nii_in.affine, nii_in.header)    
    nii_out.to_filename(out_img_name)

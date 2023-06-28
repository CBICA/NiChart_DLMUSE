import nibabel as nib
from nibabel.orientations import axcodes2ornt, inv_ornt_aff, ornt_transform
from nipype.interfaces.image import Reorient


def apply_combine(in_img_name, icv_img_name, out_img_name):
    '''Combine icv and muse masks.
    '''
    ## Read input images
    nii_in = nib.load(in_img_name)
    nii_icv = nib.load(icv_img_name)

    img_in = nii_in.get_fdata()
    img_icv = nii_icv.get_fdata()

    # Merge masks : Add a new label (1) to MUSE for foreground voxels in ICV that is not in MUSE
    #  this label will mainly represent cortical CSF
    img_in[(img_in==0) & (img_icv>0)] = 1
    
    img_in = img_in.astype(int)

    ## Save out image
    nii_out = nib.Nifti1Image(img_in, nii_in.affine, nii_in.header)    
    nii_out.to_filename(out_img_name)

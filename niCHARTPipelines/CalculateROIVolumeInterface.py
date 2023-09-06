import os
import re
from pathlib import Path

from nipype.interfaces.base import (BaseInterface, BaseInterfaceInputSpec,
                                    Directory, File, TraitedSpec, traits)

from niCHARTPipelines import CalculateROIVolume as calcroivol


###---------utils----------------
def get_basename(in_file, suffix_to_remove, ext_to_remove = ['.nii.gz', '.nii']):
    '''Get file basename 
    - Extracts the base name from the input file
    - Removes a given suffix + file extension
    '''
    ## Get file basename
    out_str = os.path.basename(in_file)

    ## Remove suffix and extension
    for tmp_ext in ext_to_remove:
        out_str, num_repl = re.subn(suffix_to_remove + tmp_ext + '$', '', out_str)
        if num_repl > 0:
            break

    ## Return basename
    if num_repl == 0:
        return None
    return out_str

def remove_common_suffix(list_files):
    '''Detect common suffix to all images in the list and remove it to return a new list
       This list can be used as unique ids for input images 
       (assumption: images have the same common suffix - example:  Subj1_T1_LPS.nii.gz -> Subj1)
    '''
    bnames = list_files    
    if len(list_files) == 1:
        return bnames
    
    common_suff = ''
    num_diff_suff = 1
    while num_diff_suff == 1:
        tmp_suff = [x[-1] for x in bnames]
        num_diff_suff = len(set(tmp_suff))
        if num_diff_suff == 1:
            bnames = [x[0:-1] for x in bnames]
    return bnames

###---------Interface------------
class CalculateROIVolumeInputSpec(BaseInterfaceInputSpec):
    list_single_roi = File(exists=True, mandatory=True, desc='the single roi list file')
    map_derived_roi = File(exists=True, mandatory=True, desc='the derived roi mapping file')
    in_dir = Directory(mandatory=True, desc='the input roi dir')
    in_suff = traits.Str(mandatory=False, desc='the in roi image suffix')
    out_dir = Directory(mandatory=True, desc='the output dir')
    out_img_suff = traits.Str(mandatory=False, desc='the output img suffix')
    out_csv_suff = traits.Str(mandatory=False, desc='the output csv suffix')
    # is_extract_roi_masks = traits.Int(mandatory=False, desc='whether to extract roi masks')
    is_extract_roi_masks = 1
    out_dir_roi_masks = Directory(mandatory=False, desc='the output dir for individual rois')

class CalculateROIVolumeOutputSpec(TraitedSpec):
    out_dir = File(desc='the output image')

class CalculateROIVolume(BaseInterface):
    input_spec = CalculateROIVolumeInputSpec
    output_spec = CalculateROIVolumeOutputSpec

    def _run_interface(self, runtime):
        
        img_ext_type = '.nii.gz'
        out_ext_type = '.csv'

        # Set input args
        if not self.inputs.in_suff:
            self.inputs.in_suff = ''
        if not self.inputs.out_img_suff:
            self.inputs.out_img_suff = '_DLMUSE'
        if not self.inputs.out_csv_suff:
            self.inputs.out_csv_suff = '_DLMUSE_Volumes'
        
        ## Create output folder
        if not os.path.exists(self.inputs.out_dir):
            os.makedirs(self.inputs.out_dir)
        
        ## Create output folder for individual ROI masks
        if self.inputs.is_extract_roi_masks == 1:
            if not os.path.exists(self.inputs.out_dir_roi_masks):
                os.makedirs(self.inputs.out_dir_roi_masks)

        ## Get a list of input images
        infiles = Path(self.inputs.in_dir).glob('*' + self.inputs.in_suff + img_ext_type)
        in_img_names = []
        bnames = []
        for in_img_name in infiles:
            in_img_names.append(in_img_name)
            bnames.append(get_basename(in_img_name, self.inputs.in_suff, [img_ext_type]))
              
        ## Detect scan ids
        scan_ids = remove_common_suffix(bnames)
                
        ## Iterate for each image
        for i, in_bname in enumerate(bnames):
            
            ## Get args
            in_img_name = in_img_names[i]
            scan_id = scan_ids[i]
            out_img_name = os.path.join(self.inputs.out_dir,
                                        in_bname + self.inputs.out_img_suff + img_ext_type)
            out_csv_name = os.path.join(self.inputs.out_dir,
                                        in_bname + self.inputs.out_csv_suff + out_ext_type)

            calcroivol.create_roi_csv(scan_id,
                                      in_img_name,
                                      self.inputs.list_single_roi,
                                      self.inputs.map_derived_roi,
                                      out_img_name,
                                      out_csv_name)
            
            ## If the flag is set, create individual ROI masks
            out_img_pref = os.path.join(self.inputs.out_dir_roi_masks, 
                                        in_bname + self.inputs.out_img_suff)
            if self.inputs.is_extract_roi_masks == 1:
                calcroivol.extract_roi_masks(in_img_name,
                                             self.inputs.map_derived_roi,
                                             out_img_pref)
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_dir': self.inputs.out_dir}

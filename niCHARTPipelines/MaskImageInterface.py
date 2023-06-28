import os
import re
from pathlib import Path

from nipype.interfaces.base import (BaseInterface, BaseInterfaceInputSpec,
                                    Directory, File, TraitedSpec, traits)

from niCHARTPipelines import MaskImage as masker


###---------Interface------------
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

class MaskImageInputSpec(BaseInterfaceInputSpec):
    in_dir = Directory(mandatory=True, desc='the input dir')
    in_suff = traits.Str(mandatory=False, desc='the input image suffix')
    mask_dir = Directory(mandatory=True, desc='the mask img directory')
    mask_suff = traits.Str(mandatory=False, desc='the mask image suffix')
    out_dir = Directory(mandatory=True, desc='the output dir') 
    out_suff = traits.Str(mandatory=False, desc='the out image suffix')

class MaskImageOutputSpec(TraitedSpec):
    out_dir = File(desc='the output image')

class MaskImage(BaseInterface):
    input_spec = MaskImageInputSpec
    output_spec = MaskImageOutputSpec

    def _run_interface(self, runtime):

        img_ext_type = '.nii.gz'

        # Set input args
        if not self.inputs.in_suff:
            self.inputs.in_suff = ''
        if not self.inputs.mask_suff:
            self.inputs.mask_suff = ''
        if not self.inputs.out_suff:
            self.inputs.out_suff = '_masked'
        
        ## Create output folder
        if not os.path.exists(self.inputs.out_dir):
            os.makedirs(self.inputs.out_dir)
        
        infiles = Path(self.inputs.in_dir).glob('*' + self.inputs.in_suff + img_ext_type)
        
        for in_img_name in infiles:
            
            ## Get args
            in_bname = get_basename(in_img_name, self.inputs.in_suff, [img_ext_type])
            mask_img_name = os.path.join(self.inputs.mask_dir,
                                         in_bname + self.inputs.mask_suff + img_ext_type)
            out_img_name = os.path.join(self.inputs.out_dir,
                                        in_bname + self.inputs.out_suff + img_ext_type)

            ## Call the main function
            masker.apply_mask(in_img_name, mask_img_name, out_img_name)

        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_dir': self.inputs.out_dir}

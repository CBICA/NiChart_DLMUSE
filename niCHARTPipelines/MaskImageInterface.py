from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, Directory, TraitedSpec
import MaskImage as masker
from pathlib import Path
import os

###---------utils----------------
def get_file_basename_without_extension(filepath):
    return os.path.basename(filepath).split('.', 1)[0]

def get_split_filename(basename):
    what_i_want, the_rest = basename.rsplit("_", 1)
    return what_i_want

###---------Interface------------

class MaskImageInputSpec(BaseInterfaceInputSpec):
    in_dir = Directory(mandatory=True, desc='the input dir')
    out_dir = Directory(mandatory=True, desc='the output dir') 
    mask_dir =Directory(desc='the input mask directory')

class MaskImageOutputSpec(TraitedSpec):
    out_dir = File(desc='the output image')

class MaskImage(BaseInterface):
    input_spec = MaskImageInputSpec
    output_spec = MaskImageOutputSpec

    def _run_interface(self, runtime):

        # Call our python code here:
        print('in-dir: ', self.inputs.in_dir)
        infiles = Path(self.inputs.in_dir).glob('*.nii.gz')
        maskfiles = Path(self.inputs.mask_dir).glob('*.nii.gz')

        for in_file in infiles:
          basename_without_ext = get_file_basename_without_extension(in_file)
          in_file_split_name_ = get_split_filename(basename_without_ext)

          for mask_file in maskfiles:
            mask_file_name_without_ext = get_file_basename_without_extension(mask_file)

            ##TODO compare basenames only. make sure that DLICV output names match input names first
            if(in_file_split_name_ == mask_file_name_without_ext):
                out_file = os.path.join(self.inputs.out_dir,basename_without_ext) + '.nii.gz'
                masker.apply_mask(
                    in_file,
                    mask_file,
                    out_file
                )
                break
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_dir': self.inputs.out_dir}

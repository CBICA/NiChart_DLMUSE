from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, Directory, TraitedSpec
import MaskImage as masker
from pathlib import Path
import os

###---------Interface------------

class MaskImageInputSpec(BaseInterfaceInputSpec):
    #in_file = File(exists=True, mandatory=True, desc='the input image')
    in_dir = Directory(mandatory=True, desc='the input dir')
    #out_file = File(mandatory=True, desc='the output image')
    out_dir = Directory(mandatory=True, desc='the output dir') 
    #mask_file = File(desc='the input mask')
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

        # if(len(infiles) != len(maskfiles)):
        #     print('something is not right! Your input files and DLICV output file count does not match, Exiting.' )
        #     exit()
        print(maskfiles)
        print(infiles)
        for in_file in infiles:
          print('in_file: ', in_file)
          for mask_file in maskfiles:
            print('mask_file: ', mask_file)
            if(in_file == mask_file):
                out_file = os.path.join(self.inputs.out_dir,in_file)
                print('out-file: ',out_file)
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

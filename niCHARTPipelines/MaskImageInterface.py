from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, TraitedSpec
from . import MaskImage as masker

###---------Interface------------

class MaskImageInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc='the input image')
    out_file = File(mandatory=True, desc='the output image') 
    mask_file = File(desc='the input mask')

class MaskImageOutputSpec(TraitedSpec):
    out_file = File(desc='the output image')

class MaskImage(BaseInterface):
    input_spec = MaskImageInputSpec
    output_spec = MaskImageOutputSpec

    def _run_interface(self, runtime):

        # Call our python code here:
        masker.apply_mask(
            self.inputs.in_file,
            self.inputs.mask_file,
            self.inputs.out_file
        )
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_file': self.inputs.out_file}

from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, TraitedSpec, traits
from . import ROIRelabeler as relabeler

###---------Interface------------

class ROIRelabelInputSpec(BaseInterfaceInputSpec):
    in_file = File(exists=True, mandatory=True, desc='the input mask image')
    map_csv_file = File(exists=True, mandatory=True, desc='the map csv file')
    out_file = File(mandatory=True, desc='the output csv file') 

class ROIRelabelOutputSpec(TraitedSpec):
    out_file = File(desc='the output csv file')

class ROIRelabelInterface(BaseInterface):
    input_spec = ROIRelabelInputSpec
    output_spec = ROIRelabelOutputSpec

    def _run_interface(self, runtime):

        label_from = 'IndexConsecutive'
        label_to = 'IndexMUSE'

        # Call our python code here:
        relabeler.relabel_roi_img(
            self.inputs.in_file,
            self.inputs.map_csv_file,
            label_from,
            label_to,
            self.inputs.out_file
        )
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_file': self.inputs.out_file}

from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, TraitedSpec, traits
from . import ROIVolumeCalculator as volCalculator

###---------Interface------------

class CalculateROIVolumeInputSpec(BaseInterfaceInputSpec):
    mask_file = File(exists=True, mandatory=True, desc='the input mask image')
    map_csv_file = File(exists=True, mandatory=True, desc='the map csv file')
    scan_id = traits.Str(mandatory=True,desc='scan ID')
    out_file = File(mandatory=True, desc='the output csv file') 

class CalculateROIVolumeOutputSpec(TraitedSpec):
    out_file = File(desc='the output csv file')

class CalculateROIVolume(BaseInterface):
    input_spec = CalculateROIVolumeInputSpec
    output_spec = CalculateROIVolumeOutputSpec

    def _run_interface(self, runtime):

        # Call our python code here:
        volCalculator.calculate_volume(
            self.inputs.mask_file,
            self.inputs.map_csv_file,
            self.inputs.scan_id,
            self.inputs.out_file
        )
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_file': self.inputs.out_file}

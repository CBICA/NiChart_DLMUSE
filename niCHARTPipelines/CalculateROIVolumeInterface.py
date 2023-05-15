from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, Directory, TraitedSpec, traits
import ROIVolumeCalculator as volCalculator
from pathlib import Path
import os

###---------utils----------------
def get_file_basename_without_extension(filepath):
    return os.path.basename(filepath).split('.', 1)[0]

###---------Interface------------

class CalculateROIVolumeInputSpec(BaseInterfaceInputSpec):
    map_csv_file = File(exists=True, mandatory=True, desc='the map csv file')
    scan_id = traits.Str(mandatory=True,desc='scan ID')
    in_dir = Directory(mandatory=True, desc='the input dir')
    out_dir = Directory(mandatory=True, desc='the output dir') 

class CalculateROIVolumeOutputSpec(TraitedSpec):
    out_dir = File(desc='the output image')

class CalculateROIVolume(BaseInterface):
    input_spec = CalculateROIVolumeInputSpec
    output_spec = CalculateROIVolumeOutputSpec

    def _run_interface(self, runtime):

        # Call our python code here:
        infiles = Path(self.inputs.in_dir).glob('*.nii.gz')
        for in_file in infiles:
          basename_without_ext = get_file_basename_without_extension(in_file)
          out_file = os.path.join(self.inputs.out_dir,basename_without_ext) + '.csv'
          
          volCalculator.calculate_volume(
              in_file,
              self.inputs.map_csv_file,
              self.inputs.scan_id,
              out_file
          )
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_dir': self.inputs.out_dir}

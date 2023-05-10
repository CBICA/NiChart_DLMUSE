from nipype.interfaces.base import BaseInterfaceInputSpec, BaseInterface, File, Directory, TraitedSpec, traits
from pathlib import Path
import ROIRelabeler as relabeler
import os

###---------Interface------------

class ROIRelabelInputSpec(BaseInterfaceInputSpec):
    #in_file = File(exists=True, mandatory=True, desc='the input mask image')
    map_csv_file = File(exists=True, mandatory=True, desc='the map csv file')
    #out_file = File(mandatory=True, desc='the output csv file')
    in_dir = Directory(mandatory=True, desc='the input dir')
    out_dir = Directory(mandatory=True, desc='the output dir') 

class ROIRelabelOutputSpec(TraitedSpec):
    #out_file = File(desc='the output csv file')
    out_dir = File(desc='the output image')

class ROIRelabel(BaseInterface):
    input_spec = ROIRelabelInputSpec
    output_spec = ROIRelabelOutputSpec

    def _run_interface(self, runtime):

        # Call our python code here:
        label_from = 'IndexConsecutive'
        label_to = 'IndexMUSE'
        
        infiles = Path(self.inputs.in_dir).glob('*.nii.gz')

        for in_file in infiles:
          basename = os.path.basename(in_file)
          out_file = os.path.join(self.inputs.out_dir,basename)

          relabeler.relabel_roi_img(
              in_file,
              self.inputs.map_csv_file,
              label_from,
              label_to,
              out_file
          )
        # And we are done
        return runtime

    def _list_outputs(self):
        return {'out_dir': self.inputs.out_dir}
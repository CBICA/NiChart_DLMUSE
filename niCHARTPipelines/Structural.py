from nipype import Node, Workflow
from pathlib import Path

import DeepMRSegInterface
import MaskImageInterface
import CalculateROIVolumeInterface

def run_structural_pipeline(inImg,DLICVmdl,DLMUSEmdl,outImg):
    # Create DLICV Node
    dlicv = Node(DeepMRSegInterface.DeepMRSegInference(), name='dlicv')
    dlicv.inputs.in_file = Path(inImg)
    dlicv.inputs.mdl_dir1 = '/nichart/models/DLICV/LPS'
    dlicv.inputs.out_file = '/nichart/data/F1/dlicv-nipype.nii.gz'
    dlicv.inputs.batch_size = 4
    dlicv.inputs.nJobs = 1

    # Create Apply Mask Node
    maskImage = Node(MaskImageInterface.MaskImage(), name='maskImage')
    maskImage.inputs.in_file = Path(inImg)
    maskImage.inputs.out_file = '/nichart/data/F1/masked4.nii.gz'

    # Create MUSE Node
    muse = Node(DeepMRSegInterface.DeepMRSegInference(), name='muse')
    muse.inputs.mdl_dir1 = '/nichart/models/MUSE/LPS'
    muse.inputs.mdl_dir2 = '/nichart/models/MUSE/PSL'
    muse.inputs.mdl_dir3 = '/nichart/models/MUSE/SLP'
    muse.inputs.out_file = '/nichart/data/F1/muse-nipype.nii.gz'
    muse.inputs.batch_size = 4
    muse.inputs.nJobs = 1

    # Create roi csv creation Node
    roi_csv = Node(CalculateROIVolumeInterface.CalculateROIVolume(), name='roi-volume-csv')
    roi_csv.inputs.map_csv_file = '/nichart/csv/MUSE_DerivedROIs_Mappings.csv'
    roi_csv.inputs.scan_id = 'AABB'
    roi_csv.inputs.out_file = '/nichart/data/F1/muse_rois.csv'

    # Workflow
    wf = Workflow(name="structural", base_dir="/nichart/working_dir")
    wf.connect(dlicv, "out_file", maskImage, "mask_file")
    wf.connect(maskImage, "out_file", muse, "in_file")
    wf.connect(muse,"out_file", roi_csv, "mask_file")

    wf.base_dir = "/nichart/working_dir"
    wf.run()
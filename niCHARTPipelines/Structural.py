from nipype import Node, Workflow
from pathlib import Path
import os,  shutil

# from . import DeepMRSegInterface
from niCHARTPipelines import nnUNetInterface
from niCHARTPipelines import MaskImageInterface
from niCHARTPipelines import ROIRelabelInterface
from niCHARTPipelines import CalculateROIVolumeInterface

def run_structural_pipeline(inDir,
                            DLICVmdl_path,
                            DLMUSEmdl_path,
                            outDir, 
                            MuseMappingFile,
                            scanID,
                            roiMappingsFile,
                            nnUNet_raw_data_base=None,
                            nnUNet_preprocessed=None,
                            results_folder=None,
                            DLICV_task=None,
                            DLMUSE_task=None,
                            DLICV_fold=None,
                            DLMUSE_fold=None,
                            all_in_gpu='None'):
    
    print("Entering function")
    outDir = os.path.abspath(os.path.dirname(outDir))
    inDir = os.path.abspath(os.path.dirname(inDir))
    
    if nnUNet_raw_data_base:
        os.environ['nnUNet_raw_data_base'] = os.path.abspath(nnUNet_raw_data_base) + '/'
    if nnUNet_preprocessed:
        os.environ['nnUNet_preprocessed'] = os.path.abspath(nnUNet_preprocessed) + '/'
    # Assuming that both DLICV and DLMUSE models are in the same folder.
    # Example:
    # 
    # /path/to/nnUNetTrainedModels/nnUNet/Task_001/
    # /path/to/nnUNetTrainedModels/nnUNet/Task_002/
    # 
    # This is not needed if the environment variable is already set.
    if results_folder:
        os.environ['RESULTS_FOLDER'] = os.path.abspath(results_folder) + '/'

    # Create DLICV Node
    # os.environ['RESULTS_FOLDER'] = str(Path(DLICVmdl_path))
    dlicv = Node(nnUNetInterface.nnUNetInference(), name='dlicv')
    dlicv.inputs.in_dir = Path(inDir)
    dlicv.inputs.out_dir = os.path.join(outDir,'dlicv_out')
    dlicv.inputs.f_val = 1
    if DLICV_fold:
        dlicv.inputs.f_val = DLICV_fold
    dlicv.inputs.t_val = 802
    if DLICV_task:
        dlicv.inputs.t_val = DLICV_task
    dlicv.inputs.m_val = "3d_fullres"
    dlicv.inputs.all_in_gpu = all_in_gpu
    dlicv.inputs.tr_val = "nnUNetTrainerV2"
    if os.path.exists(dlicv.inputs.out_dir):
        shutil.rmtree(dlicv.inputs.out_dir)
    os.mkdir(dlicv.inputs.out_dir)
    print('outdir: ', dlicv.inputs.out_dir)
    print("DLICV done")

    # Create Apply Mask Node
    maskImage = Node(MaskImageInterface.MaskImage(), name='maskImage')
    maskImage.inputs.in_dir = Path(inDir)
    maskImage.inputs.out_dir = os.path.join(outDir,'masked_out')
    if os.path.exists(maskImage.inputs.out_dir):
        shutil.rmtree(maskImage.inputs.out_dir)
    os.mkdir(maskImage.inputs.out_dir)

    print('mask-dir: ', maskImage.inputs.out_dir)
    print("masking done")
    
    # Create MUSE Node
    # os.environ['RESULTS_FOLDER'] = str(Path(DLMUSEmdl_path))
    muse = Node(nnUNetInterface.nnUNetInference(), name='muse')
    muse.inputs.out_dir = os.path.join(outDir,'muse_out')
    muse.inputs.f_val = 2
    if DLMUSE_fold:
        muse.inputs.f_val = DLMUSE_fold
    muse.inputs.t_val = 903
    if DLMUSE_task:
        muse.inputs.t_val = DLMUSE_task
    muse.inputs.m_val = "3d_fullres"
    muse.inputs.tr_val = "nnUNetTrainerV2_noMirroring"
    muse.inputs.all_in_gpu = all_in_gpu
    muse.inputs.disable_tta = True
    if os.path.exists(muse.inputs.out_dir):
        shutil.rmtree(muse.inputs.out_dir)
    os.mkdir(muse.inputs.out_dir)
    print('outdir: ', muse.inputs.out_dir)
    print("MUSE done")
     
    #create muse relabel Node
    relabel = Node(ROIRelabelInterface.ROIRelabel(), name='relabel')
    relabel.inputs.map_csv_file = os.path.abspath(MuseMappingFile)
    relabel.inputs.out_dir = os.path.join(outDir,'relabeled_out')
    if os.path.exists(relabel.inputs.out_dir):
        shutil.rmtree(relabel.inputs.out_dir)
    os.mkdir(relabel.inputs.out_dir)

    print('relabeled-dir: ', relabel.inputs.out_dir)
    print("relabeling done")

    # Create roi csv creation Node
    roi_csv = Node(CalculateROIVolumeInterface.CalculateROIVolume(), name='roi-volume-csv')
    roi_csv.inputs.map_csv_file = os.path.abspath(roiMappingsFile)
    roi_csv.inputs.scan_id = str(scanID)
    roi_csv.inputs.out_dir = os.path.join(outDir,'csv_out')
    if os.path.exists(roi_csv.inputs.out_dir):
        shutil.rmtree(roi_csv.inputs.out_dir)
    os.mkdir(roi_csv.inputs.out_dir)

    #create working dir in output dir for now
    basedir = os.path.join(outDir,'working_dir')
    if os.path.exists(basedir):
        shutil.rmtree(basedir)

    os.makedirs(basedir, exist_ok=True)

    # Workflow
    wf = Workflow(name="structural", base_dir=basedir)
    wf.connect(dlicv, "out_dir", maskImage, "mask_dir")
    wf.connect(maskImage, "out_dir", muse, "in_dir")
    wf.connect(muse, "out_dir", relabel, "in_dir")
    wf.connect(relabel,"out_dir", roi_csv, "in_dir")
    
    wf.base_dir = basedir
    wf.run()
    print("Exiting function")

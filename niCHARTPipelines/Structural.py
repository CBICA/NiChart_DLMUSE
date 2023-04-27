from nipype import Node, Workflow
from pathlib import Path
import os,  shutil

# from . import DeepMRSegInterface
import nnUNetInterface
import MaskImageInterface
# from . import CalculateROIVolumeInterface

#def run_structural_pipeline(inImg,DLICVmdl,DLMUSEmdl,outFile,scanID,roiMappingsFile):
def run_structural_pipeline(inImg,DLICVmdl,outFile):
    print("Entering function")
    outDir = os.path.dirname(outFile)
    inDir = os.path.dirname(inImg)

    # Create MUSE Node
    dlicv = Node(nnUNetInterface.nnUNetInference(), name='dlicv')
    dlicv.inputs.in_dir = Path(inDir)
    #dlicv.inputs.mdl_dir = Path(DLICVmdl)
    os.environ['RESULTS_FOLDER'] = str(Path(DLICVmdl))
    dlicv.inputs.f_val = 1
    dlicv.inputs.t_val = 802
    dlicv.inputs.m_val = "3d_fullres"
    #dlicv.gpu_val = True
    #dlicv.inputs.out_dir = Path(outDir)
    dlicv.inputs.out_dir = os.path.join(outDir,'dlicv_out')
    if os.path.exists(dlicv.inputs.out_dir):
        shutil.rmtree(dlicv.inputs.out_dir)
    os.mkdir(dlicv.inputs.out_dir)
    #dlicv.run()
    print('outdir: ', dlicv.inputs.out_dir)
    print("DLICV done")
    # Create DLICV Node
    # dlicv = Node(DeepMRSegInterface.DeepMRSegInference(), name='dlicv')
    # dlicv.inputs.in_file = Path(inImg)
    # lps_mdl_path = os.path.join(DLICVmdl,'LPS')
    # if(os.path.isdir(lps_mdl_path)):
    #     dlicv.inputs.mdl_dir1 = lps_mdl_path
    # dlicv.inputs.out_file = os.path.join(outDir,'dlicv.nii.gz')
    # dlicv.inputs.batch_size = 4
    # dlicv.inputs.nJobs = 1

    # Create Apply Mask Node
    maskImage = Node(MaskImageInterface.MaskImage(), name='maskImage')
    #maskImage.inputs.in_dir = os.path.join(outDir,'dlicv_out')
    maskImage.inputs.in_dir = Path(inDir)
    maskImage.inputs.out_dir = os.path.join(outDir,'masked_out')
    if os.path.exists(maskImage.inputs.out_dir):
        shutil.rmtree(maskImage.inputs.out_dir)
    os.mkdir(maskImage.inputs.out_dir)

    print('mask-dir: ', maskImage.inputs.out_dir)
    print("masking done")
    # Create MUSE Node
    # muse = Node(DeepMRSegInterface.DeepMRSegInference(), name='muse')
    # muse_lps_mdl_path = os.path.join(DLMUSEmdl,'LPS')
    # #muse_psl_mdl_path = os.path.join(DLMUSEmdl,'PSL')      ## We run all in one orientation in tests
    # #muse_slp_mdl_path = os.path.join(DLMUSEmdl,'SLP')
    # if(os.path.isdir(muse_lps_mdl_path)):
    #     muse.inputs.mdl_dir1 = muse_lps_mdl_path
    # #if(os.path.isdir(muse_psl_mdl_path)):
    #     #muse.inputs.mdl_dir2 = muse_psl_mdl_path
    # #if(os.path.isdir(muse_slp_mdl_path)):
    #     #muse.inputs.mdl_dir3 = muse_slp_mdl_path        
    # muse.inputs.out_file = os.path.join(outDir,'muse.nii.gz')
    # muse.inputs.batch_size = 4
    # muse.inputs.nJobs = 1

    # Create roi csv creation Node
    # roi_csv = Node(CalculateROIVolumeInterface.CalculateROIVolume(), name='roi-volume-csv')
    # roi_csv.inputs.map_csv_file = Path(roiMappingsFile)
    # roi_csv.inputs.scan_id = str(scanID)
    # roi_csv.inputs.out_file = Path(outFile)

    #create working dir in output dir for now
    basedir = os.path.join(outDir,'working_dir')
    if os.path.exists(basedir):
        shutil.rmtree(basedir)

    os.makedirs(basedir, exist_ok=True)

    # Workflow
    wf = Workflow(name="structural", base_dir=basedir)
    wf.connect(dlicv, "out_dir", maskImage, "mask_dir")
    # wf.connect(maskImage, "out_file", muse, "in_file")
    # wf.connect(muse,"out_file", roi_csv, "mask_file")
    
    #wf.write_graph(dotfilename='graph.dot', graph2use='hierarchical', format='png', simple_form=True)

    wf.base_dir = basedir
    wf.run()
    print("Exiting function")

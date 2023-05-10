from nipype import Node, Workflow
from pathlib import Path
import os,  shutil

# from . import DeepMRSegInterface
import nnUNetInterface
import MaskImageInterface
import ROIRelabelInterface
import CalculateROIVolumeInterface

#def run_structural_pipeline(inImg,DLICVmdl,DLMUSEmdl,outFile,scanID,roiMappingsFile):
def run_structural_pipeline(inImg,DLICVmdl,DLMUSEmdl,outFile, MuseMappingFile,scanID,roiMappingsFile):
    print("Entering function")
    outDir = os.path.dirname(outFile)
    inDir = os.path.dirname(inImg)

    # Create DLICV Node
    dlicv = Node(nnUNetInterface.nnUNetInference(), name='dlicv')
    dlicv.inputs.in_dir = Path(inDir)
    dlicv.inputs.mdl_dir = str(DLICVmdl)
    #os.environ['RESULTS_FOLDER'] = str(Path(DLICVmdl))
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
    muse = Node(nnUNetInterface.nnUNetInference(), name='muse')
    muse.inputs.mdl_dir = str(DLMUSEmdl)
    #os.environ['RESULTS_FOLDER'] = str(Path(DLMUSEmdl))
    muse.inputs.f_val = 0#2
    muse.inputs.t_val = 803#903
    muse.inputs.m_val = "3d_fullres"
    muse.inputs.out_dir = os.path.join(outDir,'muse_out')
    if os.path.exists(muse.inputs.out_dir):
        shutil.rmtree(muse.inputs.out_dir)
    os.mkdir(muse.inputs.out_dir)
    print('outdir: ', muse.inputs.out_dir)
    print("MUSE done")
     
    #create muse relabel Node
    relabel = Node(ROIRelabelInterface.ROIRelabel(), name='relabel')
    #relabel.inputs.in_dir = Path(inDir)
    relabel.inputs.map_csv_file = Path(MuseMappingFile)
    relabel.inputs.out_dir = os.path.join(outDir,'relabeled_out')
    if os.path.exists(relabel.inputs.out_dir):
        shutil.rmtree(relabel.inputs.out_dir)
    os.mkdir(relabel.inputs.out_dir)

    print('relabeled-dir: ', relabel.inputs.out_dir)
    print("relabeling done")

    # Create roi csv creation Node
    roi_csv = Node(CalculateROIVolumeInterface.CalculateROIVolume(), name='roi-volume-csv')
    roi_csv.inputs.map_csv_file = Path(roiMappingsFile)
    roi_csv.inputs.scan_id = str(scanID)
    #roi_csv.inputs.out_file = Path(outFile)
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
    
    #wf.write_graph(dotfilename='graph.dot', graph2use='hierarchical', format='png', simple_form=True)

    wf.base_dir = basedir
    wf.run()
    print("Exiting function")

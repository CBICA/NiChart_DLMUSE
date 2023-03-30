# niCHARTPipelines


# Instructions
1) create a new conda env
```
conda create --name sMRI python=3.8
conda activate sMRI
```

2) Clone and install niCHARTPipelines
```
git clone  https://github.com/CBICA/niCHARTPipelines.git
cd niCHARTPipelines
pip install .

```

3) Run niCHARTPipelines. Example usage below
```
cd niCHARTPipelines/niCHARTPipelines
./test1_Tmp.sh

niCHARTPipelines --pipelineType structural --inImg $t1 --DLICVmdl $mdlDLICV --DLMUSEmdl $mdlMUSE --scanID $mrid --derivedROIMappingsFile $rois --outFile $outcsv
```

# Singularity/Apptainer-based build and installation

Singularity and Apptainer images can be built for niCHARTPipelines, allowing for frozen versions of the pipeline and easier installation for end-users.
Note that the Singularity project recently underwent a rename to "Apptainer", with a commercial fork still existing under the name "Singularity" (confusing!).
Please note that while for now these two versions are largely identical, future versions may diverge. It is recommended to use the AppTainer distribution. For now, these instructions apply to either. 

First install [the container engine](https://apptainer.org/admin-docs/3.8/installation.html). 
Then, from the cloned project repository, run:
```
singularity build nichartpipelines.sif singularity.def
```
This will take some time, but will build a containerized version of your current repo. Be aware that this includes any local changes!
The nichartpipelines.sif file can be distributed via direct download, or pushed to a container registry that accepts SIF images.

Then, anybody with the Singularity/Apptainer engine can run the image easily:
```
singularity run --nv nichartpipelines.sif [options go here]
```
The --nv option is required to allow niCHARTPipelines to use the host machine's GPU.

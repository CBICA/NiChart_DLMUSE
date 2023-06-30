# niCHARTPipelines

## Installation

1. create a new conda env

    ```bash
    conda create --name NCP python=3.8
    conda activate NCP
    ```

2. Clone and install niCHARTPipelines

    ```bash
    git clone  https://github.com/CBICA/niCHARTPipelines.git
    cd niCHARTPipelines
    pip install .

    ```

3. Run niCHARTPipelines. Example usage below

    ```bash
    niCHARTPipelines --indir                     /path/to/input     \
                     --outdir                    /path/to/output    \
                     --pipelinetype structural                      \
                     --derived_ROI_mappings_file /path/to/file.csv  \
                     --MUSE_ROI_mappings_file    /path/to/file.csv  \
                     --nnUNet_raw_data_base      /path/to/folder/   \
                     --nnUNet_preprocessed       /path/to/folder/   \
                     --model_folder              /path/to/folder/   \
                     --all_in_gpu True                              \
                     --mode fastest                                 \
                     --disable_tta
    ```

## Singularity/Apptainer-based build and installation

Singularity and Apptainer images can be built for niCHARTPipelines, allowing for frozen versions of the pipeline and easier installation for end-users.
Note that the Singularity project recently underwent a rename to "Apptainer", with a commercial fork still existing under the name "Singularity" (confusing!).
Please note that while for now these two versions are largely identical, future versions may diverge. It is recommended to use the AppTainer distribution. For now, these instructions apply to either.

First install [the container engine](https://apptainer.org/admin-docs/3.8/installation.html).
Then, from the cloned project repository, run:

```bash
singularity build nichartpipelines.sif singularity.def
```

This will take some time, but will build a containerized version of your current repo. Be aware that this includes any local changes!
The nichartpipelines.sif file can be distributed via direct download, or pushed to a container registry that accepts SIF images.

Then, anybody with the Singularity/Apptainer engine can run the image easily:

```bash
singularity run --nv nichartpipelines.sif [options go here]
```

The --nv option is required to allow niCHARTPipelines to use the host machine's GPU.

## Usage

```text
niCHARTPipelines v0.2
ICV calculation, brain segmentation, and ROI extraction pipelines for 
structural MRI data.

required arguments:
    [INDIR]         The filepath of the directory containing the input. The 
    [-i, --indir]   input can be a single .nii.gz (or .nii) file or a  
                    directory containing .nii.gz files (or .nii files). 

    [OUTDIR]        The filepath of the directory where the output will be
    [-o, --outdir]  saved.

    [PIPELINETYPE]  Specify type of pipeline[structural, dti, fmri]. 
    [-p,            Currently only structural pipeline is supported.
    --pipelinetype]

    [DERIVED_ROI_MAPPINGS_FILE]     The filepath of the derived MUSE ROI 
    [--derived_ROI_mappings_file]   mappings file.

    [MUSE_ROI_MAPPINGS_FILE]    The filepath of the MUSE ROI mappings file.
    [--MUSE_ROI_mappings_file]

optional arguments: 
    [DLICVMDL]      The filepath of the DLICV model will be. In case the
    [--DLICVmdl]    model to be used is an nnUNet model, the filepath of
                    the model's parent directory should be given. Example: 
                    /path/to/nnUNetTrainedModels/nnUNet/
    
    [DLMUSEMDL]     The filepath of the DLMUSE model will be. In case the
    [--DLMUSEmdl]   model to be used is an nnUNet model, the filepath of
                    the model's parent directory should be given. Example:
                    /path/to/nnUNetTrainedModels/nnUNet/

    [NNUNET_RAW_DATA_BASE]   The filepath of the base directory where the 
    [--nnUNet_raw_data_base] raw data of are saved.  This argument is only 
                                required if the DLICVMDL and DLMUSEMDL 
                                arguments are corresponding to a  nnUNet model 
                                (v1 needs this currently).

    [NNUNET_PREPROCESSED]   The filepath of the directory where the 
    [--nnUNet_preprocessed] intermediate preprocessed data are saved. This
                            argument is only required if the DLICVMDL and
                            DLMUSEMDL arguments are corresponding to a
                            nnUNet model (v1 needs this currently).

    [MODEL_FOLDER]          THIS IS ONLY NEEDED IF BOTH DLICV AND DLMUSE 
    [--model_folder]        MODELS ARE NNUNET MODELS. The filepath of the
                            directory where the models are saved. The path
                            given should be up to (without) the nnUNet/ 
                            directory. Example:
                            /path/to/nnUNetTrainedModels/          correct
                            /path/to/nnUNetTrainedModels/nnUNet/   wrong
                            This is a temporary fix, and will be removed 
                            in the future. Both models should be saved in 
                            the same directory. Example:
                            /path/to/nnUNetTrainedModels/nnUNet/Task_001/
                            /path/to/nnUNetTrainedModels/nnUNet/Task_002/

    [DLICV_TASK]            The task number of the DLICV model. This 
    [--DLICV_task]          argument is only required if the DLICVMDL is a 
                            nnUNet model.

    [DLMUSE_TASK]           The task number of the DLMUSE model. This 
    [--DLMUSE_task]         argument is only required if the DLMUSEMDL is a 
                            nnUNet model.

    [DLICV_FOLD]            The fold number of the DLICV model. This 
    [--DLICV_fold]          argument is only required if the DLICVMDL is a
                            nnUNet model.

    [DLMUSE_FOLD]           The fold number of the DLMUSE model. This
    [--DLMUSE_fold]         argument is only required if the DLMUSEMDL is a
                            nnUNet model.

    [ALL_IN_GPU]            If this var is set, all the processes will be
    [--all_in_gpu]          done in the GPU. This var is only available if 
                            the DLICVMDL and DLMUSEMDL arguments are 
                            corresponding to a nnUNet model. Either 'True',
                            'False' or 'None'. 

    [DISABLE_TTA]           If this var is given, test-time augmentation  
    [--disable_tta]         will be disabled. This var is only available if 
                            the DLICV and DLMUSE models are nnUNet models. 

    [MODE]                  The mode of the pipeline. Either 'normal' or
    [--mode]                'fastest'. 'normal' mode is the default mode.

    [-h, --help]    Show this help message and exit.
    
    [-V, --version] Show program's version number and exit.

    EXAMPLE USAGE:
    
    niCHARTPipelines --indir                     /path/to/input     \
                     --outdir                    /path/to/output    \
                     --pipelinetype structural                      \
                     --derived_ROI_mappings_file /path/to/file.csv  \
                     --MUSE_ROI_mappings_file    /path/to/file.csv  \
                     --nnUNet_raw_data_base      /path/to/folder/   \
                     --nnUNet_preprocessed       /path/to/folder/   \
                     --model_folder              /path/to/folder/   \
                     --all_in_gpu True                              \
                     --mode fastest                                 \
                     --disable_tta
```

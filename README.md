# niCHARTPipelines

## Overview

niCHARTPipelines is a package that allows the users to process their brain imaging (sMRI) data easily and efficiently.

niCHARTPipelines offers easy ICV (Intra-Cranial Volume) mask extraction, and brain segmentation into ROIs. This is achieved through the [DLICV](https://github.com/CBICA/DLICV) and [DLMUSE](https://github.com/CBICA/DLMUSE) methods. Intermediate step results are saved for easy access to the user.

Given an input (sMRI) scan, niCHARTPipelines extracts the following:

1. ICV mask
2. Brain MUSE ROI segmentation
3. ROI volumes in a .csv format
4. Individual ROI mask (optionally).

This package uses [nnUNet](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1) (version 1) as a basis model architecture for the deep learning parts, [nipype](https://nipy.org/packages/nipype/index.html) for the workflow management and various other [libraries](requirements.txt).

It is available both as an installable package, as well as a [docker container](https://hub.docker.com/repository/docker/aidinisg/nichartpipelines/general). Please see [Installation](#installation) and [Usage](#usage) for more information on how to use it.

## Installation

1. Create a new conda env

    ```bash
    conda create --name NCP python=3.8
    conda activate NCP
    ```

    In one command:

    ```bash
    conda create --name NCP -y python=3.8 && conda activate NCP
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

## Docker/Singularity/Apptainer-based build and installation

The package comes already pre-built as a [docker container](https://hub.docker.com/repository/docker/aidinisg/nichartpipelines/general), for convenience. Please see [Usage](#usage) for more information on how to use it. Alternatively, you can build the docker image locally, like so:

```bash
docker -t nichartpipelines .
```

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

## Usage

Due to the [nnunetv1](https://github.com/MIC-DKFZ/nnUNet/tree/nnunetv1) dependency, the package follows nnUNet's requirements for folder structure and naming conventions. Therefore assuming the following folder structure:

```bash
temp
├── nnUNet_model
│   └── nnUNet
├── nnUNet_out
├── nnUNet_preprocessed
└── nnUNet_raw_database
    └── nnUNet_raw_data
        ├── image1.nii.gz
        ├── image2.nii.gz
        └── image3.nii.gz
```

### As a locally installed package

A complete command would be:

```bash
niCHARTPipelines --indir                     temp/nnUNet_raw_database/nnUNet_raw_data           \
                 --outdir                    temp/nnUNet_out                                    \
                 --pipelinetype              structural                                         \
                 --derived_ROI_mappings_file shared/dicts/MUSE_mapping_derived_rois.csv         \
                 --MUSE_ROI_mappings_file    shared/dicts/MUSE_mapping_consecutive_indices.csv  \
                 --nnUNet_raw_data_base      temp/nnUNet_raw_database                           \
                 --nnUNet_preprocessed       temp/nnUNet_preprocessed                           \
                 --model_folder              temp/nnUNet_model                                  \
                 --all_in_gpu                True                                               \
                 --mode                      fastest                                            \
                 --disable_tta
```

For further explanation please refer to the complete documentation:

```bash
niCHARTPipelines -h
```

### Using the docker container

Using the file structure explained above, an example command using the [docker container](https://hub.docker.com/repository/docker/aidinisg/nichartpipelines/general) is the following:

```bash
docker run -it --rm --gpus all -v ./:/workspace/ aidinisg/nichartpipelines:0.1.7 niCHARTPipelines -i temp/nnUNet_raw_database/nnUNet_raw_data/ -o temp/nnUNet_out/ -p structural --derived_ROI_mappings_file /niCHARTPipelines/shared/dicts/MUSE_mapping_derived_rois.csv --MUSE_ROI_mappings_file /niCHARTPipelines/shared/dicts/MUSE_mapping_consecutive_indices.csv --model_folder temp/nnUNet_model/ --nnUNet_raw_data_base temp/nnUNet_raw_database/ --nnUNet_preprocessed  temp/nnUNet_preprocessed/ --all_in_gpu True --mode fastest --disable_tta
```

### Using the singularity container

```bash
singularity run --nv --containall --bind /path/to/.\:/workspace/ niCHARTPipelines.simg niCHARTPipelines -i /workspace/temp/nnUNet_raw_data_base/nnUNet_raw_data/ -o /workspace/temp/nnUNet_out -p structural --derived_ROI_mappings_file /niCHARTPipelines/shared/dicts/MUSE_mapping_derived_rois.csv --MUSE_ROI_mappings_file /niCHARTPipelines/shared/dicts/MUSE_mapping_consecutive_indices.csv --nnUNet_raw_data_base /workspace/temp/nnUNet_raw_data_base/ --nnUNet_preprocessed /workspace/temp/nnUNet_preprocessed/ --model_folder /workspace/temp/nnUNet_model/ --all_in_gpu True --mode fastest --disable_tta
```

import glob
import logging
import os
import re
from typing import Optional

import numpy as np
import pandas as pd

LIST_IMG_EXT = [".nii", ".nii.gz"]

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pipeline.log", encoding="utf-8", level=logging.DEBUG)


def get_basename(
    in_file: str, suffix_to_remove: str, ext_to_remove: list = LIST_IMG_EXT
) -> str:
    """
    Get file basename
    - Extracts the base name from the input file
    - Removes a given suffix + file extension

    :param in_file: the input file
    :type in_file: str
    :param suffix_to_remove: passed suffix to be removed
    :type suffix_to_remove: str
    :param ext_to_remove: passed extensions to be removed.Default value:
                        ['.nii.gz', '.nii']
    :type ext_to_remove: list

    :return: the string without the suffix + file extension
    :rtype: str
    """
    # Get file basename
    out_str = os.path.basename(in_file)
    num_repl: Optional[int] = None
    # Remove suffix and extension
    for tmp_ext in ext_to_remove:
        out_str, num_repl = re.subn(suffix_to_remove + tmp_ext + "$", "", out_str)
        if num_repl > 0:
            break

    if num_repl == 0:
        return out_str

    return out_str


def remove_common_suffix(list_files: list) -> list:
    """
    Detect common suffix to all images in the list and remove it to return a new list
    This list can be used as unique ids for input images
    (assumption: images have the same common suffix - example:  Subj1_T1_LPS.nii.gz -> Subj1)

    :param list_files: a list with all the filenames
    :type list_files: list

    :return: a list with the removed common suffix files
    :rtype: list

    """

    bnames = list_files
    if len(list_files) == 1:
        return bnames

    num_diff_suff = 1
    while num_diff_suff == 1:
        tmp_suff = [x[-1] for x in bnames]
        num_diff_suff = len(set(tmp_suff))
        if num_diff_suff == 1:
            bnames = [x[0:-1] for x in bnames]
    return bnames


def make_img_list(in_data: str) -> pd.DataFrame:
    """
    Make a list of images
    """

    # Read list of input images
    nii_files = []

    #   case: input data is a folder with images
    if os.path.isdir(in_data):
        in_data = os.path.abspath(in_data)
        for tmp_ext in LIST_IMG_EXT:
            nii_files.extend(glob.glob(os.path.join(in_data, "*" + tmp_ext)))

    #   case: input data is a single image file
    elif in_data.endswith(".nii") or in_data.endswith(".nii.gz"):
        nii_files = [os.path.abspath(in_data)]

    #   case: input data is a list with image names (full path, one file in each line)
    else:
        with open(in_data, "r") as file:
            lines = file.readlines()
            nii_files = []
            for line in lines:
                is_nifti = False
                for tmp_ext in LIST_IMG_EXT:
                    if line.strip().endswith(tmp_ext):
                        is_nifti = True
                if is_nifti is True:
                    nii_files.append(os.path.abspath(line.strip()))

    nii_files = np.array(nii_files)

    # Check if images exist
    if len(nii_files) > 0:
        flag = np.zeros(nii_files.shape[0])  # type:ignore
        for i, ftmp in enumerate(nii_files):
            if os.path.exists(ftmp):
                flag[i] = 1
        nii_files = nii_files[flag == 1]

    logging.info(
        f"Detected {nii_files.shape[0]} images. Valid images are {len(nii_files)}..."  # type:ignore
    )
    # Create a dataframe
    df_out = pd.DataFrame(data=nii_files, columns=["img_path"])

    # Detect file info
    bnames = [os.path.basename(filename) for filename in nii_files]
    bnames_noext = [get_basename(filename, "", LIST_IMG_EXT) for filename in bnames]
    mrids = remove_common_suffix(bnames_noext)

    # Extend the dataframe with file info
    df_out = df_out.reindex(["MRID", "img_path", "img_base", "img_prefix"], axis=1)
    df_out["MRID"] = mrids
    df_out["img_base"] = bnames
    df_out["img_prefix"] = bnames_noext

    # Return out dataframe
    return df_out


def get_bids_prefix(filename: str, folder: bool = False) -> str:
    """
    Returns the prefix of a bids file
    """
    checker = "-" if folder is False else "_"
    prefix = ""
    idx = 0
    char = filename[idx]
    while char != checker:
        prefix += char
        idx += 1
        if idx >= len(filename):
            break
        char = filename[idx]

    return prefix


def dir_size(in_dir: str) -> int:
    """
    Returns the number of images the user passed
    """
    size = 0
    for path in os.listdir(in_dir):
        if os.path.isfile(os.path.join(in_dir, path)):
            size += 1

    return size


def dir_foldercount(in_dir: str) -> int:
    """
    Returns the number of subfolders that the input directory has
    """

    size = 0
    for path in os.listdir(in_dir):
        if os.path.isdir(os.path.join(in_dir, path)):
            size += 1

    return size


def collect_T1(in_dir: str, out_dir: str) -> None:
    """
    This function collects all the raw T1 images from the passed BIDS input dir and
    it creates a temporary folder that will act as a generic dataset with only T1 images
    """
    if os.path.isdir("raw_temp_T1") and len(os.listdir("raw_temp_T1")):
        os.system("rm -r raw_temp_T1/*")
    elif not os.path.isdir("raw_temp_T1"):
        # create the raw_temp_T1 folder that will host all the T1 images
        os.system("mkdir raw_temp_T1")

    os.system(f"cp -r {in_dir}/* {out_dir}/")

    total_subs = dir_foldercount(in_dir)
    accepted_subfolders = []
    for i in range(total_subs):
        if i < 9:
            accepted_subfolders.append(f"sub-0{i + 1}")
        else:
            accepted_subfolders.append(f"sub-{i + 1}")

    for root, subs, files in os.walk(in_dir):
        for sub in subs:
            if sub in accepted_subfolders:
                os.system(f"cp {os.path.join(in_dir, sub)}/anat/* raw_temp_T1/")


def merge_bids_output_data(out_data: str) -> None:
    """
    Move all the images on the s5_relabeled subfolder to the subfolder of their prefix
    """
    for split in os.listdir(out_data):
        if get_bids_prefix(split, True) == "split":
            s5_relabeled_dir = os.path.join(
                out_data, split, "temp_working_dir", "s5_relabeled"
            )
            for img in os.listdir(s5_relabeled_dir):
                os.system(
                    f"mv {s5_relabeled_dir}/{img} {out_data}/{get_bids_prefix(img, True)}/anat/"
                )


def split_data(in_dir: str, N: int) -> list:
    """
    Splits the input data directory into subfolders of size.
    N should be > 0 and the number of files in each subfolder should be > 0 as well.
    """
    assert N > 0
    data_size = dir_size(in_dir)
    no_files_in_folders = (
        data_size // N if (data_size % N == 0) else (data_size // N) + 1
    )
    assert no_files_in_folders > 0
    subfolders = []

    current_folder = 1
    current_file = 0
    os.system(f"mkdir {in_dir}/split_{current_folder}")
    for img in os.listdir(in_dir):
        if current_file >= no_files_in_folders:
            subfolders.append(f"{in_dir}/split_{current_folder}")
            current_folder += 1
            os.system(f"mkdir {in_dir}/split_{current_folder}")
            current_file = 0

        file = os.path.join(in_dir, img)
        if os.path.isfile(file):
            os.system(f"cp {file} {in_dir}/split_{current_folder}")
            current_file += 1

    if current_file < no_files_in_folders:
        # Don't forget the last split if it has less files than the maximum files in a subfolder
        subfolders.append(f"{in_dir}/split_{current_folder}")

    return subfolders


def remove_subfolders(in_dir: str) -> None:
    """
    Removes all the split_* subolders from the input folder
    """
    os.system(f"rm -r {in_dir}/split_*")


def merge_output_data(in_dir: str) -> None:
    """
    Takes all the results from the temp_working_fir and moves them into
    the output folder
    """

    os.system(f"mkdir {in_dir}/s1_reorient_lps")
    os.system(f"mkdir {in_dir}/s2_dlicv")
    os.system(f"mkdir {in_dir}/s3_masked")
    os.system(f"mkdir {in_dir}/s4_dlmuse")
    os.system(f"mkdir {in_dir}/s5_relabeled")
    os.system(f"mkdir {in_dir}/s6_combined")

    for dir in os.listdir(in_dir):
        if dir == "results":
            continue

        os.system(
            f"mv {in_dir}/{dir}/temp_working_dir/s1_reorient_lps/* {in_dir}/s1_reorient_lps/"
        )
        os.system(f"mv {in_dir}/{dir}/temp_working_dir/s2_dlicv/* {in_dir}/s2_dlicv/")
        os.system(f"mv {in_dir}/{dir}/temp_working_dir/s3_masked/* {in_dir}/s3_masked/")
        os.system(f"mv {in_dir}/{dir}/temp_working_dir/s4_dlmuse/* {in_dir}/s4_dlmuse/")
        os.system(
            f"mv {in_dir}/{dir}/temp_working_dir/s5_relabeled/* {in_dir}/s5_relabeled/"
        )
        os.system(
            f"mv {in_dir}/{dir}/temp_working_dir/s6_combined/* {in_dir}/s6_combined/"
        )
        os.system(f"mv {in_dir}/{dir}/*.nii.gz {in_dir}/")

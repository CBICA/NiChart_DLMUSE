import glob
import os
import re
from typing import Any

import numpy as np
import pandas as pd

LIST_IMG_EXT = [".nii", ".nii.gz"]


def get_basename(
    in_file: Any, suffix_to_remove: Any, ext_to_remove: Any = LIST_IMG_EXT
) -> Any:
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
            nii_files = [
                os.path.abspath(line.strip())
                for line in lines
                if line.strip().endswith(LIST_IMG_EXT)  # type:ignore
            ]

    nii_files = np.array(nii_files)
    print(f"Detected {nii_files.shape[0]} images ...")  # type:ignore

    # Check if images exist
    if len(nii_files) > 0:
        flag = np.zeros(nii_files.shape[0])  # type:ignore
        for i, ftmp in enumerate(nii_files):
            if os.path.exists(ftmp):
                flag[i] = 1
        nii_files = nii_files[flag == 1]

    print(f"Number of valid images is {len(nii_files)} ...")
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

import os

import pandas as pd

from NiChart_DLMUSE.utils import (
    get_basename,
    get_bids_prefix,
    make_img_list,
    remove_common_suffix,
    remove_subfolders,
    split_data,
)


def testing_get_basename() -> None:
    test_file: str = "test.nii.gz"
    assert get_basename(test_file, "", [".nii", ".nii.gz"]) == "test"

    test_file = "test.nii"
    assert get_basename(test_file, "", [".nii", ".nii.gz"]) == "test"


def testing_remove_common_suffix() -> None:
    test_files: list = ["test1.nii.gz", "test2.nii.gz", "test3.nii.gz", "test4.nii.gz"]
    correct_res: list = ["test1", "test2", "test3", "test4"]
    assert remove_common_suffix(test_files) == correct_res

    test_files = ["test1.nii.gz"]  # WARNING: Single case, review if needed
    correct_res = ["test1.nii.gz"]

    assert remove_common_suffix(test_files) == correct_res


def testing_make_img_list() -> None:
    os.system("mkdir test_dataset")
    for i in range(3):
        os.system(f"touch test_dataset/IXI10{i}-Guys-0000-T1.nii.gz")

    df_img: pd.DataFrame = make_img_list("test_dataset")
    df_img = df_img.sort_values(by="MRID")
    info = {
        "MRID": [f"IXI10{i}" for i in range(3)],
        "img_path": [
            os.path.abspath(f"test_dataset/IXI10{i}-Guys-0000-T1.nii.gz")
            for i in range(3)
        ],
        "img_base": [f"IXI10{i}-Guys-0000-T1.nii.gz" for i in range(3)],
        "img_prefix": [f"IXI10{i}-Guys-0000-T1" for i in range(3)],
    }
    df_test: pd.DataFrame = pd.DataFrame(info)

    assert list(df_img["MRID"]) == list(df_test["MRID"])
    assert list(df_img["img_path"]) == list(df_test["img_path"])
    assert list(df_img["img_base"] == list(df_test["img_base"]))
    assert list(df_img["img_prefix"] == list(df_test["img_prefix"]))

    os.system("rm -r test_dataset")


def testing_get_bids_prefix() -> None:
    pass


def testing_collect_T1() -> None:
    os.system("mkdir test_collect_T1")

    # Generate the BIDS input folder for testing
    for i in range(9):
        os.system(f"mkdir test_collect_T1/sub-0{i}")
        os.system(f"mkdir test_collect_T1/sub-0{i}/anat")
        os.system(f"touch test_collect_T1/sub-0{i}/anat/IXI-10{i}-Guys-0000-T1.nii.gz")

    for subfolder in os.listdir("test_collect_T1"):
        assert get_bids_prefix(subfolder) == "sub"

    os.system("rm -r test_collect_T1")


def testing_split_data() -> None:
    if os.path.exists("test_split_data"):
        os.system("rm -r test_split_data")

    def generate_random_test_folders(no_files: int = 15) -> None:
        os.system("mkdir test_split_data")
        for i in range(no_files):
            if i < 10:
                os.system(f"touch test_split_data/IXI-10{i}-Guys-0000-T1.nii.gz")
            else:
                os.system(f"touch test_split_data/IXI-1{i}-Guys-0000-T1.nii.gz")

    def check_subfolder_count(no_folders: int, count_in: int, count_last: int) -> None:
        subfldr_files = []
        for idx, subfldr in enumerate(os.listdir("test_split_data")):
            joined = os.path.join("test_split_data", subfldr)
            if idx < no_folders and os.path.isdir(joined):
                subfldr_files.append(len(os.listdir(joined)))
            elif idx >= no_folders and os.path.isdir(joined):
                subfldr_files.append(len(os.listdir(joined)))

        in_count: int = 0
        last_count: int = 0

        for files in subfldr_files:
            if files == count_in:
                in_count += 1
            else:
                last_count += 1

        assert (last_count == 1 if count_in != count_last else last_count == 0) and (
            in_count == no_folders - 1
            if count_in != count_last
            else in_count == no_folders
        )

    generate_random_test_folders(12)
    subfolders: list = split_data("test_split_data", 4)

    assert len(subfolders) == 4
    check_subfolder_count(4, 3, 3)
    os.system("rm -r test_split_data")

    generate_random_test_folders(20)
    subfolders = split_data("test_split_data", 4)

    assert len(subfolders) == 4
    check_subfolder_count(4, 5, 5)
    os.system("rm -r test_split_data")

    generate_random_test_folders(35)
    subfolders = split_data("test_split_data", 4)

    assert len(subfolders) == 4
    check_subfolder_count(4, 9, 8)
    os.system("rm -r test_split_data")

    generate_random_test_folders(1)
    subfolders = split_data("test_split_data", 4)

    assert len(subfolders) == 1
    print(len(subfolders))
    check_subfolder_count(1, 1, 1)
    os.system("rm -r test_split_data")


def testing_remove_subfolders() -> None:
    def generate_random_test_folders(no_files: int = 15) -> None:
        os.system("mkdir test_split_data")
        for i in range(no_files):
            if i < 10:
                os.system(f"touch test_split_data/IXI-10{i}-Guys-0000-T1.nii.gz")
            else:
                os.system(f"touch test_split_data/IXI-1{i}-Guys-0000-T1.nii.gz")

    generate_random_test_folders(10)
    remove_subfolders("test_split_data")

    assert len(os.listdir("test_split_data")) == 10
    os.system("rm -r test_split_data")

    generate_random_test_folders(1)
    remove_subfolders("test_split_data")
    assert len(os.listdir("test_split_data")) == 1

    os.system("rm -r test_split_data")

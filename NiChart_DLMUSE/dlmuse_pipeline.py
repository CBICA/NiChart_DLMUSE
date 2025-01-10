import logging
import os
import shutil
import threading
from typing import Any

import pkg_resources  # type: ignore

from .CalcROIVol import apply_create_roi_csv, combine_roi_csv
from .MaskImage import apply_combine_masks, apply_mask_img
from .RelabelROI import apply_relabel_rois
from .ReorientImage import apply_reorient_img, apply_reorient_to_init
from .SegmentImage import run_dlicv, run_dlmuse
from .utils import (
    collect_T1,
    make_img_list,
    merge_bids_output_data,
    merge_output_data,
    remove_subfolders,
    split_data,
)

# Config vars
SUFF_LPS = "_LPS.nii.gz"
SUFF_DLICV = "_DLICV.nii.gz"
SUFF_DLMUSE = "_DLMUSE.nii.gz"
SUFF_ROI = "_DLMUSE_Volumes.csv"
OUT_CSV = "DLMUSE_Volumes.csv"

REF_ORIENT = "LPS"

DICT_MUSE_NNUNET_MAP = pkg_resources.resource_filename(
    "NiChart_DLMUSE", "shared/dicts/MUSE_mapping_consecutive_indices.csv"
)
LABEL_FROM = "IndexConsecutive"
LABEL_TO = "IndexMUSE"

DICT_MUSE_SINGLE = DICT_MUSE_NNUNET_MAP

DICT_MUSE_DERIVED = pkg_resources.resource_filename(
    "NiChart_DLMUSE", "shared/dicts/MUSE_mapping_derived_rois.csv"
)

logger = logging.getLogger(__name__)
logging.basicConfig(filename="pipeline.log", encoding="utf-8", level=logging.DEBUG)


def run_dlmuse_pipeline(
    in_dir: str,
    out_dir: str,
    device: str,
    dlicv_extra_args: str,
    dlmuse_extra_args: str,
    clear_cache: bool,
    bids: bool,
    cores: str,
) -> None:
    """
    NiChart pipeline

    :param in_dir: The input directory
    :type in_dir: str
    :param out_dir: The output directory
    :type out_dir: str
    :type device: cpu/cuda/mps
    :param device: str
    :param dlicv_extra_args: Extra arguments for DLICV API
    :type dlicv_extra_args: str
    :param dlmuse_extra_args: Extra arguments for DLMUSE API
    :type dlmuse_extra_args: str
    :param clear_cache: True if cache should be cleared
    :type clear_cache: bool
    :param bids: True if your input is a bids type folder
    :type bids: bool
    :param cores: The number of cores(default is 4)
    :type cores: str

    :rtype: None
    """
    if not os.path.isdir(out_dir):
        print(f"Can't find {out_dir}, creating it...")
        # os.system(f"mkdir {out_dir}")
        os.mkdir(out_dir)

    elif len(os.listdir(out_dir)) != 0:
        print(f"Emptying output folder: {out_dir}...")
        for root, dirs, files in os.walk(out_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
    if clear_cache:
        os.system("DLICV -i ./dummy -o ./dummy --clear_cache")
        os.system("DLMUSE -i ./dummy -o ./dummy --clear_cache")

    working_dir = os.path.join(os.path.abspath(out_dir))

    if bids is True:
        if int(cores) > 1:
            collect_T1(in_dir, out_dir)

            no_threads = int(cores)
            subfolders = split_data("raw_temp_T1", no_threads)
            threads = []
            for i in range(len(subfolders)):
                curr_out_dir = out_dir + f"/split_{i}"
                curr_thread = threading.Thread(
                    target=run_thread,
                    args=(
                        subfolders[i],
                        curr_out_dir,
                        device,
                        dlmuse_extra_args,
                        dlicv_extra_args,
                        i,
                    ),
                )
                curr_thread.start()
                threads.append(curr_thread)

            for t in threads:
                t.join()

            merge_bids_output_data(working_dir)
            remove_subfolders("raw_temp_T1")
            remove_subfolders(out_dir)
        else:  # No core parallelization
            run_thread(in_dir, out_dir, device, dlmuse_extra_args, dlicv_extra_args)

    else:  # Non-BIDS
        if int(cores) > 1:
            no_threads = int(cores)
            subfolders = split_data(in_dir, no_threads)

            threads = []
            for i in range(len(subfolders)):
                curr_out_dir = out_dir + f"/split_{i}"
                curr_thread = threading.Thread(
                    target=run_thread,
                    args=(
                        subfolders[i],
                        curr_out_dir,
                        device,
                        dlmuse_extra_args,
                        dlicv_extra_args,
                        i,
                    ),
                )
                curr_thread.start()
                threads.append(curr_thread)

            for t in threads:
                t.join()

            merge_output_data(out_dir)
            remove_subfolders(in_dir)
            remove_subfolders(out_dir)
        else:  # No core parallelization
            run_thread(in_dir, out_dir, device, dlmuse_extra_args, dlicv_extra_args)


def run_thread(
    in_data: str,
    out_dir: str,
    device: str,
    dlmuse_extra_args: str = "",
    dlicv_extra_args: str = "",
    sub_fldr: int = 1,
    progress_bar: Any = None,
) -> None:
    """
    Run a thread of the pipeline

    :param in_data: the input directory
    :type in_data: str
    :param out_dir: the output directory
    :type out_dir: str
    :param device: conda/mps for GPU acceleration otherwise cpu
    :type device: str
    :param dlmuse_extra_args: extra arguments for DLMUSE package
    :type dlmuse_extra_args: str
    :param dlicv_extra_args: extra arguments for DLICV package
    :type dlicv_extra_args: str
    :param sub_fldr: the number of subfolders(default = 1)
    :type sub_fldr: int
    :param progress_bar: tqdm/stqdm progress bar for DLMUSE (default: None)
    :type progress_bar: tqdm


    :rtype: None
    """
    logging.info(f"Starting the pipeline on folder {sub_fldr}")
    logging.info(f"Detecting input images for batch [{sub_fldr}]...")
    # Detect input images
    df_img = make_img_list(in_data)
    logging.info(f"Detecting input images for batch [{sub_fldr}] done")

    # Set init paths and envs
    out_dir = os.path.abspath(out_dir)
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    out_dir_final = out_dir

    # Create working dir (FIXME: created within the output dir for now)
    working_dir = os.path.join(out_dir_final, "temp_working_dir")

    os.makedirs(working_dir, exist_ok=True)

    logging.info(f"Reorient images to LPS for batch [{sub_fldr}]...")
    # Reorient image to LPS
    out_dir = os.path.join(working_dir, "s1_reorient_lps")
    ref = REF_ORIENT
    out_suff = SUFF_LPS
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Reorienting images")
    apply_reorient_img(df_img, ref, out_dir, out_suff)
    logging.info(f"Reorient images to LPS for batch [{sub_fldr}] done")

    logging.info(f"Applying DLICV for batch [{sub_fldr}]...")
    # Apply DLICV
    in_dir = os.path.join(working_dir, "s1_reorient_lps")
    out_dir = os.path.join(working_dir, "s2_dlicv")
    in_suff = SUFF_LPS
    out_suff = SUFF_DLICV
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Running DLICV")
    run_dlicv(in_dir, in_suff, out_dir, out_suff, device, dlicv_extra_args)

    logging.info(f"Applying DLICV for batch [{sub_fldr}] done")

    logging.info(f"Applying mask for batch [{sub_fldr}]...")
    # Mask image
    in_dir = os.path.join(working_dir, "s1_reorient_lps")
    mask_dir = os.path.join(working_dir, "s2_dlicv")
    out_dir = os.path.join(working_dir, "s3_masked")
    in_suff = SUFF_LPS
    mask_suff = SUFF_DLICV
    out_suff = SUFF_DLICV
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Applying mask")
    apply_mask_img(df_img, in_dir, in_suff, mask_dir, mask_suff, out_dir, out_suff)

    logging.info(f"Applying mask for batch [{sub_fldr}] done")

    logging.info(f"Applying DLMUSE for batch [{sub_fldr}]...")
    # Apply DLMUSE
    in_dir = os.path.join(working_dir, "s3_masked")
    out_dir = os.path.join(working_dir, "s4_dlmuse")
    in_suff = SUFF_DLICV
    out_suff = SUFF_DLMUSE
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Running DLMUSE")
    run_dlmuse(in_dir, in_suff, out_dir, out_suff, device, dlmuse_extra_args)

    logging.info(f"Applying DLMUSE for batch [{sub_fldr}] done")

    logging.info(f"Relabeling DLMUSE for batch [{sub_fldr}]...")
    # Relabel DLMUSE
    in_dir = os.path.join(working_dir, "s4_dlmuse")
    out_dir = os.path.join(working_dir, "s5_relabeled")
    in_suff = SUFF_DLMUSE
    out_suff = SUFF_DLMUSE
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Relabeling ROIs")
    apply_relabel_rois(
        df_img,
        in_dir,
        in_suff,
        out_dir,
        out_suff,
        DICT_MUSE_NNUNET_MAP,
        LABEL_FROM,
        LABEL_TO,
    )

    logging.info(f"Applying DLMUSE for batch [{sub_fldr}] done")

    logging.info(f"Combining DLICV and MUSE masks for batch [{sub_fldr}]...")
    # Combine DLICV and MUSE masks
    in_dir = os.path.join(working_dir, "s5_relabeled")
    mask_dir = os.path.join(working_dir, "s2_dlicv")
    out_dir = os.path.join(working_dir, "s6_combined")
    in_suff = SUFF_DLMUSE
    mask_suff = SUFF_DLICV
    out_suff = SUFF_DLMUSE
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Combining masks")
    apply_combine_masks(df_img, in_dir, in_suff, mask_dir, mask_suff, out_dir, out_suff)

    logging.info(f"Combining DLICV and MUSE masks for batch [{sub_fldr}] done")

    logging.info(f"Reorienting to initial orientation for batch [{sub_fldr}]...")
    # Reorient to initial orientation
    in_dir = os.path.join(working_dir, "s6_combined")
    out_dir = out_dir_final
    in_suff = SUFF_DLMUSE
    out_suff = SUFF_DLMUSE
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Revert to initial orientation")
    apply_reorient_to_init(df_img, in_dir, in_suff, out_dir, out_suff)

    logging.info(f"Reorienting to initial orientation for batch [{sub_fldr}] done")

    logging.info(f"Create ROI csv for batch [{sub_fldr}]...")
    # Create roi csv
    in_dir = out_dir_final
    out_dir = out_dir_final
    in_suff = SUFF_DLMUSE
    out_suff = SUFF_ROI
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Creating ROI CSV")
    apply_create_roi_csv(
        df_img, in_dir, in_suff, DICT_MUSE_SINGLE, DICT_MUSE_DERIVED, out_dir, out_suff
    )
    logging.info(f"Create ROI csv for batch [{sub_fldr}] done")

    logging.info(f"Combine ROI csv for batch [{sub_fldr}]...")
    # Combine roi csv
    in_dir = out_dir_final
    out_dir = out_dir_final
    in_suff = SUFF_ROI
    out_name = OUT_CSV
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Combining CSV")
    combine_roi_csv(df_img, in_dir, in_suff, out_dir, out_name)

    logging.info(f"Combine ROI csv for batch [{sub_fldr}] done")

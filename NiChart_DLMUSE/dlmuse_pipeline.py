import logging
import os
import sys
from importlib.resources import files
from typing import Optional

import pandas as pd

from .CalcROIVol import apply_create_roi_csv, combine_roi_csv
from .MaskImage import apply_combine_masks, apply_mask_img
from .QualityControl import (
    DLICV_FAIL,
    DLMUSE_FAIL,
    OUT_QC_CSV,
    QC_REPORT_NAME,
    failed_prefixes,
    filter_cases,
    read_dlicv_qc,
    read_dlmuse_qc,
    write_combined_qc,
)
from .RelabelROI import apply_relabel_rois
from .ReorientImage import apply_reorient_img, apply_reorient_to_init
from .SegmentImage import run_dlicv, run_dlmuse
from .utils import make_img_list

# Config vars
SUFF_LPS = "_LPS.nii.gz"
SUFF_DLICV = "_DLICV.nii.gz"
SUFF_BRAINMASK = "_BrainMask.nii.gz"
SUFF_DLMUSE = "_DLMUSE.nii.gz"
SUFF_ROI = "_DLMUSE_Volumes.csv"
OUT_CSV = "DLMUSE_Volumes.csv"

REF_ORIENT = "LPS"

DICT_MUSE_NNUNET_MAP = str(
    files("NiChart_DLMUSE") / "shared/dicts/MUSE_mapping_consecutive_indices.csv"
)
LABEL_FROM = "IndexConsecutive"
LABEL_TO = "IndexMUSE"

DICT_MUSE_SINGLE = DICT_MUSE_NNUNET_MAP

DICT_MUSE_DERIVED = str(
    files("NiChart_DLMUSE") / "shared/dicts/MUSE_mapping_derived_rois.csv"
)

logger = logging.getLogger(__name__)
logging.basicConfig(encoding="utf-8", level=logging.DEBUG,
                    handlers=[logging.FileHandler("pipeline.log"),
                              logging.StreamHandler(sys.stdout)])


def run_pipeline(
    in_data: str,
    out_dir: str,
    device: str,
    dlmuse_extra_args: str = '',
    dlicv_extra_args: str = '',
    refaced_data: bool = False,
    sub_fldr: int = 1,
    progress_bar = None,
    qc: bool = True,
    drop_qc_failed: bool = False,
    qc_csv: Optional[str] = None,
) -> None:
    """
    NiChart pipeline

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
    :param qc: read DLICV/DLMUSE QC reports and write a combined QC csv (default: True)
    :type qc: bool
    :param drop_qc_failed: drop QC-failed cases from downstream steps; they stay in
                           DLMUSE_Volumes.csv with empty volumes (default: False)
    :type drop_qc_failed: bool
    :param qc_csv: path of the combined QC csv (default: <out_dir>/DLMUSE_QC.csv)
    :type qc_csv: str


    :rtype: None
    """
    logging.info(f"Starting the pipeline on folder {sub_fldr}")
    logging.info(f"Detecting input images for batch [{sub_fldr}]...")
    # Detect input images
    df_img = make_img_list(in_data)
    logging.info(f"Detecting input images for batch [{sub_fldr}] done")

    if drop_qc_failed and not qc:
        logging.warning("drop_qc_failed is ignored because QC is disabled")
        drop_qc_failed = False

    # Cases still moving through the pipeline (QC may remove some)
    df_active = df_img.copy()
    dropped: dict = {}
    df_dlicv_qc = df_dlmuse_qc = None

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
    run_dlicv(
        in_dir, in_suff, out_dir, out_suff, device, dlicv_extra_args,
        drop_failed=drop_qc_failed,
    )

    # If refaced data is specified, refine the masks used in the next step (s3_masked)
    if refaced_data:
        import SimpleITK as sitk

        for _, tmp_row in df_img.iterrows():
            img_prefix = tmp_row.img_prefix
            fpath = os.path.join(out_dir, img_prefix + SUFF_DLICV)
            if os.path.exists(fpath):
                s2_dlicv_output = sitk.ReadImage(fpath)
                # Keep only the largest connected component
                mask_component = sitk.ConnectedComponent(s2_dlicv_output)
                mask_sorted_component = sitk.RelabelComponent(
                    mask_component, sortByObjectSize=True
                )
                final_mask = sitk.Equal(mask_sorted_component, 1)
                # Write refined mask back in-place within s2_dlicv
                sitk.WriteImage(final_mask, fpath)

    # DLICV QC: drop failed cases (if requested) and cases without a mask
    failed: set = set()
    if qc:
        df_dlicv_qc = read_dlicv_qc(os.path.join(out_dir, QC_REPORT_NAME), SUFF_LPS)
        failed = failed_prefixes(df_dlicv_qc, "DLICV_QC_flag", DLICV_FAIL)
    df_active = filter_cases(
        df_active, failed, out_dir, SUFF_DLICV, "DLICV", drop_qc_failed, dropped
    )

    logging.info(f"Applying DLICV for batch [{sub_fldr}] done")

    logging.info(f"Applying mask for batch [{sub_fldr}]...")
    # Mask image
    in_dir = os.path.join(working_dir, "s1_reorient_lps")
    mask_dir = os.path.join(working_dir, "s2_dlicv")
    out_dir = os.path.join(working_dir, "s3_masked")
    in_suff = SUFF_LPS
    mask_suff = SUFF_DLICV
    out_suff = SUFF_BRAINMASK
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Applying mask")
    apply_mask_img(df_active, in_dir, in_suff, mask_dir, mask_suff, out_dir, out_suff)

    logging.info(f"Applying mask for batch [{sub_fldr}] done")

    logging.info(f"Applying DLMUSE for batch [{sub_fldr}]...")
    # Apply DLMUSE
    in_dir = os.path.join(working_dir, "s3_masked")
    out_dir = os.path.join(working_dir, "s4_dlmuse")
    in_suff = SUFF_BRAINMASK
    out_suff = SUFF_DLMUSE
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    if progress_bar is not None:
        progress_bar.update(1)
        progress_bar.set_description("Running DLMUSE")
    if len(df_active) > 0:
        run_dlmuse(
            in_dir, in_suff, out_dir, out_suff, device, dlmuse_extra_args, qc=qc
        )
    else:
        logging.warning(f"No cases left for DLMUSE in batch [{sub_fldr}]")

    # DLMUSE QC: drop failed cases (if requested) and cases without a segmentation
    failed = set()
    if qc:
        df_dlmuse_qc = read_dlmuse_qc(
            os.path.join(out_dir, QC_REPORT_NAME), SUFF_BRAINMASK
        )
        failed = failed_prefixes(df_dlmuse_qc, "DLMUSE_QC_status", DLMUSE_FAIL)
    df_active = filter_cases(
        df_active, failed, out_dir, SUFF_DLMUSE, "DLMUSE", drop_qc_failed, dropped
    )

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
        df_active,
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
    apply_combine_masks(df_active, in_dir, in_suff, mask_dir, mask_suff, out_dir, out_suff)

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
    apply_reorient_to_init(df_active, in_dir, in_suff, out_dir, out_suff)

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
        df_active, in_dir, in_suff, DICT_MUSE_SINGLE, DICT_MUSE_DERIVED, out_dir, out_suff
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
    # All input MRIDs are kept; dropped cases have empty volumes
    combine_roi_csv(
        df_img, in_dir, in_suff, out_dir, out_name, dict_derived_roi=DICT_MUSE_DERIVED
    )

    logging.info(f"Combine ROI csv for batch [{sub_fldr}] done")

    # Combined QC csv (one row per input scan)
    if qc:
        if qc_csv is None:
            qc_csv = os.path.join(out_dir_final, OUT_QC_CSV)
        empty = pd.DataFrame()
        write_combined_qc(
            df_img,
            df_dlicv_qc if df_dlicv_qc is not None else empty,
            df_dlmuse_qc if df_dlmuse_qc is not None else empty,
            dropped,
            qc_csv,
        )

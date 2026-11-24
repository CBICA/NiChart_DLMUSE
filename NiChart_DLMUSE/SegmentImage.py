import glob
import os
from typing import Any
import DLMUSE 
import DLICV


def run_dlicv(
    in_dir: str,
    in_suff: str,
    out_dir: str,
    out_suff: str,
    device: str,
    extra_args: str = "",
    drop_failed: bool = False,
) -> None:
    """
    Run dlicv with the passed images

    :param in_dir: the input directory
    :type in_dir: str
    :param in_suff: the input suffix
    :type in_suff: str
    :param out_dir: the output directory
    :type out_dir: str
    :param out_suff: the output suffix
    :type out_suff: str
    :param device: cuda/mps for GPU acceleration otherwise cpu
    :type device: str
    :param extra_args: extra arguments for DLICV package
    :type extra_args: str
    :param drop_failed: if True, DLICV deletes the masks of QC-failed cases
    :type drop_failed: bool

    :rtype: None
    """
    # Call DLICV
    drop_arg = "--drop_failed " if drop_failed else ""
    os.system(f"DLICV -i {in_dir} -o {out_dir} -device {device} {drop_arg}" + extra_args)

    for fname in glob.glob(os.path.join(out_dir, "label_*.nii.gz")):
        new_fname = fname.replace("label_", "", 1).replace(in_suff, out_suff)
        # Rename instead of copy so s2_dlicv doesn't keep a duplicate mask
        os.replace(fname, new_fname)


def run_dlmuse(
    in_dir: str,
    in_suff: Any,
    out_dir: str,
    out_suff: Any,
    device: str,
    extra_args: str = "",
    qc: bool = True,
) -> None:
    """
    Run dlmuse with the passed images

    :param in_dir: the input directory
    :type in_dir: str
    :param in_suff: the input suffix
    :type in_suff: str
    :param out_dir: the output directory
    :type out_dir: str
    :param out_suff: the output suffix
    :type out_suff: str
    :param device: cuda/mps for GPU acceleration otherwise cpu
    :type device: str
    :param extra_args: extra arguments for DLMUSE package
    :type extra_args: str
    :param qc: if True, run DLMUSE QC (writes <out_dir>/qc_report.csv)
    :type qc: bool

    :rtype: None
    """
    # Call DLMUSE
    qc_arg = "--qc " if qc else ""
    os.system(f"DLMUSE -i {in_dir} -o {out_dir} -device {device} {qc_arg}" + extra_args)

    for fname in glob.glob(os.path.join(out_dir, "DLMUSE_mask_*.nii.gz")):
        new_fname = fname.replace("DLMUSE_mask_", "", 1).replace(in_suff, out_suff)
        # Rename instead of copy so s4_dlmuse doesn't keep a duplicate mask
        os.replace(fname, new_fname)

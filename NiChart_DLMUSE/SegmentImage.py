import glob
import os
import shutil
from typing import Any


def run_dlicv(
    in_dir: str,
    in_suff: Any,
    out_dir: str,
    out_suff: Any,
    device: str,
    extra_args: str = "",
) -> None:
    # Call DLICV
    os.system(f"DLICV -i {in_dir} -o {out_dir} -device {device} " + extra_args)

    for fname in glob.glob(os.path.join(out_dir, "label_*.nii.gz")):
        new_fname = fname.replace("label_", "", 1).replace(in_suff, out_suff)
        shutil.copyfile(fname, new_fname)


def run_dlmuse(
    in_dir: str,
    in_suff: Any,
    out_dir: str,
    out_suff: Any,
    device: str,
    extra_args: str = "",
) -> None:
    # Call DLMUSE
    os.system(f"DLMUSE -i {in_dir} -o {out_dir} -device {device} " + extra_args)

    for fname in glob.glob(os.path.join(out_dir, "DLMUSE_mask_*.nii.gz")):
        new_fname = fname.replace("DLMUSE_mask_", "", 1).replace(in_suff, out_suff)
        # os.rename(fname, new_fname)
        shutil.copyfile(fname, new_fname)

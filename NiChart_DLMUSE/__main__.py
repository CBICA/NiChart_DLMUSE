# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2024 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

import argparse
import os
import threading

from .dlmuse_pipeline import run_pipeline
from .utils import merge_output_data, remove_subfolders, split_data

# VERSION = pkg_resources.require("NiChart_DLMUSE")[0].version
VERSION = 1.0


def main() -> None:
    prog = "NiChart_DLMUSE"
    description = "NiCHART Data Preprocessing Pipelines"
    usage = """
    NiChart_DLMUSE v{VERSION}
    ICV calculation, brain segmentation, and ROI extraction pipelines for
    structural MRI data.
    required arguments:
        [-i, --in_data]   Input images. The input should be:
                          - a single image file (.nii.gz or .nii), or
                          - a directory containing image files, or
                          - a list with the full path for each input image (one in each row)
        [-o, --out_dir]   The filepath of the output directory
        [-d, --device]    Device to run segmentation ('cuda' (GPU), 'cpu' (CPU) or 'mps' (Apple
                          M-series chips supporting 3D CNN))
    optional arguments:
        [-h, --help]    Show this help message and exit.
        [-V, --version] Show program's version number and exit.
        EXAMPLE USAGE:
        NiChart_DLMUSE  --in_data                     /path/to/input     \
                        --out_dir                    /path/to/output    \
    """.format(
        VERSION=VERSION
    )

    parser = argparse.ArgumentParser(
        prog=prog, usage=usage, description=description, add_help=False
    )

    # INDIR argument
    parser.add_argument(
        "-i",
        "--in_data",
        type=str,
        help="Input images.",
        default=None,
        required=True,
    )

    # OUTDIR argument
    parser.add_argument(
        "-o",
        "--out_dir",
        type=str,
        help="Output folder.",
        default=None,
        required=True,
    )

    # DEVICE argument
    parser.add_argument(
        "-d",
        "--device",
        type=str,
        help="Device (cpu, cuda, or mps)",
        default=None,
        required=True,
    )

    parser.add_argument(
        "-c",
        "--cores",
        type=str,
        help="Number of cores",
        default=4,
        required=False,
    )

    # VERSION argument
    help = "Show the version and exit"
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=prog + ": v{VERSION}.".format(VERSION=VERSION),
        help=help,
    )
    parser.add_argument(
        "--clear_cache",
        action="store_true",
        required=False,
        default=False,
        help="Set this flag to clear any cached models before running. This is recommended if a previous download failed.",
    )
    parser.add_argument(
        "--dlmuse_args",
        type=str,
        required=False,
        default="",
        help="Pass additional args to be sent to DLMUSE (ex. '-nps 1 -npp 1'). It is recommended to surround these args in a set of double quotes. See the DLMUSE documentation for details.",
    )

    parser.add_argument(
        "--dlicv_args",
        type=str,
        required=False,
        default="",
        help="Pass additional args to be sent to DLICV (ex. '-nps 1 -npp 1'). It is recommended to surround these args in a set of double quotes. See the DLICV documentation for details.",
    )

    # HELP argument
    help = "Show this message and exit"
    parser.add_argument("-h", "--help", action="store_true", help=help)

    args = parser.parse_args()

    in_data = args.in_data
    out_dir = args.out_dir
    device = args.device
    dlicv_extra_args = args.dlicv_args
    dlmuse_extra_args = args.dlmuse_args

    print()
    print("Arguments:")
    print(args)
    print()

    if args.clear_cache:
        os.system("DLICV -i ./dummy -o ./dummy --clear_cache")
        os.system("DLMUSE -i ./dummy -o ./dummy --clear_cache")

    # Run pipeline
    no_threads = args.cores  # for now
    subfolders = split_data(in_data, no_threads)

    threads = []
    for i in range(len(subfolders)):
        curr_out_dir = out_dir + f"/split_{i}"
        curr_thread = threading.Thread(
            target=run_pipeline,
            args=(
                subfolders[i],
                curr_out_dir,
                device,
                dlmuse_extra_args,
                dlicv_extra_args,
            ),
        )
        curr_thread.start()
        threads.append(curr_thread)

    for t in threads:
        t.join()

    merge_output_data(out_dir)
    remove_subfolders(in_data)


if __name__ == "__main__":
    main()

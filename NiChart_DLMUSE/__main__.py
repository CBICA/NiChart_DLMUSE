# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2024 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

import argparse

from .dlmuse_pipeline import run_dlmuse_pipeline

# VERSION = pkg_resources.require("NiChart_DLMUSE")[0].version
VERSION = "1.0.9"


def main() -> None:
    prog = "NiChart_DLMUSE"
    description = "NiCHART Data Preprocessing Pipelines"
    usage = """
    NiChart_DLMUSE v{VERSION}
    ICV calculation, brain segmentation, and ROI extraction pipelines for
    structural MRI data.
    required arguments:
        [-i, --in_dir]   Input images. The input should be:
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
        NiChart_DLMUSE  --in_dir                     /path/to/input     \
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
        "--in_dir",
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

    parser.add_argument(
        "--bids",
        type=bool,
        help="Specify if the provided dataset is BIDS type",
        default=False,
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

    in_dir = args.in_dir
    out_dir = args.out_dir
    device = args.device
    dlicv_extra_args = args.dlicv_args
    dlmuse_extra_args = args.dlmuse_args
    clear_cache = args.clear_cache
    bids = args.bids
    cores = args.cores

    print()
    print("Arguments:")
    print(args)
    print()

    run_dlmuse_pipeline(
        in_dir,
        out_dir,
        device,
        dlicv_extra_args,
        dlmuse_extra_args,
        clear_cache,
        bids,
        cores,
    )


if __name__ == "__main__":
    main()

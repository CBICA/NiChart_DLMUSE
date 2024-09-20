# This Python file uses the following encoding: utf-8
"""
contact: software@cbica.upenn.edu
Copyright (c) 2018 University of Pennsylvania. All rights reserved.
Use of this source code is governed by license located in license file: https://github.com/CBICA/NiBAx/blob/main/LICENSE
"""

import argparse

import pkg_resources  # type: ignore

#from NiChart_DLMUSE import dlmuse_pipeline
import dlmuse_pipeline as dlp

# VERSION = pkg_resources.require("NiChart_DLMUSE")[0].version
VERSION=1.0

def main() -> None:
    prog = "NiChart_DLMUSE"
    description = "niCHART Data Preprocessing Pipelines"
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
        help="Device.",
        default=None,
        required=True,
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

    # HELP argument
    help = "Show this message and exit"
    parser.add_argument("-h", "--help", action="store_true", help=help)

    args = parser.parse_args()

    in_data = args.in_data
    out_dir = args.out_dir
    device = args.device

    print()
    print("Arguments:")
    print(args)
    print()

    # Run pipeline
    #dlmuse_pipeline.run_pipeline(in_data, out_dir, device)
    dlp.run_pipeline(in_data, out_dir, device)
    

if __name__ == "__main__":
    main()

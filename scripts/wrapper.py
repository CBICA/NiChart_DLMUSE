import argparse
import os
import shutil
import tempfile
import time
import sys
from pathlib import Path
import pandas as pd


# This wrapper script just adapts NiChart_DLMUSE to take two separate output args. Everything else is passed transparently


def main():
    parser = argparse.ArgumentParser(description="Wrapper", allow_abbrev=False)
    parser.add_argument("-i", "--in_dir", required=True, help="Input directory")
    parser.add_argument(
        "-o1",
        "--out_segs",
        required=True,
        help="Output directory for segmentation files",
    )
    parser.add_argument(
        "-o2", "--out_csvs", required=True, help="Output directory for CSV files"
    )

    # Parse known args; leave the rest for original app
    args, extra_args = parser.parse_known_args()

    input_dir = args.in_dir
    seg_dir = Path(args.out_segs)
    csv_dir = Path(args.out_csvs)

    seg_dir.mkdir(parents=True, exist_ok=True)
    csv_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_output:
        tmp_output_path = Path(tmp_output)
        print(f"Input dir: {input_dir}, Seg dir: {seg_dir}, CSV dir: {csv_dir}, tmp dir: {tmp_output_path}")
        # Build command to run original application

        cmd = [
            "NiChart_DLMUSE",
            "-i",
            input_dir,
            "-o",
            str(tmp_output_path),
        ] + extra_args
        command = " ".join(cmd)
        os.system(command)
        if returncode > 0:
            sys.exit(1)

        # Copy output files
        for item in tmp_output_path.rglob("*"):
            if item.is_file():
                if item.name == "DLMUSE_Volumes.csv":
                    shutil.copy2(item, csv_dir / item.name)
                else:
                    dest_path = seg_dir / item.relative_to(tmp_output_path)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    print(f"Destination path for non-DLMUSE_Volumes file: {dest_path}")
                    shutil.copy2(item, dest_path)

    # Post-process DLMUSE_Volumes.csv
    csv_path = csv_dir / "DLMUSE_Volumes.csv"
    if csv_path.exists():
        df = pd.read_csv(csv_path)
        new_columns = []
        for col in df.columns:
            try:
                num = int(col)
                new_columns.append(f"DL_MUSE_Volume_{num}")
            except ValueError:
                new_columns.append(col)  # keep non-integer columns like 'MRID' unchanged
        df.columns = new_columns
        df.to_csv(csv_path, index=False)
    else:
        print("Warning: DLMUSE_Volumes.csv not found in output CSV directory.")

    # Delete temporary output files
    if os.path.exists(os.path.join(seg_dir / "temp_working_dir")):
        shutil.rmtree(os.path.join(seg_dir / "temp_working_dir"))


if __name__ == "__main__":
    main()


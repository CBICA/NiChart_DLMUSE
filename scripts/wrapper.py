import argparse
import os
import shutil
import tempfile
from pathlib import Path

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

        # Copy output files
        for item in tmp_output_path.rglob("*"):
            if item.is_file():
                if item.suffix.lower() == ".csv":
                    shutil.copy2(item, csv_dir / item.name)
                else:
                    dest_path = seg_dir / item.relative_to(tmp_output_path)
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, dest_path)


if __name__ == "__main__":
    main()

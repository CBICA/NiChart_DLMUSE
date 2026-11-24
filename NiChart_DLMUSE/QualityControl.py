"""
QC helpers for the NiChart_DLMUSE pipeline.

Reads the QC reports written by DLICV (s2_dlicv/qc_report.csv) and DLMUSE
(s4_dlmuse/qc_report.csv), drops failed cases from downstream steps when requested,
and writes one combined QC row per input scan.
"""

import logging
import os
from typing import Dict, Optional, Set

import pandas as pd

logger = logging.getLogger(__name__)

QC_REPORT_NAME = "qc_report.csv"
OUT_QC_CSV = "DLMUSE_QC.csv"

DLICV_FAIL = "Failed"
DLMUSE_FAIL = "FAIL"
DLMUSE_WARN = "WARN"
NOT_RUN = "NOT_RUN"
MISSING_OUTPUT = "missing output"

DLICV_COLS = ["DLICV_QC_flag", "DLICV_QC_log"]
DLMUSE_COLS = ["DLMUSE_QC_status", "DLMUSE_QC_issues"]
COMBINED_QC_COLUMNS = (
    ["MRID", "img_path"]
    + DLICV_COLS
    + DLMUSE_COLS
    + ["QC_overall", "Dropped", "Dropped_at_stage", "Drop_reason"]
)


def _strip(name: str, prefix: str, suffix: str) -> str:
    name = os.path.basename(str(name))
    if prefix and name.startswith(prefix):
        name = name[len(prefix):]
    if suffix and name.endswith(suffix):
        name = name[: -len(suffix)]
    return name


def _read_report(
    report_csv: str,
    name_col: str,
    rename: Dict[str, str],
    prefix: str,
    suffix: str,
) -> pd.DataFrame:
    """Read a QC report into a frame indexed by img_prefix."""
    out_cols = list(rename.values())
    if not os.path.isfile(report_csv):
        logger.warning(f"QC report not found: {report_csv}")
        return pd.DataFrame(columns=out_cols, index=pd.Index([], name="img_prefix"))
    df = pd.read_csv(report_csv, dtype=str, keep_default_na=False)
    missing = [c for c in [name_col, *rename] if c not in df.columns]
    if missing:
        logger.warning(f"QC report {report_csv} is missing columns {missing}; ignoring it")
        return pd.DataFrame(columns=out_cols, index=pd.Index([], name="img_prefix"))
    df["img_prefix"] = [_strip(x, prefix, suffix) for x in df[name_col]]
    df = df.drop_duplicates("img_prefix", keep="last").set_index("img_prefix")
    return df[list(rename)].rename(columns=rename)


def read_dlicv_qc(report_csv: str, in_suff: str) -> pd.DataFrame:
    """
    DLICV report columns: file_path,file_name,QC_flag,QC_log
    file_name is the DLICV input name, i.e. <img_prefix><in_suff>
    """
    return _read_report(
        report_csv,
        "file_name",
        {"QC_flag": "DLICV_QC_flag", "QC_log": "DLICV_QC_log"},
        "",
        in_suff,
    )


def read_dlmuse_qc(report_csv: str, in_suff: str) -> pd.DataFrame:
    """
    DLMUSE report columns: file,status,issues
    file is DLMUSE_mask_<img_prefix><in_suff>
    """
    return _read_report(
        report_csv,
        "file",
        {"status": "DLMUSE_QC_status", "issues": "DLMUSE_QC_issues"},
        "DLMUSE_mask_",
        in_suff,
    )


def failed_prefixes(df_qc: pd.DataFrame, col: str, fail_value: str) -> Set[str]:
    if df_qc.empty or col not in df_qc.columns:
        return set()
    return set(df_qc.index[df_qc[col].str.upper() == fail_value.upper()])


def filter_cases(
    df_active: pd.DataFrame,
    failed: Set[str],
    out_dir: str,
    out_suff: str,
    stage: str,
    drop: bool,
    dropped: Dict[str, dict],
) -> pd.DataFrame:
    """
    Remove cases from the active list after a stage.

    Cases whose stage output is missing are always removed (they can't be processed
    further). QC-failed cases are removed only when drop is True; their stage output
    is deleted so nothing stale is picked up downstream.
    """
    keep = []
    for _, row in df_active.iterrows():
        prefix = row.img_prefix
        out_file = os.path.join(out_dir, prefix + out_suff)
        if drop and prefix in failed:
            if os.path.exists(out_file):
                os.remove(out_file)
            dropped[prefix] = {"stage": stage, "reason": "QC failed"}
            logger.info(f"[QC] Dropping {prefix} at {stage}: QC failed")
            keep.append(False)
        elif not os.path.exists(out_file):
            dropped[prefix] = {"stage": stage, "reason": MISSING_OUTPUT}
            logger.warning(f"[QC] Dropping {prefix} at {stage}: {MISSING_OUTPUT} ({out_file})")
            keep.append(False)
        else:
            keep.append(True)
    return df_active[keep].reset_index(drop=True)


def _overall(row: pd.Series) -> str:
    dlicv = str(row["DLICV_QC_flag"])
    dlmuse = str(row["DLMUSE_QC_status"]).upper()
    if row["Dropped"] or dlicv == DLICV_FAIL or dlmuse == DLMUSE_FAIL:
        return "FAIL"
    if dlicv == NOT_RUN and dlmuse == NOT_RUN:
        return NOT_RUN
    if dlmuse == DLMUSE_WARN:
        return "WARN"
    return "PASS"


def write_combined_qc(
    df_img: pd.DataFrame,
    df_dlicv: pd.DataFrame,
    df_dlmuse: pd.DataFrame,
    dropped: Dict[str, dict],
    out_csv: str,
) -> pd.DataFrame:
    """Write one QC row per input scan to out_csv and return the frame."""
    df = df_img[["MRID", "img_path", "img_prefix"]].set_index("img_prefix")
    df = df.join(df_dlicv, how="left").join(df_dlmuse, how="left")
    for col in DLICV_COLS + DLMUSE_COLS:
        if col not in df.columns:
            df[col] = None
    for col in ("DLICV_QC_flag", "DLMUSE_QC_status"):
        df[col] = df[col].fillna(NOT_RUN)
    for col in ("DLICV_QC_log", "DLMUSE_QC_issues"):
        df[col] = df[col].fillna("")

    df["Dropped"] = [p in dropped for p in df.index]
    df["Dropped_at_stage"] = [dropped.get(p, {}).get("stage", "") for p in df.index]
    df["Drop_reason"] = [dropped.get(p, {}).get("reason", "") for p in df.index]
    df["QC_overall"] = df.apply(_overall, axis=1)

    df = df.reset_index(drop=True)[COMBINED_QC_COLUMNS]
    os.makedirs(os.path.dirname(os.path.abspath(out_csv)), exist_ok=True)
    df.to_csv(out_csv, index=False)

    counts = df["QC_overall"].value_counts()
    logger.info(
        f"[QC] {counts.get('PASS', 0)} passed, {counts.get('WARN', 0)} warned, "
        f"{counts.get('FAIL', 0)} failed, {int(df['Dropped'].sum())} dropped. "
        f"Combined QC saved to {out_csv}"
    )
    return df


def merge_qc_csvs(qc_csvs: list, out_csv: str) -> Optional[pd.DataFrame]:
    """Concatenate per-split combined QC CSVs into one file."""
    dfs = [pd.read_csv(f, keep_default_na=False) for f in qc_csvs if os.path.isfile(f)]
    if not dfs:
        return None
    df = pd.concat(dfs).reset_index(drop=True)
    df.to_csv(out_csv, index=False)
    return df

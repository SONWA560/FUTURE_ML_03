"""One-off data preparation step.

Reads the raw Kaggle "Resume Dataset" archive downloaded locally, trims the
CSV to the columns the pipeline actually needs, and copies a small, deliberately
chosen subset of the original PDFs (3 per category, picked by ID) so the app can
demonstrate real PDF parsing without bundling all ~2,484 near-duplicate files.

Run once from the backend/ directory:
    python3 scripts/prepare_dataset.py
"""

import shutil
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
ARCHIVE_DIR = PROJECT_ROOT / "archive (1)"
SOURCE_CSV = ARCHIVE_DIR / "Resume" / "Resume.csv"
SOURCE_PDF_ROOT = ARCHIVE_DIR / "data" / "data"

RAW_DATA_DIR = BACKEND_DIR / "data" / "raw"
TRIMMED_CSV = RAW_DATA_DIR / "Resume.csv"
SAMPLE_PDF_ROOT = RAW_DATA_DIR / "sample_pdfs"

SAMPLES_PER_CATEGORY = 3


def trim_csv() -> pd.DataFrame:
    df = pd.read_csv(SOURCE_CSV)
    trimmed = df[["ID", "Resume_str", "Category"]].copy()
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    trimmed.to_csv(TRIMMED_CSV, index=False)
    print(f"Wrote trimmed CSV: {TRIMMED_CSV} ({len(trimmed)} rows)")
    return trimmed


def copy_sample_pdfs(df: pd.DataFrame) -> None:
    SAMPLE_PDF_ROOT.mkdir(parents=True, exist_ok=True)
    total_copied = 0
    for category, group in df.groupby("Category"):
        chosen_ids = sorted(group["ID"].tolist())[:SAMPLES_PER_CATEGORY]
        dest_dir = SAMPLE_PDF_ROOT / category
        dest_dir.mkdir(parents=True, exist_ok=True)
        for resume_id in chosen_ids:
            source_pdf = SOURCE_PDF_ROOT / category / f"{resume_id}.pdf"
            if not source_pdf.exists():
                print(f"  WARNING: missing expected PDF {source_pdf}")
                continue
            shutil.copy2(source_pdf, dest_dir / f"{resume_id}.pdf")
            total_copied += 1
    print(f"Copied {total_copied} sample PDFs across {df['Category'].nunique()} categories")


if __name__ == "__main__":
    trimmed_df = trim_csv()
    copy_sample_pdfs(trimmed_df)

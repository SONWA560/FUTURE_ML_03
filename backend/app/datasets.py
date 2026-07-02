"""Loads the bundled Resume.csv corpus and looks up sample resumes for the UI."""

from functools import lru_cache

import pandas as pd

from app.config import settings


@lru_cache(maxsize=1)
def load_resume_corpus() -> pd.DataFrame:
    return pd.read_csv(settings.resume_csv_path)


def list_categories() -> list[str]:
    df = load_resume_corpus()
    return sorted(df["Category"].unique().tolist())


def get_sample_resumes(category: str | None = None, limit: int = 10) -> list[dict]:
    df = load_resume_corpus()
    if category:
        df = df[df["Category"] == category]
    df = df.head(limit)
    return [
        {"id": str(row.ID), "category": row.Category, "text": row.Resume_str}
        for row in df.itertuples()
    ]


def get_resume_by_id(resume_id: str) -> dict | None:
    df = load_resume_corpus()
    match = df[df["ID"].astype(str) == str(resume_id)]
    if match.empty:
        return None
    row = match.iloc[0]
    return {"id": str(row.ID), "category": row.Category, "text": row.Resume_str}

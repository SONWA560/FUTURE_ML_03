"""One-off offline fit of the TF-IDF vectorizer used for resume-to-JD similarity.

The vectorizer is fit ONCE here, on the full background resume corpus, and
persisted to disk. The live API only ever calls .transform() on this fitted
vectorizer - never .fit_transform() - so similarity scores stay stable and
reproducible regardless of which candidates are in a given screening batch.

Run once from the backend/ directory (after prepare_dataset.py):
    python3 scripts/build_tfidf_vectorizer.py
"""

import sys
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.preprocessing import clean_text  # noqa: E402


def main() -> None:
    df = pd.read_csv(settings.resume_csv_path)
    print(f"Fitting TF-IDF vectorizer on {len(df)} resumes...")

    cleaned_texts = df["Resume_str"].fillna("").map(clean_text)

    vectorizer = TfidfVectorizer(
        min_df=2,
        max_df=0.9,
        sublinear_tf=True,
        ngram_range=(1, 2),
    )
    vectorizer.fit(cleaned_texts)

    settings.tfidf_vectorizer_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(vectorizer, settings.tfidf_vectorizer_path)
    print(
        f"Fitted vectorizer with {len(vectorizer.vocabulary_)} terms, "
        f"saved to {settings.tfidf_vectorizer_path}"
    )


if __name__ == "__main__":
    main()

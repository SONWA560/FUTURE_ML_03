"""Loads the pre-fitted TF-IDF vectorizer artifact.

Only .transform() is ever called at request time - the vectorizer is never
refit here. See scripts/build_tfidf_vectorizer.py for the offline fit step.
"""

from functools import lru_cache

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from app.config import settings


@lru_cache(maxsize=1)
def get_vectorizer() -> TfidfVectorizer:
    return joblib.load(settings.tfidf_vectorizer_path)

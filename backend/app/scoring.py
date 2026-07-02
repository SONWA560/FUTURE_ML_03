"""Resume-to-job scoring: skill overlap + TF-IDF cosine similarity.

The two scores are deliberately kept separate and independently testable:
- compute_skill_score: rule-based overlap against the JD's declared skills.
- compute_similarity_scores_batch: TF-IDF cosine similarity via the
  pre-fitted vectorizer (see vectorizer.py), min-max rescaled within the
  batch so it is on a comparable scale to skill_score before combining.
- combine_scores: a simple weighted sum of the two.
"""

from app.config import settings
from app.preprocessing import clean_text
from app.vectorizer import get_vectorizer

from sklearn.metrics.pairwise import cosine_similarity


def compute_skill_score(
    required: list[str],
    preferred: list[str],
    candidate_skills: list[str],
) -> float:
    candidate_set = set(candidate_skills)
    required_weight = settings.required_skill_weight
    preferred_weight = settings.preferred_skill_weight

    total_possible = len(required) * required_weight + len(preferred) * preferred_weight
    if total_possible == 0:
        return 1.0

    matched_required = sum(1 for s in required if s in candidate_set)
    matched_preferred = sum(1 for s in preferred if s in candidate_set)

    earned = matched_required * required_weight + matched_preferred * preferred_weight
    return earned / total_possible


def compute_similarity_scores_batch(
    jd_text: str,
    candidate_texts: list[str],
    vectorizer=None,
) -> list[float]:
    """Cosine similarity between the JD and each candidate's cleaned text,
    transformed through the pre-fitted vectorizer, then min-max rescaled
    across the batch to [0, 1]. Accepts an optional vectorizer override so
    tests can inject a small, fast, fixture-fitted vectorizer instead of the
    full corpus-fitted one used in production."""
    if not candidate_texts:
        return []

    if vectorizer is None:
        vectorizer = get_vectorizer()
    cleaned_jd = clean_text(jd_text)
    cleaned_candidates = [clean_text(t) for t in candidate_texts]

    jd_vector = vectorizer.transform([cleaned_jd])
    candidate_vectors = vectorizer.transform(cleaned_candidates)

    raw_scores = cosine_similarity(candidate_vectors, jd_vector).flatten().tolist()

    lo, hi = min(raw_scores), max(raw_scores)
    if hi - lo < 1e-9:
        # All candidates equally (dis)similar - avoid a divide-by-zero and
        # avoid implying a meaningful spread that doesn't exist.
        return [0.5 for _ in raw_scores]
    return [(s - lo) / (hi - lo) for s in raw_scores]


def combine_scores(skill_score: float, similarity_score: float, w1: float, w2: float) -> float:
    total_weight = w1 + w2
    if total_weight == 0:
        return 0.0
    return (w1 * skill_score + w2 * similarity_score) / total_weight

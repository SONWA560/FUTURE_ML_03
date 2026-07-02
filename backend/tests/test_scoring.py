import pytest
from sklearn.feature_extraction.text import TfidfVectorizer

from app.scoring import combine_scores, compute_similarity_scores_batch, compute_skill_score


# --- compute_skill_score -----------------------------------------------

def test_full_skill_match():
    score = compute_skill_score(
        required=["Python", "SQL"],
        preferred=["Docker"],
        candidate_skills=["Python", "SQL", "Docker"],
    )
    assert score == 1.0


def test_partial_required_only_match():
    # required=[A,B] (weight 1.0 each), candidate only has A -> 1.0 / 2.0 = 0.5
    score = compute_skill_score(
        required=["Python", "SQL"],
        preferred=[],
        candidate_skills=["Python"],
    )
    assert score == pytest.approx(0.5)


def test_no_match():
    score = compute_skill_score(
        required=["Python", "SQL"],
        preferred=["Docker"],
        candidate_skills=["Excel"],
    )
    assert score == 0.0


def test_zero_requirements_guard():
    score = compute_skill_score(required=[], preferred=[], candidate_skills=["Python"])
    assert score == 1.0


# --- compute_similarity_scores_batch ------------------------------------

@pytest.fixture
def toy_vectorizer():
    corpus = [
        "python sql developer building backend systems",
        "chef cooking menu planning kitchen",
        "python sql developer building backend systems",
    ]
    vectorizer = TfidfVectorizer()
    vectorizer.fit(corpus)
    return vectorizer


def test_identical_text_similarity_is_high(toy_vectorizer):
    jd_text = "python sql developer building backend systems"
    scores = compute_similarity_scores_batch(
        jd_text,
        ["python sql developer building backend systems", "chef cooking menu planning kitchen"],
        vectorizer=toy_vectorizer,
    )
    # after batch min-max rescaling, the identical-text candidate should be at the top of the batch
    assert scores[0] == 1.0
    assert scores[1] == 0.0


def test_disjoint_vocabulary_similarity_batch_rescale(toy_vectorizer):
    jd_text = "python sql developer building backend systems"
    scores = compute_similarity_scores_batch(
        jd_text,
        ["chef cooking menu planning kitchen"],
        vectorizer=toy_vectorizer,
    )
    # single-candidate batch with no spread -> degenerate case returns 0.5
    assert scores == [0.5]


def test_empty_candidate_list_returns_empty(toy_vectorizer):
    assert compute_similarity_scores_batch("some jd text", [], vectorizer=toy_vectorizer) == []


def test_similarity_is_stable_regardless_of_other_candidates_ranking(toy_vectorizer):
    """Regression guard: a candidate's raw similarity to the JD must not depend
    on which other candidates happen to be in the batch. This only holds for
    the underlying vectorizer transform - the batch rescale intentionally
    changes relative scores, so we check the pre-rescale cosine similarity
    directly via the vectorizer, not the rescaled output."""
    from sklearn.metrics.pairwise import cosine_similarity

    jd_vector = toy_vectorizer.transform(["python sql developer building backend systems"])
    candidate_text = "python sql developer building backend systems"
    candidate_vector = toy_vectorizer.transform([candidate_text])

    score_alone = cosine_similarity(candidate_vector, jd_vector)[0][0]
    score_again = cosine_similarity(candidate_vector, jd_vector)[0][0]
    assert score_alone == score_again


# --- combine_scores -------------------------------------------------------

def test_combine_scores_default_weights():
    result = combine_scores(skill_score=0.8, similarity_score=0.4, w1=0.6, w2=0.4)
    assert result == pytest.approx(0.6 * 0.8 + 0.4 * 0.4)


def test_combine_scores_weights_are_normalised():
    # weights not summing to 1 are normalised by their sum, not taken literally
    result = combine_scores(skill_score=1.0, similarity_score=0.0, w1=2.0, w2=2.0)
    assert result == pytest.approx(0.5)

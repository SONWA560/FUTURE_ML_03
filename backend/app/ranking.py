"""Orchestrates: gather candidates -> extract skills -> score -> rank -> gaps."""

from dataclasses import dataclass

from app.explain import build_explanation
from app.scoring import combine_scores, compute_similarity_scores_batch, compute_skill_score
from app.schemas import CandidateResult, JobDescription
from app.skills import get_skill_extractor


@dataclass
class RawCandidate:
    id: str
    source: str
    text: str
    category: str | None = None


def rank_candidates(
    job: JobDescription,
    candidates: list[RawCandidate],
    skill_weight: float,
    similarity_weight: float,
) -> list[CandidateResult]:
    if not candidates:
        return []

    extractor = get_skill_extractor()
    jd_text = f"{job.title}. {job.description}"

    candidate_texts = [c.text for c in candidates]
    similarity_scores = compute_similarity_scores_batch(jd_text, candidate_texts)

    scored: list[CandidateResult] = []
    for candidate, similarity_score in zip(candidates, similarity_scores):
        candidate_skills = extractor.extract(candidate.text)
        candidate_skill_set = set(candidate_skills)

        skill_score = compute_skill_score(job.required_skills, job.preferred_skills, candidate_skills)
        final_score = combine_scores(skill_score, similarity_score, skill_weight, similarity_weight)

        matched_required = [s for s in job.required_skills if s in candidate_skill_set]
        matched_preferred = [s for s in job.preferred_skills if s in candidate_skill_set]
        missing_required = [s for s in job.required_skills if s not in candidate_skill_set]
        missing_preferred = [s for s in job.preferred_skills if s not in candidate_skill_set]

        scored.append(
            CandidateResult(
                id=candidate.id,
                source=candidate.source,
                category=candidate.category,
                rank=0,  # assigned below after sorting
                skill_score=round(skill_score, 4),
                similarity_score=round(similarity_score, 4),
                final_score=round(final_score, 4),
                matched_required_skills=matched_required,
                matched_preferred_skills=matched_preferred,
                missing_required_skills=missing_required,
                missing_preferred_skills=missing_preferred,
                explanation="",  # filled in below, once rank is known
                text_snippet=candidate.text[:280].strip(),
            )
        )

    scored.sort(key=lambda c: c.final_score, reverse=True)
    total = len(scored)
    for position, result in enumerate(scored, start=1):
        result.rank = position
        result.explanation = build_explanation(result, total)

    return scored

"""Deterministic, template-based plain-English explanations for recruiters.

Takes an already-scored CandidateResult and only formats it into prose - it
never recomputes matching itself, so the explanation text can never diverge
from the numbers shown alongside it.
"""

from app.schemas import CandidateResult


def build_explanation(result: CandidateResult, total_candidates: int) -> str:
    required_total = len(result.matched_required_skills) + len(result.missing_required_skills)
    preferred_total = len(result.matched_preferred_skills) + len(result.missing_preferred_skills)

    sentences = [
        f"Ranked #{result.rank} of {total_candidates}."
    ]

    if required_total:
        sentences.append(
            f"Matches {len(result.matched_required_skills)} of {required_total} required skills"
            + (
                f" and {len(result.matched_preferred_skills)} of {preferred_total} preferred skills."
                if preferred_total
                else "."
            )
        )

    sentences.append(
        f"The resume's overall content is a {round(result.similarity_score * 100)}% textual match "
        "to the job description relative to the other candidates in this batch."
    )

    if result.missing_required_skills:
        sentences.append(
            "Missing required skills: " + ", ".join(result.missing_required_skills) + "."
        )
    if result.missing_preferred_skills:
        sentences.append(
            "Missing preferred skills: " + ", ".join(result.missing_preferred_skills) + "."
        )
    if not result.missing_required_skills and not result.missing_preferred_skills:
        sentences.append("No listed required or preferred skills are missing.")

    return " ".join(sentences)

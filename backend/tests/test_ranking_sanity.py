from app.datasets import get_resume_by_id
from app.ranking import RawCandidate, rank_candidates
from app.schemas import JobDescription

# Real, ID-pinned rows from the bundled Resume.csv (also used as sample PDFs),
# so this test exercises the full pipeline against genuine resume text.
IT_RESUME_IDS = ["10089434", "10247517", "10265057"]
CHEF_RESUME_IDS = ["10001727", "10276858", "10333299"]

IT_JOB = JobDescription(
    id="it-support-engineer",
    title="Information Technology Support Engineer",
    category="INFORMATION-TECHNOLOGY",
    description=(
        "We are looking for an IT Support Engineer to maintain our network "
        "infrastructure and provide help desk support to staff. You will manage "
        "user accounts in Active Directory, troubleshoot hardware and software "
        "issues, administer Windows Server environments, and write SQL queries "
        "to investigate data issues."
    ),
    required_skills=["Networking", "Troubleshooting", "Active Directory", "Help Desk Support", "Windows Server", "SQL"],
    preferred_skills=["Amazon Web Services (AWS)", "Docker", "Python", "Linux", "Cloud Computing"],
)


def _load_candidates(resume_ids, source="sample"):
    candidates = []
    for resume_id in resume_ids:
        resume = get_resume_by_id(resume_id)
        assert resume is not None, f"expected fixture resume {resume_id} to exist in Resume.csv"
        candidates.append(RawCandidate(id=resume["id"], source=source, text=resume["text"], category=resume["category"]))
    return candidates


def test_it_resumes_outrank_chef_resumes_for_it_job():
    candidates = _load_candidates(IT_RESUME_IDS) + _load_candidates(CHEF_RESUME_IDS)

    results = rank_candidates(job=IT_JOB, candidates=candidates, skill_weight=0.6, similarity_weight=0.4)

    ranks_by_id = {r.id: r.rank for r in results}
    max_it_rank = max(ranks_by_id[rid] for rid in IT_RESUME_IDS)
    min_chef_rank = min(ranks_by_id[rid] for rid in CHEF_RESUME_IDS)

    assert max_it_rank < min_chef_rank


def test_missing_skill_lists_preserve_jd_declared_order():
    candidates = _load_candidates(CHEF_RESUME_IDS[:1])
    results = rank_candidates(job=IT_JOB, candidates=candidates, skill_weight=0.6, similarity_weight=0.4)

    result = results[0]
    all_missing = result.missing_required_skills
    # order must match the JD's declared required_skills order, not arbitrary set order
    expected_order = [s for s in IT_JOB.required_skills if s in all_missing]
    assert all_missing == expected_order

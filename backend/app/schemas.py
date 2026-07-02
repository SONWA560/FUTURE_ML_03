from pydantic import BaseModel, Field


class JobRoleSummary(BaseModel):
    id: str
    title: str
    category: str


class JobDescription(BaseModel):
    id: str = "custom"
    title: str
    category: str | None = None
    description: str
    required_skills: list[str]
    preferred_skills: list[str] = Field(default_factory=list)


class CustomJobRequest(BaseModel):
    title: str
    description: str


class SampleResumeRef(BaseModel):
    id: str
    category: str


class UploadedCandidate(BaseModel):
    id: str
    filename: str
    text: str


class ScreenRequest(BaseModel):
    job: JobDescription
    sample_resume_ids: list[str] = Field(default_factory=list)
    uploaded_candidates: list[UploadedCandidate] = Field(default_factory=list)
    skill_weight: float = 0.6
    similarity_weight: float = 0.4


class CandidateResult(BaseModel):
    id: str
    source: str  # "sample" or "upload"
    category: str | None = None
    rank: int
    skill_score: float
    similarity_score: float
    final_score: float
    matched_required_skills: list[str]
    matched_preferred_skills: list[str]
    missing_required_skills: list[str]
    missing_preferred_skills: list[str]
    explanation: str
    text_snippet: str


class ScreenResponse(BaseModel):
    job: JobDescription
    candidates: list[CandidateResult]

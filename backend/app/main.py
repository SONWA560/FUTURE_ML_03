import uuid

from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app import datasets, jobs
from app.config import settings
from app.pdf_extract import ExtractionError, extract_text_from_pdf
from app.ranking import RawCandidate, rank_candidates
from app.schemas import (
    CustomJobRequest,
    JobDescription,
    JobRoleSummary,
    ScreenRequest,
    ScreenResponse,
)
from app.skills import get_skill_extractor

app = FastAPI(title="Resume Screening & Ranking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/job-roles", response_model=list[JobRoleSummary])
def api_list_job_roles():
    return jobs.list_job_roles()


@app.get("/api/job-roles/{job_id}", response_model=JobDescription)
def api_get_job_role(job_id: str):
    job = jobs.get_job_role(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job role not found")
    return job


@app.post("/api/job-roles/custom", response_model=JobDescription)
def api_custom_job(request: CustomJobRequest):
    extractor = get_skill_extractor()
    detected_skills = extractor.extract(request.description)
    return JobDescription(
        id="custom",
        title=request.title,
        category=None,
        description=request.description,
        required_skills=detected_skills,
        preferred_skills=[],
    )


@app.get("/api/resumes/categories", response_model=list[str])
def api_list_categories():
    return datasets.list_categories()


@app.get("/api/resumes/sample")
def api_sample_resumes(category: str | None = None, limit: int = 10):
    return datasets.get_sample_resumes(category=category, limit=limit)


@app.post("/api/resumes/upload")
async def api_upload_resume(file: UploadFile):
    file_bytes = await file.read()
    filename = file.filename or "upload"

    if filename.lower().endswith(".pdf"):
        try:
            text = extract_text_from_pdf(file_bytes)
        except ExtractionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
    else:
        try:
            text = file_bytes.decode("utf-8", errors="ignore")
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Could not read file as text") from exc

    if len(text.strip()) < settings.min_extractable_text_chars:
        raise HTTPException(
            status_code=422,
            detail="No usable text was found in this file.",
        )

    return {"id": str(uuid.uuid4()), "filename": filename, "text": text}


@app.post("/api/screen", response_model=ScreenResponse)
def api_screen(request: ScreenRequest):
    candidates: list[RawCandidate] = []

    for resume_id in request.sample_resume_ids:
        resume = datasets.get_resume_by_id(resume_id)
        if resume is None:
            raise HTTPException(status_code=404, detail=f"Sample resume {resume_id} not found")
        candidates.append(
            RawCandidate(id=resume["id"], source="sample", text=resume["text"], category=resume["category"])
        )

    for uploaded in request.uploaded_candidates:
        candidates.append(RawCandidate(id=uploaded.id, source="upload", text=uploaded.text, category=None))

    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates supplied to screen")

    results = rank_candidates(
        job=request.job,
        candidates=candidates,
        skill_weight=request.skill_weight,
        similarity_weight=request.similarity_weight,
    )

    return ScreenResponse(job=request.job, candidates=results)

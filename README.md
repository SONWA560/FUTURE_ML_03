# Resume Screening & Ranking

An NLP-powered system that screens, scores and ranks candidate resumes against a job role, and explains *why* each candidate ranked where they did — built to be shown to a recruiter or HR manager, not just a data scientist.

Given a job description and a set of resumes, it:

- cleans and preprocesses the resume text (NLTK),
- extracts skills from resumes and job descriptions (spaCy),
- scores each resume against the job on two independent signals — matched skills and overall text similarity (scikit-learn),
- ranks candidates by a combined, adjustable score,
- and lists each candidate's missing required/preferred skills with a plain-English explanation of the ranking.

## How it works (for recruiters and HR)

Every candidate gets two separate scores, combined into one overall score:

1. **Skill match** — the proportion of the job's required and preferred skills found in the candidate's resume (required skills count twice as much as preferred ones).
2. **Text similarity** — how closely the overall wording of the resume matches the job description, using TF-IDF (a standard, transparent text-comparison technique — no black-box AI model, every similarity score can be traced back to which words overlap).

You can drag a slider on the results page to decide how much each of these should matter, and the ranking updates instantly. Click any candidate to see:

- a breakdown of their two scores,
- which required/preferred skills they have and which are missing,
- a one-paragraph, plain-English explanation of their rank.

## Architecture

```
backend/    FastAPI + spaCy + NLTK + scikit-learn — the screening pipeline and API
frontend/   Next.js (App Router) + shadcn/ui, themed with tweakcn "darkmatter" — the UI
notebooks/  Jupyter notebooks documenting the data exploration and a ranking sanity check
```

The frontend never touches resume data directly — it calls the backend API for everything (sample resumes, job roles, uploads, screening).

## Dataset

The resume corpus is the real [Kaggle "Resume Dataset" by snehaanbhawal](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset) — 2,484 real resumes across 24 job categories, bundled as `backend/data/raw/Resume.csv` (trimmed to the `ID`, `Resume_str`, `Category` columns actually used) plus a deliberately small sample of the original PDFs (3 per category, `backend/data/raw/sample_pdfs/`) to demonstrate genuine PDF parsing.

No public job-description dataset was used. The ten curated job roles in `backend/app/data/curated_jobs.json` (IT Support Engineer, Business Development Manager, Staff Accountant, Legal Advocate, Mechanical Design Engineer, Financial Analyst, Executive Chef, Healthcare Coordinator, Aviation Logistics Coordinator, IT Consultant) are hand-written for this project, drawn from the resume dataset's higher-count categories. Users can also paste in any real job description of their own, and skills are auto-detected from the text.

The skills taxonomy (`backend/app/data/skills_taxonomy.json`, 200 skills) is **grounded in the dataset itself**: `notebooks/01_data_exploration.ipynb` parses the comma-separated "Skills" sections that almost every resume in this dataset has, and tallies which phrases recruiters/candidates actually use — see `backend/scripts/build_skills_taxonomy.py` for the curated result.

## Scoring methodology, in more detail

- **Skill extraction** uses a spaCy `PhraseMatcher` over the curated taxonomy (with aliases, e.g. "JS" → "JavaScript"), matched on token boundaries so short skill names can't falsely match inside unrelated words.
- **Text similarity** uses a TF-IDF vectorizer **fitted once, offline**, on the full 2,484-resume corpus (`backend/scripts/build_tfidf_vectorizer.py`, artifact committed at `backend/artifacts/tfidf_vectorizer.joblib`). The live API only ever calls `.transform()` on this fitted vectorizer — it is never refit per request — so a candidate's similarity score is stable and reproducible no matter which other candidates are in the same screening batch. Raw cosine similarities are then rescaled to 0–100% within each screening batch, since raw TF-IDF similarities are naturally small and would otherwise be dwarfed by the skill-match score.
- **Ranking** sorts by the combined score and records each candidate's missing required/preferred skills in the job's declared order.
- **Explanations** are template-based, generated purely from the already-computed scores — never from a separate model call — so the text can never contradict the numbers shown next to it.

## Running it locally

### Backend

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -c "import nltk; [nltk.download(p) for p in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']]"
uvicorn app.main:app --reload --port 8000
```

The TF-IDF vectorizer artifact is already committed, so this is all that's needed to serve the API. If you change the preprocessing or the resume corpus, regenerate it with `python3 scripts/build_tfidf_vectorizer.py`.

### Frontend

```bash
cd frontend
cp .env.example .env.local   # points the UI at http://localhost:8000
pnpm install
pnpm dev
```

Open http://localhost:3000.

### Tests

```bash
cd backend
source .venv/bin/activate
pytest
```

23 tests cover text preprocessing, skill extraction (including a check that short skill names can't falsely match inside unrelated words), scoring edge cases (including a regression test that the vectorizer is never refit per request), and an end-to-end ranking sanity check on real resume rows (IT resumes must outrank Chef resumes for an IT job description).

### Notebooks

```bash
cd backend && source .venv/bin/activate
cd ../notebooks && jupyter notebook
```

- `01_data_exploration.ipynb` — category distribution, resume length stats, and the frequency scan used to ground the skills taxonomy.
- `02_scoring_sanity_check.ipynb` — runs the real pipeline against ID-pinned resumes and confirms the ranking behaves sensibly.

## Tech stack

Python, FastAPI, spaCy, NLTK, scikit-learn, pandas, pdfplumber, Next.js, TypeScript, shadcn/ui, Tailwind CSS, Recharts.

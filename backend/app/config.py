from pathlib import Path

from pydantic_settings import BaseSettings

APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent


class Settings(BaseSettings):
    skills_taxonomy_path: Path = APP_DIR / "data" / "skills_taxonomy.json"
    curated_jobs_path: Path = APP_DIR / "data" / "curated_jobs.json"
    resume_csv_path: Path = BACKEND_DIR / "data" / "raw" / "Resume.csv"
    sample_pdfs_dir: Path = BACKEND_DIR / "data" / "raw" / "sample_pdfs"
    tfidf_vectorizer_path: Path = BACKEND_DIR / "artifacts" / "tfidf_vectorizer.joblib"

    default_skill_weight: float = 0.6
    default_similarity_weight: float = 0.4
    required_skill_weight: float = 1.0
    preferred_skill_weight: float = 0.5

    min_extractable_text_chars: int = 50

    cors_origins: list[str] = ["http://localhost:3000"]


settings = Settings()

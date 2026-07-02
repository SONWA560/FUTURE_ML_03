# Backend

FastAPI + spaCy + NLTK + scikit-learn resume screening pipeline and API.

See the [project root README](../README.md) for the full methodology explanation, dataset provenance and setup instructions.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 -c "import nltk; [nltk.download(p) for p in ['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4']]"
uvicorn app.main:app --reload --port 8000
pytest
```

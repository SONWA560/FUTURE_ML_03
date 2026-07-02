#!/usr/bin/env bash
set -e

echo "Downloading NLTK data..."
python -c "
import nltk
nltk.download(['punkt', 'punkt_tab', 'stopwords', 'wordnet', 'omw-1.4'], quiet=True)
"

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

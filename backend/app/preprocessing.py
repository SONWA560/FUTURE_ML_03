"""Text cleaning shared by the offline TF-IDF fit script and the live API.

Both paths must call clean_text() so the fitted vectorizer's vocabulary stays
aligned with text seen at request time.
"""

import re

from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

_LEMMATIZER = WordNetLemmatizer()
_STOPWORDS = set(stopwords.words("english"))

# This dataset's resumes share a near-identical templated structure; these
# section headers add no discriminative signal and would otherwise pollute
# the TF-IDF vocabulary shared across almost every document.
_BOILERPLATE_HEADERS = [
    "professional summary",
    "career summary",
    "summary",
    "highlights",
    "accomplishments",
    "experience",
    "education and training",
    "education",
    "certifications",
    "affiliations",
    "interests",
    "skills",
    "additional information",
    "professional affiliations",
]

_HEADER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(h) for h in _BOILERPLATE_HEADERS) + r")\b",
    re.IGNORECASE,
)
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_NON_ALPHA_PATTERN = re.compile(r"[^a-zA-Z\s]")
_WHITESPACE_PATTERN = re.compile(r"\s+")


def strip_boilerplate_headers(text: str) -> str:
    return _HEADER_PATTERN.sub(" ", text)


def clean_text(text: str) -> str:
    """Lowercase, strip HTML/boilerplate/punctuation, tokenise, remove
    stopwords and lemmatise. Returns a single space-joined string ready for
    TF-IDF vectorisation or skill matching."""
    if not text:
        return ""

    text = _HTML_TAG_PATTERN.sub(" ", text)
    text = strip_boilerplate_headers(text)
    text = text.lower()
    text = _NON_ALPHA_PATTERN.sub(" ", text)
    text = _WHITESPACE_PATTERN.sub(" ", text).strip()

    tokens = word_tokenize(text)
    cleaned_tokens = [
        _LEMMATIZER.lemmatize(token)
        for token in tokens
        if token not in _STOPWORDS and len(token) > 1
    ]
    return " ".join(cleaned_tokens)

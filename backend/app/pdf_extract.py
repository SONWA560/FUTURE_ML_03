"""PDF text extraction for both bundled sample resumes and live uploads."""

from io import BytesIO

import pdfplumber

from app.config import settings


class ExtractionError(Exception):
    """Raised when no usable text could be extracted from a PDF."""


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            pages_text = [page.extract_text() or "" for page in pdf.pages]
    except Exception as exc:
        raise ExtractionError(f"Could not read PDF: {exc}") from exc

    text = "\n".join(pages_text).strip()
    if len(text) < settings.min_extractable_text_chars:
        raise ExtractionError(
            "No extractable text was found in this PDF. It may be a scanned "
            "image without a text layer - please try a text-based PDF or a "
            ".txt file instead."
        )
    return text

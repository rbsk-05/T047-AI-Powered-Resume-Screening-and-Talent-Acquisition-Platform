"""File text extractor for PDF and DOCX resume documents."""

import io
import fitz
from docx import Document


class TextExtractor:
    """Extract plain text from uploaded PDF or DOCX file bytes."""

    ALLOWED_SUFFIXES: frozenset[str] = frozenset({".pdf", ".docx"})

    @classmethod
    def extract_text(cls, filename: str, content: bytes) -> str:
        """Validate extension and non-empty content, returning extracted text."""
        if not content:
            raise ValueError("The uploaded file is empty.")

        suffix = filename.lower().rsplit(".", maxsplit=1)
        suffix = f".{suffix[-1]}" if len(suffix) == 2 else ""
        if suffix not in cls.ALLOWED_SUFFIXES:
            raise ValueError(
                f"Unsupported file type '{suffix or '(none)'}'. "
                "Only PDF and DOCX resume files are accepted."
            )

        if suffix == ".pdf":
            return cls._extract_pdf(content)
        return cls._extract_docx(content)

    @staticmethod
    def _extract_pdf(content: bytes) -> str:
        try:
            document = fitz.open(stream=content, filetype="pdf")
        except Exception as exc:
            raise ValueError(
                "The PDF file appears to be corrupted or unreadable."
            ) from exc
        try:
            pages = [page.get_text() for page in document]
        finally:
            document.close()
        text = "\n".join(pages).strip()
        if not text:
            raise ValueError(
                "No text could be extracted from the PDF. "
                "It may be a scanned image without OCR text."
            )
        return text

    @staticmethod
    def _extract_docx(content: bytes) -> str:
        try:
            document = Document(io.BytesIO(content))
        except Exception as exc:
            raise ValueError(
                "The DOCX file appears to be corrupted or unreadable."
            ) from exc
        text = "\n".join(p.text for p in document.paragraphs).strip()
        if not text:
            raise ValueError("No text could be extracted from the DOCX file.")
        return text

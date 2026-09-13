"""
Module 1: Resume Upload and Parsing
------------------------------------
Extracts raw text content from an uploaded resume file (PDF or DOCX).

This module is DONE / working. You shouldn't need to touch it unless
you want to improve extraction quality (e.g. handling multi-column
resumes, tables, etc.) later.
"""
import os
import pdfplumber
import docx

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_file(filename: str) -> bool:
    """Check whether the uploaded file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(filepath: str) -> str:
    """Extract all text from a PDF file, page by page."""
    text_parts = []
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_text_from_docx(filepath: str) -> str:
    """Extract all text from a DOCX file, paragraph by paragraph."""
    document = docx.Document(filepath)
    return "\n".join(p.text for p in document.paragraphs if p.text.strip())


def extract_text(filepath: str) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    Raises ValueError for unsupported file types.
    """
    ext = filepath.rsplit(".", 1)[1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(filepath)
    elif ext == "docx":
        return extract_text_from_docx(filepath)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

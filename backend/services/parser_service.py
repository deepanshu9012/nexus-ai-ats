import io

import docx
import fitz
import pytesseract
from pdf2image import convert_from_bytes


def extract_text_from_docx(file_bytes: bytes) -> str:
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        document = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [paragraph.text for paragraph in document.paragraphs]
        return "\n".join(paragraphs).strip()
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("The uploaded file is not a readable DOCX.") from exc


def extract_text_with_ocr(file_bytes: bytes) -> str:
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        images = convert_from_bytes(file_bytes)
        extracted_pages = [pytesseract.image_to_string(img) for img in images]
        return "\n".join(extracted_pages).strip()
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError("Failed to extract text with OCR.") from exc


def extract_text_from_pdf(file_bytes: bytes) -> str:
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        with fitz.open(stream=file_bytes, filetype="pdf") as document:
            if document.page_count == 0:
                raise ValueError("The uploaded PDF has no pages.")

            extracted_pages = [page.get_text("text") for page in document]
            return "\n".join(extracted_pages).strip()
    except fitz.FileDataError as exc:
        raise ValueError("The uploaded file is not a readable PDF.") from exc
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError("Failed to extract text from the PDF.") from exc


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    normalized_name = (filename or "").strip().lower()
    extension = normalized_name.rsplit(".", 1)[-1] if "." in normalized_name else ""

    if extension == "docx":
        return extract_text_from_docx(file_bytes)

    if extension == "pdf":
        text = extract_text_from_pdf(file_bytes)
        if len(text.strip()) < 50:
            return extract_text_with_ocr(file_bytes)
        return text

    raise ValueError("Unsupported file format. Please upload a PDF or DOCX.")

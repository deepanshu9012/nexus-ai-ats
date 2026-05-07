import fitz


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    if not pdf_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
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

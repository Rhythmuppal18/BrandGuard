import io
from pathlib import Path
from typing import Tuple

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import docx
except ImportError:
    docx = None

def extract_text_from_file(filename: str, file_bytes: bytes) -> Tuple[str, str]:
    """
    Extracts text from raw file bytes.
    Returns (extracted_text, detected_format).
    """
    ext = Path(filename).suffix.lower()
    
    if ext in [".txt", ".md", ".json", ".csv"]:
        try:
            return file_bytes.decode("utf-8"), "Plain Text / Markdown"
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1", errors="replace"), "Plain Text"

    elif ext == ".pdf":
        if fitz is None:
            raise RuntimeError("PyMuPDF (fitz) is not installed for PDF reading.")
        
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text_parts = []
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_text = page.get_text()
            if page_text.strip():
                text_parts.append(f"--- [Page {page_idx + 1}] ---\n{page_text.strip()}")
        doc.close()
        full_text = "\n\n".join(text_parts)
        if not full_text.strip():
            return "No extractable text found in PDF document (may be raster image or scanned).", "PDF"
        return full_text, "PDF Document"

    elif ext in [".docx", ".doc"]:
        if docx is None:
            raise RuntimeError("python-docx is not installed for Word document reading.")
        
        file_stream = io.BytesIO(file_bytes)
        doc = docx.Document(file_stream)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)
        full_text = "\n\n".join(paragraphs)
        if not full_text.strip():
            return "No text found in Word document.", "Word DOCX"
        return full_text, "Word Document (.docx)"

    else:
        # Fallback to UTF-8 decoding
        return file_bytes.decode("utf-8", errors="replace"), "Generic Document"


from pathlib import Path

from .pdf import extract_content_pdf
from .txt import extract_content_txt
from .docx import extract_content_docx

def extract_content(path : str) -> str:
    path = Path(path)
    extension = path.suffix.lower()

    if extension == ".pdf":
        return extract_content_pdf(path)

    elif extension in {".txt", ".csv", ".md"}:
        return extract_content_txt(path)
    
    elif extension == ".docx":
        return extract_content_docx(path)

    else:
        return ""
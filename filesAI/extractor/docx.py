from pathlib import Path
from docx import Document

def extract_content_docx(path:str | Path) -> str:

    try:
        doc = Document(path)
        paragraphs = [paragraph.text for paragraph in doc.paragraphs]
        return "\n".join(paragraphs).strip()
    except Exception as e:
        print(f"Error leyendo {path} : {e}")
        return ""


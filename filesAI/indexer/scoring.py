import re
from datetime import datetime


# Formatos de archivo reconocidos para comparar con la query.
# Cada formato tiene sus posibles extensiones y palabras de búsqueda.
FORMAT_ALIASES = {
    "pdf": {"exts": [".pdf"], "words": ["pdf"]},
    "word": {"exts": [".doc", ".docx"], "words": ["word", "doc", "docx"]},
    "excel": {"exts": [".xls", ".xlsx", ".csv"], "words": ["excel", "xls", "xlsx", "csv"]},
    "powerpoint": {"exts": [".ppt", ".pptx"], "words": ["powerpoint", "ppt", "pptx"]},
    "text": {"exts": [".txt", ".md", ".rtf"], "words": ["txt", "text", "md", "markdown"]},
}


def _normalize_text(text: str) -> str:
    """Pasa a minúsculas y elimina puntuación."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text


def infer_requested_format(query: str) -> str | None:
    """
    Detecta si la query pide explícitamente un formato de archivo.
    Devuelve la clave del formato (pdf, word, excel...) o None.
    """
    normalized = _normalize_text(query)
    words = set(normalized.split())

    for fmt, data in FORMAT_ALIASES.items():
        if any(alias in words for alias in data["words"]):
            return fmt
    return None


def compute_format_score(extension: str | None, requested_format: str | None) -> float:
    """
    Boost si la extensión del archivo coincide con el formato pedido en la query.
    Si la query no pide un formato concreto, el score es neutro (1.0).
    """
    if requested_format is None:
        return 1.0

    if extension is None:
        return 0.0

    ext_lower = extension.lower()
    if ext_lower in FORMAT_ALIASES[requested_format]["exts"]:
        return 2.0
    return 0.0


def compute_recency_score(modified_at: str, max_age_days: int = 365) -> float:
    """
    Devuelve un valor entre 0 y 1.
    1.0 = modificado hoy, 0.0 = más antiguo que max_age_days.
    """
    try:
        modified = datetime.strptime(modified_at, "%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return 0.0

    now = datetime.now()
    days = (now - modified).total_seconds() / 86400
    return max(0.0, min(1.0, 1.0 - days / max_age_days))

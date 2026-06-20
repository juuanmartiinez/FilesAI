import re
import math

from filesAI.indexer.database import get_connection


def extract_keywords(query: str) -> list[str]:
    """
    Extrae palabras clave de la query.
    Ignora puntuación y palabras muy cortas.
    """
    query = query.lower()
    query = re.sub(r"[^\w\s]", " ", query)
    words = query.split()
    return [word for word in words if len(word) > 2]


def compute_idf_weights(keywords: list[str], files_data: list) -> dict[str, float]:
    """
    Calcula pesos IDF simples para cada palabra clave.
    Palabras que aparecen en pocos archivos valen más.
    """
    total_files = len(files_data) or 1
    doc_counts = {kw: 0 for kw in keywords}

    for _path, name, content in files_data:
        text = f"{name} {content}".lower()
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                doc_counts[kw] += 1

    weights = {}
    for kw in keywords:
        count = max(doc_counts[kw], 1)
        weights[kw] = math.log(total_files / count) + 1

    return weights


def search(query: str, top_k: int = 5):
    """
    Búsqueda estricta por palabras clave.
    Solo devuelve archivos que contienen al menos el 70% de las keywords.
    """
    keywords = extract_keywords(query)

    if not keywords:
        return []

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path, name, content FROM files WHERE content != ''")
    files = cursor.fetchall()
    conn.close()

    min_matches = max(1, int(len(keywords) * 0.7))
    idf_weights = compute_idf_weights(keywords, files)

    query_normalized = query.lower()
    results = []

    for path, name, content in files:
        text = f"{name} {content}".lower()
        name_lower = name.lower()

        # Palabras clave que aparecen como palabra completa en el documento
        matched_keywords = [
            kw for kw in keywords
            if re.search(rf"\b{re.escape(kw)}\b", text)
        ]

        if len(matched_keywords) < min_matches:
            continue

        # Frecuencia ponderada por IDF en todo el contenido
        frequency_score = sum(
            len(re.findall(rf"\b{re.escape(kw)}\b", text)) * idf_weights[kw]
            for kw in matched_keywords
        )

        # Boost si las palabras clave aparecen en el nombre
        name_score = 0
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", name_lower):
                name_score += 0.5 * idf_weights[kw]

        # Bonus si aparece la frase exacta
        phrase_score = 5 if query_normalized in text else 0

        total_score = frequency_score + name_score + phrase_score

        results.append({
            "path": path,
            "name": name,
            "total_score": total_score
        })

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results[:top_k]

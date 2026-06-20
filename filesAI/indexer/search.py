import re  # Para limpiar y procesar texto
import math  # Para calcular logaritmos en IDF

from filesAI.indexer.database import get_connection  # Acceso a SQLite
from filesAI.indexer.bm25_index import search_bm25  # Fallback con BM25
from filesAI.indexer.scoring import (  # Metadatos objetivos para ordenar
    infer_requested_format,
    compute_format_score,
    compute_recency_score,
)


def extract_keywords(query: str) -> list[str]:
    """
    Extrae palabras clave de la query del usuario.
    Ignora palabras muy cortas porque suelen ser artículos o preposiciones.
    """
    query = query.lower()  # Normalizamos a minúsculas
    query = re.sub(r"[^\w\s]", " ", query)  # Quitamos puntuación
    words = query.split()  # Separamos en palabras
    return [word for word in words if len(word) > 2]  # Filtramos palabras de 1-2 letras


def compute_idf_weights(keywords: list[str], files_data: list) -> dict[str, float]:
    """
    Calcula pesos IDF simples para cada palabra clave.
    Palabras que aparecen en pocos archivos valen más.
    """
    total_files = len(files_data) or 1  # Evitamos división por cero
    doc_counts = {kw: 0 for kw in keywords}

    for _path, name, _extension, _modified_at, content in files_data:
        text = f"{name} {content}".lower()
        for kw in keywords:
            if kw in text:
                doc_counts[kw] += 1

    weights = {}
    for kw in keywords:
        count = max(doc_counts[kw], 1)  # Evitamos división por cero
        weights[kw] = math.log(total_files / count) + 1  # +1 para evitar pesos demasiado pequeños

    return weights


def search_strict(query: str, top_k: int = 5, preview_size: int = 4000):
    """
    Búsqueda estricta: devuelve archivos que contienen un porcentaje de palabras clave.
    Puntúa según frecuencia ponderada, proximidad, nombre y frases exactas.
    """
    keywords = extract_keywords(query)

    if not keywords:  # Si no hay palabras clave válidas, no hay resultados
        return []

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT path, name, extension, modified_at, content FROM files WHERE content != ''")
    files = cursor.fetchall()
    conn.close()

    min_matches = max(1, int(len(keywords) * 0.7))  # Umbral del 70% de palabras clave

    # Calculamos pesos IDF para dar más valor a palabras raras
    idf_weights = compute_idf_weights(keywords, files)

    # Normalizamos la query original para buscar frases exactas
    query_normalized = query.lower()

    # Detectamos si la query pide un formato concreto (pdf, word, excel...)
    requested_format = infer_requested_format(query)

    results = []

    for path, name, extension, modified_at, content in files:
        preview = content[:preview_size].lower()  # Preview del inicio del documento
        name_lower = name.lower()

        # Contamos cuántas palabras clave aparecen en el preview
        matched_keywords = [kw for kw in keywords if kw in preview]
        matches = len(matched_keywords)

        if matches < min_matches:
            continue  # Si no llega al umbral, descartamos el archivo

        # Puntuación por frecuencia ponderada por IDF
        frequency_score = sum(preview.count(kw) * idf_weights[kw] for kw in matched_keywords)

        # Puntuación por proximidad: palabras cercanas = más relevante
        positions = []
        for kw in matched_keywords:
            pos = preview.find(kw)
            if pos != -1:
                positions.append(pos)

        proximity_score = 0
        if len(positions) > 1:
            span = max(positions) - min(positions)  # Distancia entre primera y última palabra
            proximity_score = max(0, preview_size - span) / preview_size  # Normalizamos

        # Boost leve si las palabras clave aparecen en el nombre
        name_score = 0
        for kw in keywords:
            if kw in name_lower:
                name_score += 0.5 * idf_weights[kw]

        # Bonus alto si la frase exacta de la query aparece en el preview
        phrase_score = 0
        if query_normalized in preview:
            phrase_score = 5

        # Metadatos objetivos para ordenar: formato pedido y recencia
        format_score = compute_format_score(extension, requested_format)
        recency_score = compute_recency_score(modified_at)

        total_score = (
            frequency_score +
            proximity_score * 10 +
            name_score +
            phrase_score +
            format_score * 2.0 +
            recency_score * 1.0
        )

        results.append({
            "path": path,
            "name": name,
            "extension": extension,
            "modified_at": modified_at,
            "total_score": total_score
        })

    results.sort(key=lambda x: x["total_score"], reverse=True)  # Ordenamos por relevancia
    return results[:top_k]


def search_bm25_fallback(query: str, top_k: int = 5):
    """
    Fallback usando BM25 cuando la búsqueda estricta no encuentra nada.
    Aplica también recencia y formato como metadatos de ordenación.
    """
    results = search_bm25(query, top_k=top_k)
    requested_format = infer_requested_format(query)

    ranked = []
    for r in results:
        format_score = compute_format_score(r.get("extension"), requested_format)
        recency_score = compute_recency_score(r.get("modified_at", ""))

        total_score = r["bm25_score"] + format_score * 2.0 + recency_score * 1.0

        ranked.append({
            "path": r["path"],
            "name": r["name"],
            "extension": r.get("extension"),
            "modified_at": r.get("modified_at"),
            "total_score": total_score
        })

    ranked.sort(key=lambda x: x["total_score"], reverse=True)
    return ranked[:top_k]


def search(query: str, top_k: int = 5):
    """
    Búsqueda en cascada:
    1. Primero intenta búsqueda estricta (umbral del 70% de palabras clave).
    2. Si no hay resultados, usa BM25 como fallback.
    """
    strict_results = search_strict(query, top_k=top_k)
    if strict_results:  # Si la estricta encuentra algo, la devolvemos directamente
        return strict_results

    return search_bm25_fallback(query, top_k=top_k)  # Si no, fallback a BM25

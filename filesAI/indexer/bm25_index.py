"""
bm25_index.py

Este módulo construye un índice de búsqueda BM25 sobre el contenido de los archivos
guardados en SQLite. BM25 es un algoritmo estándar de recuperación de información que
pondera automáticamente qué palabras son importantes en el corpus.

Funciones principales:
- tokenize(): limpia y divide un texto en palabras.
- build_bm25_index(): lee los archivos de SQLite y construye el índice BM25.
- search_bm25(): recibe una query y devuelve los documentos más relevantes.
"""

import re
from rank_bm25 import BM25Okapi
from filesAI.indexer.database import get_connection
from filesAI.indexer.utils import get_document_preview

def tokenize(text: str) -> list[str]:
    """
    Normaliza un texto: lo pasa a minúsculas, elimina puntuación
    y lo divide en palabras individuales.
    """
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)  # reemplaza puntuación por espacios
    return text.split()


def build_bm25_index():
    """
    Lee todos los archivos con contenido de SQLite y construye un índice BM25.
    El nombre del archivo se repite varias veces para darle más peso en la búsqueda.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT path, name, content FROM files WHERE content != ''")
    files = cursor.fetchall()

    conn.close()

    tokenized_corpus = []
    for path, name, content in files:
        preview = get_document_preview(content)                                                                                                                                               
        text = f"{name} {preview}"
        tokenized_corpus.append(tokenize(text))

    bm25 = BM25Okapi(tokenized_corpus)

    return bm25, files


def search_bm25(bm25, files, query: str, top_k: int = 20):
    """
    Busca documentos relevantes usando un índice BM25 ya construido.
    Recibe el índice y la lista de archivos para evitar reconstruirlo en cada búsqueda.
    """
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)

    results = []
    for i, (path, name, content) in enumerate(files):
        results.append({
            "path": path,
            "name": name,
            "bm25_score": float(scores[i])
        })

    results.sort(key=lambda x: x["bm25_score"], reverse=True)

    return results[:top_k]

import re  # Módulo estándar para trabajar con expresiones regulares

from rank_bm25 import BM25Okapi  # Algoritmo BM25 para búsqueda por palabras clave
from filesAI.indexer.database import get_connection  # Conexión a SQLite


def tokenize(text: str) -> list[str]:
    """
    Normaliza un texto para que BM25 pueda comparar palabras.
    """
    text = text.lower()  # Convertimos a minúsculas para que "Examen" y "examen" sean iguales
    text = re.sub(r"[^\w\s]", " ", text)  # Reemplazamos puntuación por espacios
    return text.split()  # Dividimos el texto en palabras individuales


def build_bm25_index():
    """
    Lee todos los archivos con contenido de SQLite y construye un índice BM25.
    """
    conn = get_connection()  # Abrimos conexión con la base de datos
    cursor = conn.cursor()

    # Seleccionamos solo archivos con contenido extraído
    cursor.execute("SELECT path, name, content FROM files WHERE content != ''")
    files = cursor.fetchall()  # Lista de tuplas (path, name, content)

    conn.close()  # Cerramos la conexión lo antes posible

    tokenized_corpus = []  # Aquí guardaremos cada documento tokenizado
    for path, name, content in files:
        text = f"{name} {content}"  # Combinamos nombre y contenido
        tokenized_corpus.append(tokenize(text))  # Tokenizamos y añadimos al corpus

    bm25 = BM25Okapi(tokenized_corpus)  # Creamos el índice BM25
    return bm25, files  # Devolvemos índice + archivos para poder mapear resultados


def search_bm25(query: str, top_k: int = 20):
    """
    Busca documentos relevantes usando BM25.
    """
    bm25, files = build_bm25_index()  # Construimos el índice

    tokenized_query = tokenize(query)  # Tokenizamos la query igual que los documentos
    scores = bm25.get_scores(tokenized_query)  # Obtenemos puntuación para cada documento

    results = []
    for i, (path, name, content) in enumerate(files):
        results.append({
            "path": path,
            "name": name,
            "bm25_score": float(scores[i])  # Convertimos a float para evitar tipos raros
        })

    results.sort(key=lambda x: x["bm25_score"], reverse=True)  # Ordenamos de mayor a menor
    return results[:top_k]  # Devolvemos solo los top_k mejores

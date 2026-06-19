from filesAI.indexer.embeddings import search_similar_file
from filesAI.indexer.bm25_index import build_bm25_index, search_bm25


def search_hybrid(query: str, top_k: int = 5):
    """
    Búsqueda híbrida que combina:
    - Búsqueda semántica con embeddings
    - Búsqueda por palabras clave con BM25
    """
    # 1. Construir el índice BM25 una sola vez
    bm25, files = build_bm25_index()

    # 2. Buscar con BM25
    bm25_results = search_bm25(bm25, files, query, top_k=20)
    bm25_scores = {}
    file_names = {}

    for result in bm25_results:
        path = result["path"]
        bm25_scores[path] = result["bm25_score"]
        file_names[path] = result["name"]

    # 3. Buscar con embeddings
    semantic_results = search_similar_file(query, max_distance=1.0)

    # 4. Combinar resultados
    combined = {}
    for path, score in bm25_scores.items():
        combined[path] = {"bm25_score": score, "semantic_score": 0.0}

    for metadata, distance in semantic_results:
        path = metadata["path"]
        semantic_score = 1 / (1 + distance)
        if path not in combined:
            combined[path] = {"bm25_score": 0.0, "semantic_score": 0.0}
            file_names[path] = metadata["name"]
        combined[path]["semantic_score"] = semantic_score

    # 5. Calcular puntuación total
    final_results = []
    for path, scores in combined.items():
        name = file_names.get(path, path.split("/")[-1])
        total = scores["bm25_score"] + scores["semantic_score"] * 2
        final_results.append({
            "path": path,
            "name": name,
            "total_score": total,
            "bm25_score": scores["bm25_score"],
            "semantic_score": scores["semantic_score"]
        })

    final_results.sort(key=lambda x: x["total_score"], reverse=True)

    return final_results[:top_k]

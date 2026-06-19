from filesAI.indexer.embeddings import search_similar_file
from filesAI.indexer.bm25_index import build_bm25_index, search_bm25

def search_hybrid(query: str, top_k: int = 5):

    bm25, files = build_bm25_index()

    bm25_scores = {}
    file_names = {}

    for q in queries:
        results = search_bm25(bm25, files, q, top_k=20)
        for result in results:
            path = result["path"]
            score = result["bm25_score"]
            bm25_scores[path] = bm25_scores.get(path, 0) + score
            file_names[path] = result["name"]

    semantic_results = search_similar_file(query, max_distance=1.0)

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

    final_results = []
    for path, scores in combined.items():
        name = file_names.get(path, path.split("/")[-1])
        total = scores["bm25_score"] + scores["semantic_score"]
        final_results.append({
            "path": path,
            "name": name,
            "total_score": total,
            "bm25_score": scores["bm25_score"],
            "semantic_score": scores["semantic_score"]
        })

    final_results.sort(key=lambda x: x["total_score"], reverse=True)

    return filtered[:top_k]
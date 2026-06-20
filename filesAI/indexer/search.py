from filesAI.indexer.text_processing import normalize
from filesAI.indexer.inverted_index import (
    get_candidate_doc_ids,
    get_doc_frequencies,
    get_doc_info,
    get_token_doc_counts,
    get_avg_doc_lengths,
    get_doc_count,
    get_doc_contents,
)
from filesAI.indexer.ranker import rank_documents, compute_proximity_score, PROXIMITY_WEIGHT


def search(query: str, top_k: int = 5):
    """
    Buscador basado en BM25 + índice invertido + stemming.
    Devuelve los top_k documentos más relevantes para la query.
    """
    tokens = normalize(query)

    if not tokens:
        return []

    doc_ids = get_candidate_doc_ids(tokens)
    if not doc_ids:
        return []

    doc_freqs = get_doc_frequencies(doc_ids, tokens)
    token_doc_counts = get_token_doc_counts(tokens)
    avg_lengths = get_avg_doc_lengths()
    N = get_doc_count()

    scores = rank_documents(tokens, doc_freqs, token_doc_counts, avg_lengths, N)

    # Umbral: el documento debe contener al menos el 50% de los tokens de la query.
    min_tokens = max(1, int(len(tokens) * 0.5))
    filtered_scores = {}
    for doc_id, score in scores.items():
        matched = sum(1 for token in tokens if doc_freqs.get(doc_id, {}).get(token, {}).get("content", 0) > 0 or doc_freqs.get(doc_id, {}).get(token, {}).get("name", 0) > 0)
        if matched >= min_tokens:
            filtered_scores[doc_id] = score

    # Añadimos proximidad de palabras a los mejores candidatos.
    sorted_candidates = sorted(filtered_scores.items(), key=lambda x: x[1], reverse=True)
    top_candidates = sorted_candidates[:100]
    candidate_ids = {doc_id for doc_id, _ in top_candidates}
    contents = get_doc_contents(candidate_ids)

    final_scores = {}
    for doc_id, base_score in top_candidates:
        content = contents.get(doc_id, "")
        proximity = compute_proximity_score(content, tokens)
        final_scores[doc_id] = base_score + proximity * PROXIMITY_WEIGHT

    for doc_id, base_score in sorted_candidates[100:]:
        final_scores[doc_id] = base_score

    doc_info = get_doc_info(set(final_scores.keys()))

    results = [
        {
            "path": doc_info[doc_id]["path"],
            "name": doc_info[doc_id]["name"],
            "total_score": score,
        }
        for doc_id, score in final_scores.items()
        if doc_id in doc_info
    ]

    results.sort(key=lambda x: x["total_score"], reverse=True)
    return results[:top_k]

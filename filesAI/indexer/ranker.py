import math

from filesAI.indexer.text_processing import normalize


# Parámetros de BM25.
K1 = 1.5
B = 0.75

# Pesos por campo.
NAME_WEIGHT = 2.0
CONTENT_WEIGHT = 1.0
PROXIMITY_WEIGHT = 5.0


def compute_proximity_score(content: str, tokens: list[str]) -> float:
    """
    Calcula un score de proximidad: cuánto más cerca estén las keywords
    en el contenido, mayor será el score.
    Devuelve un valor entre 0 y 1.
    """
    content_tokens = normalize(content)
    if not content_tokens or not tokens:
        return 0.0

    # Posiciones de cada token en el contenido.
    positions = {}
    for i, token in enumerate(content_tokens):
        if token in tokens:
            positions.setdefault(token, []).append(i)

    # Si no aparecen todos los tokens, no hay proximidad relevante.
    if len(positions) < len(set(tokens)):
        return 0.0

    # Calcular distancia media mínima entre todos los pares de tokens.
    token_list = list(positions.keys())
    total_distance = 0
    pair_count = 0

    for i in range(len(token_list)):
        for j in range(i + 1, len(token_list)):
            pos_i = positions[token_list[i]]
            pos_j = positions[token_list[j]]
            min_dist = min(abs(a - b) for a in pos_i for b in pos_j)
            total_distance += min_dist
            pair_count += 1

    if pair_count == 0:
        return 0.0

    avg_distance = total_distance / pair_count
    # Normalizar: score alto si la distancia media es pequeña.
    return 1.0 / (1.0 + avg_distance / 10.0)


def _idf(n_q: int, N: int) -> float:
    """
    Calcula IDF según la fórmula de BM25.
    n_q: número de documentos que contienen el término.
    N: número total de documentos.
    """
    return math.log((N - n_q + 0.5) / (n_q + 0.5) + 1)


def _bm25_term_score(freq: int, doc_len: int, avg_len: float, idf: float) -> float:
    """
    Calcula el score de un término en un documento según BM25.
    """
    if doc_len == 0 or avg_len == 0:
        return 0.0
    denominator = freq + K1 * (1 - B + B * (doc_len / avg_len))
    return idf * (freq * (K1 + 1)) / denominator


def rank_documents(
    tokens: list[str],
    doc_freqs: dict[int, dict[str, dict[str, int]]],
    token_doc_counts: dict[str, int],
    avg_lengths: dict[str, float],
    N: int
) -> dict[int, float]:
    """
    Calcula el score BM25 combinado para cada documento candidato.

    - doc_freqs: {doc_id: {token: {field: freq}}}
    - token_doc_counts: {token: n_q}
    - avg_lengths: {field: avg_len}
    - N: total de documentos.

    Devuelve {doc_id: score}.
    """
    scores = {}

    avg_name = avg_lengths.get("name", 1.0)
    avg_content = avg_lengths.get("content", 1.0)

    for doc_id, freqs in doc_freqs.items():
        name_len = sum(freqs[token]["name"] for token in freqs)
        content_len = sum(freqs[token]["content"] for token in freqs)

        name_score = 0.0
        content_score = 0.0

        for token in tokens:
            n_q = token_doc_counts.get(token, 0)
            if n_q == 0:
                continue

            idf = _idf(n_q, N)
            token_freq_name = freqs.get(token, {}).get("name", 0)
            token_freq_content = freqs.get(token, {}).get("content", 0)

            name_score += _bm25_term_score(token_freq_name, name_len, avg_name, idf)
            content_score += _bm25_term_score(token_freq_content, content_len, avg_content, idf)

        total_score = name_score * NAME_WEIGHT + content_score * CONTENT_WEIGHT
        if total_score > 0:
            scores[doc_id] = total_score

    return scores

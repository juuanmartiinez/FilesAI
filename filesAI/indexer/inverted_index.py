from collections import defaultdict

from filesAI.indexer.database import get_connection
from filesAI.indexer.text_processing import normalize


def init_index_tables():
    """
    Crea las tablas necesarias para el índice invertido.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inverted_index (
            token TEXT NOT NULL,
            doc_id INTEGER NOT NULL,
            field TEXT NOT NULL,
            frequency INTEGER NOT NULL,
            PRIMARY KEY (token, doc_id, field)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS index_metadata (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


def clear_index():
    """
    Elimina todos los datos del índice invertido.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inverted_index")
    cursor.execute("DELETE FROM index_metadata")
    conn.commit()
    conn.close()


def build_index():
    """
    Construye el índice invertido a partir de todos los archivos indexados.
    """
    init_index_tables()
    clear_index()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, content FROM files WHERE content != ''")
    files = cursor.fetchall()

    index_data = defaultdict(lambda: defaultdict(lambda: {"name": 0, "content": 0}))

    for doc_id, name, content in files:
        name_tokens = normalize(name)
        content_tokens = normalize(content)

        for token in name_tokens:
            index_data[token][doc_id]["name"] += 1

        for token in content_tokens:
            index_data[token][doc_id]["content"] += 1

    inserts = []
    for token, docs in index_data.items():
        for doc_id, fields in docs.items():
            for field, freq in fields.items():
                if freq > 0:
                    inserts.append((token, doc_id, field, freq))

    cursor.executemany(
        "INSERT INTO inverted_index (token, doc_id, field, frequency) VALUES (?, ?, ?, ?)",
        inserts
    )

    cursor.execute(
        "INSERT OR REPLACE INTO index_metadata (key, value) VALUES (?, ?)",
        ("doc_count", str(len(files)))
    )

    conn.commit()
    conn.close()


def get_doc_count() -> int:
    """
    Devuelve el número de documentos indexados según la metadata.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM index_metadata WHERE key = 'doc_count'")
    row = cursor.fetchone()
    conn.close()
    return int(row[0]) if row else 0


def get_candidate_doc_ids(tokens: list[str]) -> set[int]:
    """
    Devuelve los IDs de documentos que contienen al menos uno de los tokens.
    """
    if not tokens:
        return set()

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ", ".join("?" for _ in tokens)
    cursor.execute(
        f"SELECT DISTINCT doc_id FROM inverted_index WHERE token IN ({placeholders})",
        tokens
    )

    doc_ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return doc_ids


def get_doc_frequencies(doc_ids: set[int], tokens: list[str]) -> dict[int, dict[str, dict[str, int]]]:
    """
    Devuelve para cada documento la frecuencia de cada token en name y content.
    Estructura: {doc_id: {token: {field: freq}}}
    """
    if not doc_ids or not tokens:
        return {}

    conn = get_connection()
    cursor = conn.cursor()

    placeholders_doc = ", ".join("?" for _ in doc_ids)
    placeholders_token = ", ".join("?" for _ in tokens)

    cursor.execute(
        f"""
        SELECT doc_id, token, field, frequency
        FROM inverted_index
        WHERE doc_id IN ({placeholders_doc}) AND token IN ({placeholders_token})
        """,
        list(doc_ids) + tokens
    )

    freqs = defaultdict(lambda: defaultdict(lambda: {"name": 0, "content": 0}))
    for doc_id, token, field, freq in cursor.fetchall():
        freqs[doc_id][token][field] = freq

    conn.close()
    return freqs


def get_doc_info(doc_ids: set[int]) -> dict[int, dict]:
    """
    Devuelve la información básica de los documentos: path y name.
    """
    if not doc_ids:
        return {}

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ", ".join("?" for _ in doc_ids)
    cursor.execute(
        f"SELECT id, path, name FROM files WHERE id IN ({placeholders})",
        list(doc_ids)
    )

    info = {
        row[0]: {"path": row[1], "name": row[2]}
        for row in cursor.fetchall()
    }

    conn.close()
    return info


def get_token_doc_counts(tokens: list[str]) -> dict[str, int]:
    """
    Devuelve cuántos documentos distintos contienen cada token.
    """
    if not tokens:
        return {}

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ", ".join("?" for _ in tokens)
    cursor.execute(
        f"""
        SELECT token, COUNT(DISTINCT doc_id)
        FROM inverted_index
        WHERE token IN ({placeholders})
        GROUP BY token
        """,
        tokens
    )

    counts = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return counts


def get_avg_doc_lengths() -> dict[str, float]:
    """
    Devuelve la longitud media de name y content de todos los documentos.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT field, AVG(total)
        FROM (
            SELECT doc_id, field, SUM(frequency) as total
            FROM inverted_index
            GROUP BY doc_id, field
        )
        GROUP BY field
    """)

    avgs = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return avgs


def get_doc_contents(doc_ids: set[int]) -> dict[int, str]:
    """
    Devuelve el contenido de los documentos indicados.
    """
    if not doc_ids:
        return {}

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ", ".join("?" for _ in doc_ids)
    cursor.execute(
        f"SELECT id, content FROM files WHERE id IN ({placeholders})",
        list(doc_ids)
    )

    contents = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return contents

import re

from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer


# Stopwords en español e inglés.
STOPWORDS = set(stopwords.words("spanish")) | set(stopwords.words("english"))

# Stemmers para español e inglés.
STEMMERS = {
    "spanish": SnowballStemmer("spanish"),
    "english": SnowballStemmer("english"),
}

# Por defecto usamos el stemmer español; si una palabra no se puede stemmizar
# en español, intentamos en inglés.
DEFAULT_STEMMER = STEMMERS["spanish"]


def tokenize(text: str) -> list[str]:
    """
    Pasa a minúsculas, elimina puntuación y divide en palabras.
    """
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return text.split()


def remove_stopwords(tokens: list[str]) -> list[str]:
    """
    Elimina palabras vacías en español e inglés.
    """
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def stem(tokens: list[str]) -> list[str]:
    """
    Aplica stemming a cada token.
    """
    result = []
    for token in tokens:
        stemmed = DEFAULT_STEMMER.stem(token)
        # Si el stemmer español devuelve la misma palabra, probamos inglés.
        if stemmed == token:
            stemmed = STEMMERS["english"].stem(token)
        result.append(stemmed)
    return result


def normalize(text: str) -> list[str]:
    """
    Pipeline completo: tokenizar -> quitar stopwords -> stem.
    """
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens)
    tokens = stem(tokens)
    return tokens

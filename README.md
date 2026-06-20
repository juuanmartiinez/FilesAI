# FileAI

Buscador local de archivos por contenido. Indexa los archivos de la carpeta personal del usuario y permite buscar dentro de ellos usando lenguaje natural.

> Estado actual: proyecto en desarrollo. El motor de búsqueda ya funciona con técnicas clásicas de recuperación de información.

## Qué hace ahora

1. **Escaneo**: recorre `/home/juan` (u otra carpeta personal) y extrae metadatos de cada archivo.
   - Ignora directorios ocultos, cachés, entornos virtuales, `.git`, `node_modules`, etc.
2. **Indexación**: guarda los metadatos y el texto extraído en una base de datos SQLite local (`data/fileai.db`).
   - Soporta extracción de texto de `.pdf`, `.txt` y `.docx`.
   - Mantiene el índice sincronizado: actualiza archivos modificados y elimina los que ya no existen.
3. **Motor de búsqueda**: usa un buscador clásico por relevancia inspirado en los buscadores web.
   - **Índice invertido**: localiza rápidamente los documentos que contienen las palabras de la query.
   - **Stemming**: entiende variantes de la misma palabra (`examen`, `exámenes`, `examenes`).
   - **Stopwords**: ignora palabras vacías en español e inglés.
   - **BM25**: puntúa documentos según frecuencia e importancia de las palabras.
   - **Ponderación por campo**: el nombre del archivo pesa más que el contenido.
   - **Proximidad de palabras**: favorece documentos donde las palabras de la query aparecen cerca unas de otras.
   - **Umbral mínimo**: un documento debe contener al menos el 50% de las palabras de la query para aparecer.

## Cómo usarlo

### Instalación

```bash
cd ~/Documents/proyectosPersonales/FilesAI
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Indexar archivos

```bash
source .venv/bin/activate
python index.py
```

### Buscar

Edita `test.py` con la query que quieras y ejecútalo:

```bash
source .venv/bin/activate
python test.py
```

Ejemplo de query:

```python
results = search("examenes de algoritmos y estructuras de datos", top_k=10)
```

## Estructura del proyecto

```
FilesAI/
├── filesAI/
│   ├── indexer/
│   │   ├── database.py          # Gestión de SQLite
│   │   ├── inverted_index.py    # Índice invertido para búsquedas rápidas
│   │   ├── ranker.py            # Puntuación BM25 y proximidad
│   │   ├── search.py            # API principal de búsqueda
│   │   └── text_processing.py   # Tokenización, stopwords y stemming
│   ├── scanner/
│   │   └── walker.py            # Escaneo de archivos
│   └── extractor/
│       └── ...                  # Extracción de texto por formato
├── data/
│   └── fileai.db                # Base de datos local (ignorada por Git)
├── index.py                     # Script para reindexar
├── test.py                      # Script de prueba de búsqueda
└── requirements.txt
```

## Decisiones técnicas

- **Sin LLM en runtime**: no se usan modelos de lenguaje grandes para las búsquedas por consumo y temperatura del equipo.
- **Sin embeddings**: la búsqueda se basa en técnicas clásicas de recuperación de información.
- **Base de datos local**: SQLite en `data/fileai.db`, no se sube a Git.

## Limitaciones conocidas

- La búsqueda puede generar falsos positivos con palabras ambiguas muy comunes (p. ej., `datos` puede aparecer tanto en documentos de bases de datos como de estructuras de datos).
- Solo se indexan archivos cuyo texto se puede extraer (`pdf`, `txt`, `docx`).
- El índice completo se reconstruye al ejecutar `index.py`.
- No se corrigen faltas de ortografía ni se usan sinónimos de forma explícita (aún).

## Próximos pasos

- Recoger feedback real de usuarios para ajustar pesos y umbral.
- Evaluar sinónimos generales y corrección ortográfica ligera.
- Considerar un modelo de embeddings ligero si el motor clásico llega a su techo.

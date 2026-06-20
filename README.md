# FileAI

Buscador local de archivos por contenido. Indexa los archivos de la carpeta personal del usuario y permite buscar dentro de ellos usando palabras clave.

> Estado actual: proyecto en desarrollo. La búsqueda es funcional pero aún se está refinando.

## Qué hace ahora

1. **Escaneo**: recorre `/home/juan` (u otra carpeta personal) y extrae metadatos de cada archivo.
   - Ignora directorios ocultos, cachés, entornos virtuales, `.git`, `node_modules`, etc.
2. **Indexación**: guarda los metadatos y el texto extraído en una base de datos SQLite local (`data/fileai.db`).
   - Soporta extracción de texto de `.pdf`, `.txt` y `.docx`.
   - Mantiene el índice sincronizado: actualiza archivos modificados y elimina los que ya no existen.
3. **Búsqueda estricta**: encuentra archivos que contienen al menos el 70% de las palabras clave de la query.
   - Usa coincidencia de palabra completa.
   - Ordena por frecuencia ponderada (IDF), coincidencias en el nombre y frases exactas.

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
results = search("examenes de algoritmos y estructuras de datos II", top_k=10)
```

## Estructura del proyecto

```
FilesAI/
├── filesAI/
│   ├── indexer/
│   │   ├── database.py   # Gestión de SQLite
│   │   └── search.py     # Algoritmo de búsqueda estricta
│   ├── scanner/
│   │   └── walker.py     # Escaneo de archivos
│   └── extractor/
│       └── ...           # Extracción de texto por formato
├── data/
│   └── fileai.db         # Base de datos local (ignorada por Git)
├── index.py              # Script para reindexar
├── test.py               # Script de prueba de búsqueda
└── requirements.txt
```

## Decisiones técnicas

- **Sin LLM en runtime**: no se usan modelos de lenguaje para las búsquedas por consumo y temperatura del equipo.
- **Sin embeddings**: la búsqueda es puramente por palabras clave.
- **Base de datos local**: SQLite en `data/fileai.db`, no se sube a Git.

## Limitaciones conocidas

- La búsqueda aún genera falsos positivos con palabras comunes (p. ej., `datos` puede aparecer en documentos de bases de datos).
- Solo se indexan archivos cuyo texto se puede extraer (`pdf`, `txt`, `docx`).
- El índice completo se reconstruye al ejecutar `index.py`.

## Próximos pasos

- Refinar el algoritmo de búsqueda estricta en `search.py` para reducir ruido y mejorar el orden de resultados.
- Evaluar si se añaden mejoras como sinónimos, ponderación por campo o filtros por tipo de archivo.

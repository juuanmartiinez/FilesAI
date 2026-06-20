from filesAI.scanner.walker import scan_all  # Escaneo de archivos
from filesAI.indexer.database import (
    init_db,
    insert_files,
    update_sql_content,
    get_all_paths,
    delete_files_not_in,
)  # Base de datos
from filesAI.extractor.extractor import extract_content  # Extracción de texto


if __name__ == "__main__":

    print("Reindexando archivos...")

    init_db()  # Creamos/recreamos la tabla files

    files = scan_all()  # Escaneamos todos los directorios configurados
    scanned_paths = {file["path"] for file in files}

    insert_files(files)  # Guardamos/actualizamos metadatos en SQLite

    # Eliminamos del índice archivos que ya no existen en disco
    indexed_paths = get_all_paths()
    deleted = delete_files_not_in(scanned_paths)
    if deleted:
        print(f"Eliminados {deleted} archivos que ya no existen.")

    # Extraemos texto de los archivos escaneados
    for file in files:
        content = extract_content(file["path"])
        if content:
            update_sql_content(file["path"], content)

    print(f"Indexación completada: {len(files)} archivos indexados.")

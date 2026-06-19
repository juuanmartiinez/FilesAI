from filesAI.scanner.walker import get_download_path, scan_directory  # Escaneo de archivos
from filesAI.indexer.database import init_db, insert_files, update_sql_content  # Base de datos
from filesAI.extractor.extractor import extract_content  # Extracción de texto


if __name__ == "__main__":
    
    print("Reindexando archivos...")

    init_db()  # Creamos/recreamos la tabla files

    downloads = get_download_path()  # Obtenemos la ruta de Downloads
    files = scan_directory(downloads)  # Escaneamos todos los archivos

    insert_files(files)  # Guardamos metadatos en SQLite

    for file in files:
        content = extract_content(file["path"])  # Extraemos texto según la extensión
        if content:
            update_sql_content(file["path"], content)  # Guardamos el contenido en SQLite

    print("Indexación completada.")

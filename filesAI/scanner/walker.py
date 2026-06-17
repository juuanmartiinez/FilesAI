from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes

# Paso 1: Obtener la ruta de donde vamos a operar (de momento en Downloads/)

def get_download_path():
    
    downloadPath = Path.home() / "Downloads"

    if downloadPath.exists():                   # comprobamos si exite la ruta
        return downloadPath
    else:
        return "Error while finding the path"
    
# Paso 2: Paso 2: Recorrer todos los archivos de la ruta de Downloads

def scan_directory(directory : Path):
    
    files = []                                  # aqui guardaremos los metadatos de los ficheros obtenidos

    for file in directory.rglob("*"):           # recorremos todo Downloads y añadimos la info de cada fichero al diccionario

        if any(part.startswith(".") for part in file.parts):        # si es oculto, continuamos                                                                                                                                                     
            continue

        if file.is_file():
            file_info = {
                "path" : str(file),
                "name" : file.name,
                "extension" : file.suffix,
                "size" : file.stat().st_size,
                "modified_at" :  datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                "mime_type": mimetypes.guess_type(str(file))[0] or "unknown",                       # nos indica que tipo de archivo es 
                "hash" : get_hash(file),
            }
            files.append(file_info)
    return files

def get_hash(file_path : Path, algorithm="sha256") -> str:          # calculamos un hash para cada fichero
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()
    

if __name__ == "__main__":

    downloads = get_download_path()
    files = scan_directory(downloads)

    for file in files:
        print(file)
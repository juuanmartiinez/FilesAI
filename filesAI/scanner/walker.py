from pathlib import Path
from datetime import datetime
import hashlib
import mimetypes


# Directorios y nombres que nunca queremos indexar.
EXCLUDED_NAMES = {
    # Entornos virtuales y caché de Python
    ".venv", "venv", "env",
    "__pycache__", "node_modules",
    # Control de versiones
    ".git", ".svn", ".hg",
    # Cachés y configuraciones del sistema/usuario
    ".cache", ".config", ".local", ".kimi-code",
    ".mozilla", ".thunderbird", ".var", ".wine",
    ".npm", ".p2", ".ipython", ".jupyter", ".sage",
    ".vscode", ".vscode-shared", ".eclipse", ".java",
    ".pki", ".themes", ".icons", ".gnupg", ".ssh",
    ".gphoto", ".swt", ".dotnet", ".copilot",
    # Archivos de apps específicas grandes
    ".sqldeveloper", ".wine", ".var",
}


def get_scan_paths() -> list[Path]:
    """
    Devuelve la lista de directorios raíz a escanear.
    Por defecto: la carpeta personal del usuario.
    """
    return [Path.home()]


def is_excluded(path: Path) -> bool:
    """
    Determina si una ruta debe ignorarse.
    - Directorios ocultos (empiezan por '.').
    - Nombres en EXCLUDED_NAMES.
    """
    for part in path.parts:
        if part.startswith(".") and part != ".":
            return True
        if part in EXCLUDED_NAMES:
            return True
    return False


def scan_directory(directory: Path) -> list[dict]:
    """
    Escanea recursivamente un directorio y devuelve metadatos de los archivos.
    Ignora rutas excluidas y maneja errores de permisos.
    """
    files = []

    try:
        iterator = directory.rglob("*")
    except OSError as e:
        print(f"No se pudo acceder a {directory}: {e}")
        return files

    for file in iterator:
        try:
            if is_excluded(file):
                continue

            if file.is_file():
                file_info = {
                    "path": str(file),
                    "name": file.name,
                    "extension": file.suffix,
                    "size": file.stat().st_size,
                    "modified_at": datetime.fromtimestamp(file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "mime_type": mimetypes.guess_type(str(file))[0] or "unknown",
                    "hash": get_hash(file),
                }
                files.append(file_info)
        except (OSError, PermissionError) as e:
            # Archivo o directorio al que no podemos acceder: lo saltamos.
            continue

    return files


def scan_all() -> list[dict]:
    """
    Escanea todos los directorios configurados en get_scan_paths().
    """
    all_files = []
    for directory in get_scan_paths():
        print(f"Escaneando {directory}...")
        all_files.extend(scan_directory(directory))
    return all_files


def get_hash(file_path: Path, algorithm="sha256") -> str:
    """
    Calcula un hash para cada fichero.
    Si no se puede leer, devuelve una cadena vacía.
    """
    try:
        hasher = hashlib.new(algorithm)
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except (OSError, PermissionError):
        return ""


if __name__ == "__main__":
    files = scan_all()
    for file in files[:20]:
        print(file)
    print(f"\nTotal archivos encontrados: {len(files)}")

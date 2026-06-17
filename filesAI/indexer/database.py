from pathlib import Path
import sqlite3

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"       # .resolve() para saber donde esta database.py                                                                                                                                       
DATA_DIR.mkdir(exist_ok=True)                                                                                                                                                                                                     
DB_PATH = DATA_DIR / "fileai.db"                                        # construye la ruta donde estara la base de datos

def get_connection():
    return sqlite3.connect(DB_PATH)                                     # abrir/crear la base de datos                        

def init_db():

    conn = sqlite3.connect(DB_PATH)                                                                                                                                                                                   
    cursor = conn.cursor()                                              # crear el objeto para ejecutar SQL                                                                                                                                                          

    # execute(...) siempre que queramos ejecutar comandos en SQL

    cursor.execute("""                                                                                                                                                                                                                                   
            CREATE TABLE IF NOT EXISTS files (                                                                                                                                                                   
                id INTEGER PRIMARY KEY AUTOINCREMENT,                                                                                                                                                            
                path TEXT UNIQUE NOT NULL,                                                                                                                                                                       
                name TEXT NOT NULL,                                                                                                                                                                              
                extension TEXT,                                                                                                                                                                                  
                size INTEGER,                                                                                                                                                                                    
                modified_at TEXT,                                                                                                                                                                                
                mime_type TEXT,                                                                                                                                                                                  
                hash TEXT,                                                                                                                                                                                       
                scanned_at TEXT DEFAULT CURRENT_TIMESTAMP                                                                                                                                                        
            );                                                                                                                                                                                                   
        """)                                                                                                                                                                                                     
                                                                                                                                                                                                                  
    conn.commit()     # guardar cambios                                                                                                                                                                                          
    conn.close()      # cerrar conexion

def insert_files(files):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for file in files:
        cursor.execute("""                                                                                                                                                                                   
                INSERT OR IGNORE INTO files                                                                                                                                                                      
                (path, name, extension, size, modified_at, mime_type, hash)                                                                                                                                      
                VALUES (?, ?, ?, ?, ?, ?, ?)                                                                                                                                                                     
            """, (                                                                                                                                                                                               
                file["path"],                                                                                                                                                                                    
                file["name"],                                                                                                                                                                                    
                file["extension"],                                                                                                                                                                               
                file["size"],                                                                                                                                                                                    
                file["modified_at"],                                                                                                                                                                             
                file["mime_type"],                                                                                                                                                                               
                file["hash"],                                                                                                                                                                                    
            ))                                                                                                                                                                                                   
                                                                                                                                                                                                                  
    conn.commit()                                                                                                                                                                                            
    conn.close()

def count_files():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM files")
    result = cursor.fetchone()                      # leer el resultado de una consulta

    conn.close()

    return result[0]
import chromadb
import ollama
import sqlite3

from filesAI.indexer.database import get_connection

# Creamos conexiones con la ChromaBD, obtenemos la coleccion que guarda el vector y calculamos el vector

def get_chroma_client():    
    return chromadb.PersistentClient(path="data/chroma")        # guarda los datos en la carpeta data/chroma

def get_collection(client):       # obtiene/crea la coleccion donde guardaremos los vectores
    return client.get_or_create_collection(name="files")

def generate_embedding(text: str):        # generamos los vectores que representaran el texto que analizamos
    response = ollama.embed(
        model="nomic-embed-text",           # este modelo procesa el texto y nos devuelve el vector
        input=text
    )
    return response.embeddings[0]

def index_files():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(                                                                                                                                                                                          
            "SELECT id, path, name, content FROM files WHERE content != ''"                                                                                                                                      
        )
    files = cursor.fetchall()

    client = get_chroma_client()
    collection = get_collection(client)

    conn.close()

    for file_id, file_path, file_name, file_content in files:                  
        embedding = generate_embedding(file_content)

        collection.add(
            ids=[str(file_id)],
            documents=[file_content],
            metadatas=[{"path" : file_path, "name" : file_name}],
            embeddings = [embedding]
        )
        print(f"Indexado: {file_name}")

def search_similar_file(query : str, max_distance: float):
    query_embedding = generate_embedding(query)

    client = get_chroma_client()
    collection = get_collection(client)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results= 50
    )

    filtered = []

    for metadata, distance in zip(results["metadatas"][0], results["distances"][0]):
        if distance <= max_distance:
            filtered.append((metadata, distance))

    return filtered

def search_hybrid(query : str, max_distance : float, top_k : int):
    keywords = [word.lower() for word in query.split() if len(word) > 2]                                                                                                                                     
    scores = {}
    
    semantic_results = search_similar_file(query, max_distance)

    for metadata, distance in semantic_results:
        path = metadata["path"]
        name = metadata["name"]

        semantic_score = 1 / (1 + distance)

        scores[path] = {
            "name": name,
            "path": path,
            "semantic_score" : semantic_score,
            "keyword_score" : 0.0,
            "distance" : distance,
        }
    
    # Busqueda por palabras clave

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT path, name, content FROM files WHERE content != ''")
    files = cursor.fetchall()

    conn.close()

    for path, name, content in files:
        path_lower = path.lower()                                                                                                                                                                            
        name_lower = name.lower()                                                                                                                                                                            
        content_lower = content.lower() if content else ""

        keyword_score = 0.0

        for keyword in keywords:
            if keyword in name_lower:
                keyword_score += 2.0
            elif keyword in content_lower:
                keyword_score += 1.0 

        if keyword_score > 0:
            if path not in scores:                                                                                                                                                                           
                    scores[path] = {                                                                                                                                                                             
                        "name": name,                                                                                                                                                                            
                        "path": path,                                                                                                                                                                            
                        "semantic_score": 0.0,                                                                                                                                                                   
                        "keyword_score": 0.0,                                                                                                                                                                    
                        "distance": None                                                                                                                                                                         
                    }                                                                                                                                                                                            
            scores[path]["keyword_score"] += keyword_score

    # Combinamos resultados 

    results = []

    for item in scores.values():
        total_score = item["semantic_score"] + item["keyword_score"]
        item["total_score"] = total_score
        results.append(item)
    
    return results[:top_k]
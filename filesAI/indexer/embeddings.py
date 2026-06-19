import chromadb
import ollama

from filesAI.indexer.database import get_connection
from filesAI.indexer.utils import get_document_preview

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

        preview = get_document_preview(file_content)
        embedding = generate_embedding(preview)

        collection.add(
            ids=[str(file_id)],
            documents=[preview],
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
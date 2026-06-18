from filesAI.indexer.embeddings import search_hybrid

query = "AED II"
results = search_hybrid(query, max_distance=0.75, top_k=10)

print("Resultados para: " + query)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['name']}")                                                                                                                                                                          
    print(f"   Puntuación total: {result['total_score']:.3f}")                                                                                                                                               
    print(f"   Semántica: {result['semantic_score']:.3f}")                                                                                                                                                   
    print(f"   Palabras clave: {result['keyword_score']:.3f}")                                                                                                                                               
    print(f"   Distancia: {result['distance']}")                                                                                                                                                             
    print()
from filesAI.indexer.search import search  # Función principal de búsqueda

results = search("", top_k=10)  # Lanzamos una búsqueda de prueba

for i, result in enumerate(results, 1):
    print(f"{i}. {result['name']}")
    print(f"   Score: {result['total_score']:.3f}")
    print()

from insurance_underwriter.core.rag_service import PolicyRAGService

# Initialize RAG service
rag = PolicyRAGService()

# Test query
test_query = "age band base morbidity rate premium calculation age 30"

print("Testing ChromaDB retrieval...")
print(f"Query: {test_query}\n")

results = rag.query_policy_rules(test_query, n_results=5)

print(f"Found {len(results)} results:\n")
for i, result in enumerate(results, 1):
    print(f"--- Result {i} ---")
    print(f"Content: {result['content'][:200]}...")  # First 200 chars
    print(f"Distance: {result['distance']}")
    print()

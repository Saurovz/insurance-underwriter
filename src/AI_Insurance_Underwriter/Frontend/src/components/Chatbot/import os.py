import chromadb
from chromadb.config import Settings

chroma_db_path = r"D:\Ai_React\insurance-underwriter\src\insurance_underwriter\chroma_db"
chroma_client = chromadb.PersistentClient(
    path=chroma_db_path,
    settings=Settings(anonymized_telemetry=False)
)

# List all collections
collections = chroma_client.list_collections()
print(f"✅ Found {len(collections)} collection(s):")
for col in collections:
    count = col.count()
    print(f"  - {col.name}: {count} documents")

# Check policy_rules specifically
try:
    policy_col = chroma_client.get_collection("policy_rules")
    count = policy_col.count()
    if count > 0:
        print(f"\n✅ 'policy_rules' collection has {count} documents - GOOD!")
    else:
        print(f"\n❌ 'policy_rules' collection exists but is EMPTY!")
except Exception as e:
    print(f"\n❌ 'policy_rules' collection NOT FOUND! Error: {e}")

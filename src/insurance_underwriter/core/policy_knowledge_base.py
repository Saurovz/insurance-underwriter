import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import chromadb
from chromadb.config import Settings


class PolicyKnowledgeBase:
    
    def __init__(self, 
                 db_path: str = "./chroma_db",
                 collection_name: str = "policy_rules",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the Policy Knowledge Base.
        
        Args:
            db_path: Path to store ChromaDB (will be created in project root)
            collection_name: Name of the ChromaDB collection
            embedding_model: HuggingFace embedding model name
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize embeddings
        print(f"🔄 Loading embedding model: {embedding_model}...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
    def load_and_index_policy(self, policy_pdf_path: str, force_reload: bool = False):

        # Check if collection already exists
        existing_collections = [col.name for col in self.client.list_collections()]
        
        if self.collection_name in existing_collections:
            if force_reload:
                print(f"🗑️  Deleting existing collection: {self.collection_name}")
                self.client.delete_collection(self.collection_name)
            else:
                print(f"✅ Policy knowledge base already exists. Skipping indexing.")
                return
        
        print(f"\n📄 Loading policy PDF from: {policy_pdf_path}")
        
        # Load PDF
        loader = PyPDFLoader(policy_pdf_path)
        documents = loader.load()
        print(f"   Loaded {len(documents)} pages from policy PDF")
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # Adjust based on your needs
            chunk_overlap=200,  # Overlap to maintain context
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        print(f"   Created {len(chunks)} chunks from policy document")
        
        # Prepare data for ChromaDB
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [
            {
                "page": chunk.metadata.get("page", 0),
                "source": chunk.metadata.get("source", "policy"),
                "chunk_id": i
            }
            for i, chunk in enumerate(chunks)
        ]
        ids = [f"policy_chunk_{i}" for i in range(len(chunks))]
        
        # Create embeddings and store
        print(f"🔄 Creating embeddings and storing in ChromaDB...")
        
        # Get or create collection
        collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Health Insurance Policy Rules and Regulations"}
        )
        
        # Add documents in batches (ChromaDB handles embedding automatically if we pass embedding function)
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            batch_metadatas = metadatas[i:i+batch_size]
            batch_ids = ids[i:i+batch_size]
            
            # Generate embeddings
            batch_embeddings = self.embeddings.embed_documents(batch_texts)
            
            collection.add(
                documents=batch_texts,
                metadatas=batch_metadatas,
                ids=batch_ids,
                embeddings=batch_embeddings
            )
            
            print(f"   Processed batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
        
        print(f"✅ Policy knowledge base created successfully!")
        print(f"   Database location: {self.db_path}")
        print(f"   Total chunks indexed: {len(texts)}\n")
    
    def get_collection(self):
        """Get the policy rules collection."""
        return self.client.get_collection(self.collection_name)


def setup_policy_knowledge_base(policy_pdf_path: str, force_reload: bool = False):
    """
    Utility function to set up the policy knowledge base.
    Run this once to index your policy PDF.
    
    Args:
        policy_pdf_path: Path to Policy-Rules-and-Regulations.pdf
        force_reload: Force recreation of the database
    """
    kb = PolicyKnowledgeBase()
    kb.load_and_index_policy(policy_pdf_path, force_reload)
    return kb


if __name__ == "__main__":
    # Run this script once to create the knowledge base
    POLICY_PDF_PATH = "D:\AI_HealthCare\insurance-underwriter\src\insurance_underwriter\Policy_Doc\Health Insurance Policy Rules & Regulations 2.pdf"
    
    print("=" * 70)
    print("🏥 SETTING UP POLICY KNOWLEDGE BASE")
    print("=" * 70)
    
    setup_policy_knowledge_base(POLICY_PDF_PATH, force_reload=False)

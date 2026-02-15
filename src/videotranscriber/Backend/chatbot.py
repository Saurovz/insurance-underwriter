import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Import LangChain for conversational models
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_core.messages import HumanMessage

load_dotenv()

class RAGChatbot:
    """RAG-based chatbot for patient transcription queries"""
    
    def __init__(self):
        # Initialize sentence transformer for embeddings
        print("🔄 Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Embedding model loaded")
        
        # Initialize ChromaDB with NEW API (updated for 2026)
        print("🔄 Initializing ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(
            path="./chroma_db"
        )
        print("✓ ChromaDB initialized")
        
        # HuggingFace API setup with CONVERSATIONAL task
        self.hf_api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN") or os.getenv("HUGGINGFACE_API_KEY")
        
        # Use conversational model (2026 compatible)
        self.llm_model = "mistralai/Mistral-7B-Instruct-v0.2"
        
        # Initialize LangChain conversational model
        print(f"🔄 Initializing conversational LLM: {self.llm_model}")
        try:
            llm = HuggingFaceEndpoint(
                repo_id=self.llm_model,
                task="conversational",  # KEY CHANGE: Use conversational task
                huggingfacehub_api_token=self.hf_api_key,
                temperature=0.7,
                max_new_tokens=300
            )
            self.chat_model = ChatHuggingFace(llm=llm)
            print(f"✓ LLM initialized: {self.llm_model}")
        except Exception as e:
            print(f"⚠️ LLM initialization failed: {e}")
            self.chat_model = None
        
    def create_patient_collection(self, patient_id: str) -> chromadb.Collection:
        """Create or get a collection for a specific patient"""
        collection_name = f"patient_{patient_id}"
        
        # Delete existing collection if it exists (fresh start per session)
        try:
            self.chroma_client.delete_collection(name=collection_name)
        except:
            pass
        
        # Create new collection
        collection = self.chroma_client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        print(f"✓ Created collection for {patient_id}")
        return collection
    
    def chunk_text(self, text: str, chunk_size: int = 200) -> List[str]:
        """Split text into overlapping chunks for better context"""
        words = text.split()
        chunks = []
        
        if len(words) <= chunk_size:
            return [text]  # Return as single chunk if small enough
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size + 50])  # 50 word overlap
            if chunk.strip():  # Only add non-empty chunks
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def add_patient_transcription(self, patient_id: str, transcription: str, patient_info: Dict) -> bool:
        """Add patient transcription to ChromaDB with embeddings"""
        try:
            print(f"📝 Adding transcription for {patient_id} to vector database...")
            
            # Validate input
            if not transcription or not transcription.strip():
                print("⚠️ Empty transcription, skipping ChromaDB")
                return False
            
            # Create collection
            collection = self.create_patient_collection(patient_id)
            
            # Chunk the transcription
            chunks = self.chunk_text(transcription)
            print(f"📄 Split into {len(chunks)} chunks")
            
            # Generate embeddings
            print("🔄 Generating embeddings...")
            embeddings = self.embedding_model.encode(chunks).tolist()
            print(f"✓ Generated {len(embeddings)} embeddings")
            
            # Prepare metadata
            metadatas = [
                {
                    "patient_id": patient_id,
                    "patient_name": str(patient_info.get("name", "N/A")),
                    "patient_age": str(patient_info.get("age", "N/A")),
                    "chunk_index": str(i)
                }
                for i in range(len(chunks))
            ]
            
            # Add to ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=[f"{patient_id}_chunk_{i}" for i in range(len(chunks))]
            )
            
            print(f"✓ Added {len(chunks)} chunks to vector database")
            return True
            
        except Exception as e:
            print(f"❌ Error adding to ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def query_patient_data(self, patient_id: str, question: str, top_k: int = 3) -> List[str]:
        """Query ChromaDB for relevant context"""
        try:
            collection_name = f"patient_{patient_id}"
            collection = self.chroma_client.get_collection(name=collection_name)
            
            # Generate query embedding
            print(f"🔍 Searching for: {question}")
            query_embedding = self.embedding_model.encode([question]).tolist()
            
            # Search ChromaDB
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            # Extract relevant documents
            documents = results['documents'][0] if results['documents'] else []
            
            print(f"✓ Retrieved {len(documents)} relevant chunks")
            return documents
            
        except Exception as e:
            print(f"❌ Error querying ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def call_huggingface_llm(self, prompt: str) -> Optional[str]:
        """Call HuggingFace LLM using conversational task (2026 compatible)"""
        
        if not self.chat_model:
            print("⚠️ LLM not available")
            return None
        
        try:
            print(f"🔄 Calling conversational LLM...")
            
            # Create message for conversational model
            messages = [HumanMessage(content=prompt)]
            
            # Invoke the chat model
            response = self.chat_model.invoke(messages)
            
            if response and hasattr(response, 'content'):
                answer = response.content.strip()
                if answer:
                    print("✓ LLM response received")
                    return answer
            
            print("⚠️ LLM returned empty response")
            return None
            
        except Exception as e:
            print(f"⚠️ LLM error: {e}")
            return None
    
    def generate_answer(self, patient_id: str, question: str, patient_info: Dict) -> str:
        """Generate answer using RAG pipeline with LLM"""
        try:
            print(f"🤖 Processing question: {question}")
            
            # Step 1: Retrieve relevant context from ChromaDB
            relevant_chunks = self.query_patient_data(patient_id, question, top_k=3)
            
            if not relevant_chunks:
                return "I don't have enough information to answer that question. Please make sure the patient audio has been transcribed first."
            
            # Step 2: Build context
            context = "\n\n".join(relevant_chunks)
            
            # Step 3: Build prompt for LLM
            prompt = f"""You are a medical assistant analyzing patient information.

Patient Name: {patient_info.get('name', 'N/A')}
Patient Age: {patient_info.get('age', 'N/A')}

Patient Transcription:
{context}

Question: {question}

Provide a clear, concise answer based ONLY on the patient information above."""
            
            # Step 4: Try to generate answer using LLM
            answer = self.call_huggingface_llm(prompt)
            
            if answer:
                return answer
            
            # Step 5: FALLBACK - Rule-based answers
            print("💡 Using intelligent fallback")
            
            question_lower = question.lower()
            context_lower = context.lower()
            
            # Age questions
            if any(word in question_lower for word in ["age", "old", "years"]):
                age = patient_info.get('age', 'N/A')
                if age != 'N/A':
                    return f"The patient is {age} years old."
                else:
                    return "The patient's age is not mentioned in the transcription."
            
            # Name questions
            elif any(word in question_lower for word in ["name", "who is", "patient name"]):
                name = patient_info.get('name', 'N/A')
                if name != 'N/A':
                    return f"The patient's name is {name}."
                else:
                    return "The patient's name is not clearly mentioned in the transcription."
            
            # Pain location questions
            elif any(word in question_lower for word in ["where", "location", "part", "which part"]):
                if "stomach" in context_lower or "abdomen" in context_lower:
                    return f"Based on the patient's description, the pain is in the stomach/abdominal area.\n\nDetails: {context}"
                elif "head" in context_lower:
                    return f"The patient is experiencing headache.\n\nDetails: {context}"
                elif "chest" in context_lower:
                    return f"The patient has chest pain.\n\nDetails: {context}"
                else:
                    return f"Based on the transcription:\n\n{context}"
            
            # Symptoms/suffering questions
            elif any(word in question_lower for word in ["symptom", "suffering", "problem", "complain", "issue"]):
                return f"Patient Symptoms:\n\n{context}"
            
            # Duration questions
            elif any(word in question_lower for word in ["how long", "duration", "when did", "since when"]):
                if "week" in context_lower:
                    return f"Based on the patient's statement, the symptoms have been present for approximately one week.\n\nContext: {context}"
                elif "day" in context_lower or "days" in context_lower:
                    return f"The symptoms appear to be recent (within days).\n\nContext: {context}"
                else:
                    return f"Duration from patient's description:\n\n{context}"
            
            # Type of pain questions
            elif any(word in question_lower for word in ["type", "kind", "feel", "describe"]):
                if "burning" in context_lower or "cramping" in context_lower:
                    return f"The patient describes the pain as burning or cramping.\n\nFull description: {context}"
                else:
                    return f"Patient's description:\n\n{context}"
            
            # Generic fallback
            else:
                return f"Based on the patient's transcription:\n\n{context}"
                
        except Exception as e:
            print(f"❌ Error generating answer: {e}")
            import traceback
            traceback.print_exc()
            return "I apologize, but I encountered an error. Please try rephrasing your question."
    
    def delete_patient_collection(self, patient_id: str):
        """Delete patient collection when session ends"""
        try:
            collection_name = f"patient_{patient_id}"
            self.chroma_client.delete_collection(name=collection_name)
            print(f"✓ Deleted collection for {patient_id}")
        except Exception as e:
            print(f"⚠ Could not delete collection: {e}")


# Global chatbot instance
print("🚀 Initializing RAG Chatbot...")
chatbot = RAGChatbot()
print("✅ RAG Chatbot ready!")

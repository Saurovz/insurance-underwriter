import os
from pathlib import Path
from typing import List, Dict, Optional
import chromadb
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from datetime import datetime

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
                task="conversational",
                huggingfacehub_api_token=self.hf_api_key,
                temperature=0.7,
                max_new_tokens=300
            )
            self.chat_model = ChatHuggingFace(llm=llm)
            print(f"✓ LLM initialized: {self.llm_model}")
        except Exception as e:
            print(f"⚠️ LLM initialization failed: {e}")
            self.chat_model = None
    
    # ========== NEW: INTENT CLASSIFICATION ==========
    def classify_intent(self, question: str) -> str:
        """
        Classify user intent to route between general chat and RAG
        Returns: 'general' or 'patient_specific'
        """
        question_lower = question.lower().strip()
        
        # Keywords for general conversation
        general_keywords = [
            # Greetings
            'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
            'good evening', 'how are you', 'what\'s up', 'sup',
            
            # Date/Time queries
            'what day', 'what date', 'today', 'time', 'day is it',
            'date is it', 'what time', 'current date', 'current time',
            
            # Chatbot identity
            'who are you', 'what are you', 'your name', 'who made you',
            'what can you do', 'help me', 'how do you work',
            
            # Thank you / Goodbye
            'thank you', 'thanks', 'bye', 'goodbye', 'see you', 'later',
            
            # Weather (if you want to handle it)
            'weather', 'temperature', 'forecast'
        ]
        
        # Check if question contains general keywords
        for keyword in general_keywords:
            if keyword in question_lower:
                print(f"🎯 Intent: GENERAL (matched '{keyword}')")
                return 'general'
        
        # Patient-specific keywords (indicates RAG needed)
        patient_keywords = [
            'patient', 'symptom', 'diagnosis', 'medical', 'pain',
            'suffering', 'complain', 'age', 'name', 'transcription',
            'video', 'describe', 'condition', 'illness', 'disease'
        ]
        
        for keyword in patient_keywords:
            if keyword in question_lower:
                print(f"🎯 Intent: PATIENT_SPECIFIC (matched '{keyword}')")
                return 'patient_specific'
        
        # Default: If question is very short (1-3 words), likely general
        if len(question.split()) <= 3:
            print(f"🎯 Intent: GENERAL (short query)")
            return 'general'
        
        # Otherwise, assume patient-specific (safer for medical context)
        print(f"🎯 Intent: PATIENT_SPECIFIC (default)")
        return 'patient_specific'
    
    # ========== NEW: HANDLE GENERAL QUESTIONS ==========
    def handle_general_question(self, question: str) -> str:
        """
        Handle general conversational questions without RAG
        """
        question_lower = question.lower().strip()
        
        # Greetings
        if any(word in question_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! 👋 I'm your medical transcription assistant. I can help you understand patient information from transcribed videos. Feel free to ask me questions about the patient's symptoms, conditions, or any details from the transcription!"
        
        if 'how are you' in question_lower:
            return "I'm functioning well, thank you! 😊 I'm here to help you analyze patient transcriptions. Do you have any questions about the patient data?"
        
        # Date and time
        if any(word in question_lower for word in ['what day', 'what date', 'today', 'date is it']):
            current_date = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {current_date}."
        
        if 'time' in question_lower and any(word in question_lower for word in ['what', 'current']):
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}."
        
        # Chatbot identity
        if any(phrase in question_lower for phrase in ['who are you', 'what are you']):
            return "I'm an AI-powered medical transcription assistant. I analyze patient video transcriptions and answer questions about patient symptoms, conditions, and medical information. Upload a video and ask me anything about the patient!"
        
        if 'what can you do' in question_lower or 'help' in question_lower:
            return """I can help you with:
            
1. **Analyze transcribed patient videos** - Extract key medical information
2. **Answer questions** about patient symptoms, age, conditions
3. **Search through transcriptions** - Find specific details quickly
4. **Provide context** - Give you relevant excerpts from patient conversations

Just upload a video, and ask me questions like:
- "What symptoms is the patient experiencing?"
- "How long has the patient been suffering?"
- "What is the patient's age?"
"""
        
        # Thank you
        if 'thank' in question_lower:
            return "You're welcome! 😊 Let me know if you need anything else!"
        
        # Goodbye
        if any(word in question_lower for word in ['bye', 'goodbye', 'see you']):
            return "Goodbye! Take care. Feel free to return anytime you need help with patient transcriptions! 👋"
        
        # Fallback: Try using LLM for general conversation
        if self.chat_model:
            try:
                print("🔄 Using LLM for general conversation...")
                messages = [HumanMessage(content=f"You are a friendly medical assistant chatbot. Respond to this general question naturally and concisely:\n\n{question}")]
                response = self.chat_model.invoke(messages)
                if response and hasattr(response, 'content'):
                    return response.content.strip()
            except Exception as e:
                print(f"⚠️ LLM failed: {e}")
        
        # Final fallback
        return "I'm here to help with patient transcription analysis. Could you please ask a question about the patient's medical information, or say 'help' to learn what I can do?"
    
    # ========== REST OF YOUR EXISTING METHODS (unchanged) ==========
    
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
            return [text]
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size + 50])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks if chunks else [text]
    
    def add_patient_transcription(self, patient_id: str, transcription: str, patient_info: Dict) -> bool:
        """Add patient transcription to ChromaDB with embeddings"""
        try:
            print(f"📝 Adding transcription for {patient_id} to vector database...")
            
            if not transcription or not transcription.strip():
                print("⚠️ Empty transcription, skipping ChromaDB")
                return False
            
            collection = self.create_patient_collection(patient_id)
            chunks = self.chunk_text(transcription)
            print(f"📄 Split into {len(chunks)} chunks")
            
            print("🔄 Generating embeddings...")
            embeddings = self.embedding_model.encode(chunks).tolist()
            print(f"✓ Generated {len(embeddings)} embeddings")
            
            metadatas = [
                {
                    "patient_id": patient_id,
                    "patient_name": str(patient_info.get("name", "N/A")),
                    "patient_age": str(patient_info.get("age", "N/A")),
                    "chunk_index": str(i)
                }
                for i in range(len(chunks))
            ]
            
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
            
            print(f"🔍 Searching for: {question}")
            query_embedding = self.embedding_model.encode([question]).tolist()
            
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            documents = results['documents'][0] if results['documents'] else []
            
            print(f"✓ Retrieved {len(documents)} relevant chunks")
            return documents
            
        except Exception as e:
            print(f"❌ Error querying ChromaDB: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def call_huggingface_llm(self, prompt: str) -> Optional[str]:
        """Call HuggingFace LLM using conversational task"""
        
        if not self.chat_model:
            print("⚠️ LLM not available")
            return None
        
        try:
            print(f"🔄 Calling conversational LLM...")
            messages = [HumanMessage(content=prompt)]
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
    
    # ========== MODIFIED: MAIN ANSWER GENERATION WITH INTENT ROUTING ==========
    def generate_answer(self, patient_id: str, question: str, patient_info: Dict) -> str:
        """
        Generate answer using hybrid approach:
        - General questions → Direct response (no RAG)
        - Patient-specific → RAG pipeline
        """
        try:
            print(f"🤖 Processing question: {question}")
            
            # ===== STEP 1: CLASSIFY INTENT =====
            intent = self.classify_intent(question)
            
            # ===== STEP 2: ROUTE BASED ON INTENT =====
            if intent == 'general':
                print("💬 Handling as general conversation")
                return self.handle_general_question(question)
            
            # ===== STEP 3: PATIENT-SPECIFIC → USE RAG =====
            print("🔬 Handling as patient-specific query (RAG)")
            
            # Retrieve relevant context from ChromaDB
            relevant_chunks = self.query_patient_data(patient_id, question, top_k=3)
            
            if not relevant_chunks:
                return "I don't have enough information to answer that question. Please make sure the patient audio has been transcribed first."
            
            # Build context
            context = "\n\n".join(relevant_chunks)
            
            # Build prompt for LLM
            prompt = f"""You are a medical assistant analyzing patient information.

Patient Name: {patient_info.get('name', 'N/A')}
Patient Age: {patient_info.get('age', 'N/A')}

Patient Transcription:
{context}

Question: {question}

Provide a clear, concise answer based ONLY on the patient information above."""
            
            # Try LLM generation
            answer = self.call_huggingface_llm(prompt)
            
            if answer:
                return answer
            
            # Fallback - Rule-based answers
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

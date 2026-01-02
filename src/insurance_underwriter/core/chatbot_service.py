from typing import List, Dict
import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from insurance_underwriter.config.config import ModelConfig


class PolicyChatbotService:
    """
    Chatbot service for answering policy-related questions.
    Uses RAG to query ChromaDB and LLM to generate conversational responses.
    """
    
    def __init__(self,
                 db_path: str = "D:\AI_HealthCare\insurance-underwriter\src\streamlit_app\chroma_db",
                 collection_name: str = "policy_rules",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize chatbot service.
        
        Args:
            db_path: Path to ChromaDB
            collection_name: Collection name for policy rules
            embedding_model: HuggingFace embedding model
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize embeddings (same as your existing setup)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get collection
        try:
            self.collection = self.client.get_collection(self.collection_name)
        except Exception as e:
            raise Exception(
                f"Policy knowledge base not found. Please run policy_knowledge_base.py first. Error: {e}"
            )
        
        # Initialize LLM (using your existing config)
        self.llm = ModelConfig.get_model()
    
    def query_policy_knowledge(self, user_query: str, n_results: int = 3) -> List[Dict]:
        """
        Query ChromaDB for relevant policy information.
        
        Args:
            user_query: User's question
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            List of relevant policy chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(user_query)
        
        # Search ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return formatted_results
    
    def generate_chatbot_response(self, user_query: str, conversation_history: List[Dict] = None) -> str:
        """
        Generate conversational response using RAG + LLM.
        
        Args:
            user_query: User's question
            conversation_history: Previous conversation turns (optional)
            
        Returns:
            Chatbot response string
        """
        # Step 1: Retrieve relevant policy context
        policy_chunks = self.query_policy_knowledge(user_query, n_results=3)
        
        if not policy_chunks:
            return "I couldn't find relevant information in the policy document. Please try rephrasing your question or ask about specific policy rules like risk factors, premium calculations, or coverage details."
        
        # Step 2: Format policy context
        context = self._format_policy_context(policy_chunks)
        
        # Step 3: Build conversational prompt
        prompt = self._build_chatbot_prompt(user_query, context, conversation_history)
        
        # Step 4: Get LLM response
        response = self.llm.invoke(prompt)
        
        # Parse response content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        return response_text.strip()
    
    def _format_policy_context(self, results: List[Dict]) -> str:
        """Format retrieved policy chunks into context string."""
        if not results:
            return "No relevant policy rules found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Policy Section {i}]")
            context_parts.append(result['content'])
            context_parts.append("")  # Empty line for separation
        
        return "\n".join(context_parts)
    
    def _build_chatbot_prompt(self, user_query: str, context: str, conversation_history: List[Dict] = None) -> str:
        """
        Build conversational prompt for LLM.
        
        Args:
            user_query: Current user question
            context: Retrieved policy context
            conversation_history: Previous Q&A pairs
        """
        # Build conversation history string
        history_str = ""
        if conversation_history and len(conversation_history) > 0:
            history_str = "\n**Previous Conversation:**\n"
            for turn in conversation_history[-3:]:  # Last 3 turns only
                history_str += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"
        
        prompt = f"""You are a helpful AI assistant for a Health Insurance Underwriting system. Your role is to answer questions about policy rules, risk factors, premium calculations, and coverage details based ONLY on the provided policy document context.

**Policy Document Context:**
{context}

{history_str}

**Current User Question:**
{user_query}

**Instructions:**
1. Answer the user's question based ONLY on the policy context provided above
2. Be conversational and friendly while remaining professional
3. If the user asks about specific risk factors (smoking, BMI, age, etc.), provide clear information from the policy
4. If the user asks about premium calculations, explain the factors involved
5. If the question cannot be answered from the policy context, politely say you don't have that information in the policy document
6. Do NOT provide information about specific applicants or their data
7. Do NOT make up information - stick to what's in the policy context
8. Keep your response concise (2-4 sentences) unless the user asks for detailed explanation

**Response:**"""
        
        return prompt


# Utility function to initialize chatbot service (singleton pattern)
_chatbot_service = None

def get_chatbot_service() -> PolicyChatbotService:
    """Get or create chatbot service instance (singleton)."""
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = PolicyChatbotService()
    return _chatbot_service

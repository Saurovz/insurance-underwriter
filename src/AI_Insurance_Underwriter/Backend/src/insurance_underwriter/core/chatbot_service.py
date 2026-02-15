import os
import sqlite3
from typing import List, Dict, Any

import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda


import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent  # agent, not create_sql_query_chain



from langchain_core.tools import Tool
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from insurance_underwriter.config.config import ModelConfig
# Import the DB_PATH from your database.py to ensure consistency
from insurance_underwriter.core.database import DB_PATH

class PolicyChatbotService:
    """
    Unified Chatbot service for answering policy-related questions AND application data questions.
    Uses RAG for policy documents and Text-to-SQL for database queries.
    """

    def __init__(self, 
                 chroma_db_path: str = None,
                 collection_name: str = "policy_rules",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize chatbot service with both Vector DB and SQL DB connections.
        """
        if chroma_db_path is None:
            from insurance_underwriter.config.config import CHROMA_DB_PATH
            chroma_db_path = CHROMA_DB_PATH
            
        self.chroma_db_path = chroma_db_path
        self.collection_name = collection_name
        
        # 1. Initialize LLM (Shared for all tasks)
        self.llm = ModelConfig.get_model()

        # 2. Initialize ChromaDB (Policy Knowledge)
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        self.chroma_client = chromadb.PersistentClient(
            path=self.chroma_db_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        try:
            self.collection = self.chroma_client.get_collection(self.collection_name)
        except Exception as e:
            print(f"Warning: Policy knowledge base collection not found: {e}")
            self.collection = None

        # 3. Initialize SQL Database (Application Data)
        # Ensure we use the absolute path or correct relative path to the DB
        db_uri = f"sqlite:///{DB_PATH}"
        self.db = SQLDatabase.from_uri(db_uri)

    def classify_intent(self, user_query: str) -> str:
        """
        Classifies the user query into 'POLICY' or 'DATABASE'.
        """
        classification_prompt = PromptTemplate.from_template(
            """You are a smart router for an insurance assistant. 
            Classify the following user question into one of two categories:
            
            1. 'DATABASE': Questions about specific user applications, statistics, numbers, counts, premiums of applied users, status of applications (approved/declined), or aggregate data from the system.
               Examples: "How many users got declined?", "Average premium?", "List all applicants", "Who has high risk?"
            
            2. 'POLICY': Questions about general insurance rules, coverage details, exclusions, definitions, risk factors in general, or how things are calculated theoretically.
               Examples: "What is the BMI limit?", "Is smoking covered?", "How is premium calculated normally?"

            Return ONLY the category name ('DATABASE' or 'POLICY') and nothing else.
            
            Question: {question}
            Category:"""
        )
        
        chain = classification_prompt | self.llm | StrOutputParser()
        intent = chain.invoke({"question": user_query}).strip().upper()
        
        # Fallback if model is chatty
        if "DATABASE" in intent: return "DATABASE"
        return "POLICY"

    def query_policy_knowledge(self, user_query: str, n_results: int = 3) -> List[Dict]:
        """Query ChromaDB for relevant policy information."""
        if not self.collection:
            return []

        query_embedding = self.embeddings.embed_query(user_query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        formatted_results = []
        if results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                })
        return formatted_results

    def _format_policy_context(self, results: List[Dict]) -> str:
        """Format retrieved policy chunks."""
        if not results:
            return "No relevant policy rules found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Policy Section {i}]\n{result['content']}\n")
        return "\n".join(context_parts)

    def _clean_sql(self, text: str) -> str:
        """Normalize LLM output into executable SQL."""
        if not text:
            return ""

        # Remove markdown fences
        text = text.replace("```sql", "").replace("```", "").strip()

        # If model returns: SQLQuery: SELECT ...
        m = re.search(r"SQLQuery:\s*(.*)", text, flags=re.IGNORECASE | re.DOTALL)
        if m:
            text = m.group(1).strip()

        # Optional: keep only first statement
        if ";" in text:
            text = text.split(";")[0].strip()

        # Ensure trailing semicolon
        if text and not text.endswith(";"):
            text += ";"

        return text

    def query_database_data(self, user_query: str) -> str:
        """
        Text-to-SQL without create_sql_query_chain:
        1) Provide dialect + schema (table_info)
        2) Ask LLM to output SQL only
        3) Execute SQL via SQLDatabase.run
        4) Ask LLM to convert result to natural language
        """
        sql_prompt = PromptTemplate.from_template(
            """Given an input question, write a syntactically correct {dialect} SQL query.
Only use the following tables and columns:
{table_info}

Return ONLY the SQL query (no explanations, no markdown).

Question: {question}
SQL:"""
        )  # Uses the same {dialect}/{table_info} prompt variables described in LangChain SQL docs. [page:1]

        # 1) Generate SQL
        try:
            raw_sql = (sql_prompt | self.llm | StrOutputParser()).invoke(
                {
                    "question": user_query,
                    "dialect": self.db.dialect,
                    "table_info": self.db.get_table_info(),
                }
            )
            generated_sql = self._clean_sql(raw_sql)
        except Exception as e:
            return f"I couldn't generate a SQL query for that question. Error: {str(e)}"

        # 2) Execute SQL
        try:
            result = self.db.run(generated_sql)
        except Exception as e:
            return (
                "I generated a SQL query but couldn't run it on the database. "
                f"Error: {str(e)}"
            )

        # 3) Convert result -> answer
        answer_prompt = PromptTemplate.from_template(
            """Answer the user's question using the SQL result.

Question: {question}
SQL Query: {query}
SQL Result: {result}

Answer (concise and professional):"""
        )

        try:
            final_answer = (answer_prompt | self.llm | StrOutputParser()).invoke(
                {"question": user_query, "query": generated_sql, "result": result}
            )
            return final_answer.strip()
        except Exception as e:
            return f"I got the database result but couldn't format the final answer. Error: {str(e)}"

    def generate_chatbot_response(self, user_query: str, conversation_history: List[Dict] = None) -> str:
        """
        Main entry point. Routes query to DB or Policy RAG based on intent.
        """
        # Step 1: Determine Intent
        intent = self.classify_intent(user_query)
        
        if intent == "DATABASE":
            # --- DATABASE ROUTE ---
            try:
                return self.query_database_data(user_query)
            except Exception as e:
                return f"I had trouble accessing the application data. Error: {e}"
        
        else:
            # --- POLICY RAG ROUTE (Existing Logic) ---
            policy_chunks = self.query_policy_knowledge(user_query, n_results=3)
            
            if not policy_chunks:
                return "I couldn't find relevant information in the policy document."

            context = self._format_policy_context(policy_chunks)
            prompt = self._build_chatbot_prompt(user_query, context, conversation_history)
            
            response = self.llm.invoke(prompt)
            
            if hasattr(response, 'content'):
                return response.content.strip()
            return str(response).strip()

    def _build_chatbot_prompt(self, user_query: str, context: str, conversation_history: List[Dict] = None) -> str:
        """Existing prompt builder for policy questions."""
        history_str = ""
        if conversation_history and len(conversation_history) > 0:
            history_str = "\n**Previous Conversation:**\n"
            for turn in conversation_history[-3:]:
                history_str += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"

        prompt = f"""You are a helpful AI assistant for a Health Insurance Underwriting system. 
        
        **Policy Document Context:**
        {context}
        {history_str}
        
        **Current User Question:**
        {user_query}
        
        **Instructions:**
        1. Answer based ONLY on the policy context above.
        2. If asking about specific applicants, say you cannot access that data here (the router should have caught this, but just in case).
        3. Keep it professional and concise.
        
        **Response:**"""
        return prompt

# Singleton access
_chatbot_service = None

def get_chatbot_service() -> PolicyChatbotService:
    global _chatbot_service
    if _chatbot_service is None:
        _chatbot_service = PolicyChatbotService()
    return _chatbot_service

from typing import Dict, List, Tuple
import chromadb
from chromadb.config import Settings
from langchain_huggingface import HuggingFaceEmbeddings
from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.config.config import ModelConfig


class PolicyRAGService:
    """
    RAG Service to query policy rules based on applicant information.
    """
    
    def __init__(self, 
                 db_path: str = "./chroma_db",
                 collection_name: str = "policy_rules",
                 embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize RAG service.
        """
        self.db_path = db_path
        self.collection_name = collection_name
        
        # Initialize embeddings (same as knowledge base)
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
            raise Exception(f"Policy knowledge base not found. Please run policy_knowledge_base.py first. Error: {e}")
        
        # Initialize LLM
        self.llm = ModelConfig.get_model()
    
    def query_policy_rules(self, query: str, n_results: int = 5) -> List[Dict]:
        """
        Query the policy database for relevant rules.
        
        Args:
            query: Search query describing what policy rules to find
            n_results: Number of relevant chunks to retrieve
            
        Returns:
            List of relevant policy chunks with metadata
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        
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
    
    def get_risk_evaluation_rules(self, state: UnderwritingState) -> str:
        """
        Retrieve policy rules relevant to risk evaluation for given applicant.
        
        Args:
            state: Current underwriting state with applicant info
            
        Returns:
            Formatted context string with relevant policy rules
        """
        # Build query based on applicant characteristics
        query_parts = []
        
        if state.get('age'):
            query_parts.append(f"age {state['age']} years risk evaluation scoring")
        
        if state.get('bmi'):
            bmi_category = self._get_bmi_category(state['bmi'])
            query_parts.append(f"BMI {state['bmi']} {bmi_category} loading factor")
        
        if state.get('smoking_status'):
            query_parts.append(f"smoking {state['smoking_status']} risk loading")
        
        if state.get('alcohol_consumption'):
            query_parts.append(f"alcohol consumption {state['alcohol_consumption']} risk")
        
        # Combine queries
        combined_query = " ".join(query_parts)
        
        # Retrieve relevant policy chunks
        results = self.query_policy_rules(combined_query, n_results=5)
        
        # Format context
        context = self._format_policy_context(results)
        
        return context
    
    def get_premium_calculation_rules(self, state: UnderwritingState) -> str:
        """
        Retrieve policy rules relevant to premium calculation.
        
        Args:
            state: Current underwriting state with applicant info
            
        Returns:
            Formatted context string with relevant premium calculation rules
        """
        # Build query for premium calculation
        query = f"""
        premium calculation base rate age {state['age']} 
        medical loading {state.get('risk_category', 'MEDIUM')}
        health status adjustment discount
        """
        
        # Retrieve relevant chunks
        results = self.query_policy_rules(query, n_results=5)
        
        # Format context
        context = self._format_policy_context(results)
        
        return context
    def extract_structured_rules_with_llm(self, context: str, applicant_info: Dict, task: str) -> Dict:
        """
        Use LLM to extract structured rules from policy context.
        """
        if task == 'risk_evaluation':
            prompt = self._build_risk_evaluation_prompt(context, applicant_info)
        elif task == 'premium_calculation':
            prompt = self._build_premium_calculation_prompt(context, applicant_info)
        else:
            raise ValueError(f"Unknown task: {task}")
        
        # ===== DEBUG: Print what's being sent to LLM =====
        print("\n" + "="*60)
        print("DEBUG: PROMPT SENT TO LLM")
        print("="*60)
        print(prompt[:2000])  # Print first 2000 chars
        print("...\n")
        # ================================================
        
        # Get LLM response
        response = self.llm.invoke(prompt)
        
        # Parse response content
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        # ===== DEBUG: Print what LLM returned =====
        print("\n" + "="*60)
        print("DEBUG: LLM RESPONSE")
        print("="*60)
        print(response_text)
        print("="*60 + "\n")
        # =========================================
        
        # Extract structured data from response
        structured_data = self._parse_llm_response(response_text, task)
        
        print(f"DEBUG: Parsed structured_data = {structured_data}\n")
        
        return structured_data


    
    # def extract_structured_rules_with_llm(self, context: str, applicant_info: Dict, task: str) -> Dict:
    #     """
    #     Use LLM to extract structured rules from policy context.
        
    #     Args:
    #         context: Policy rules context from RAG
    #         applicant_info: Applicant details
    #         task: Either 'risk_evaluation' or 'premium_calculation'
            
    #     Returns:
    #         Structured rules as dictionary
    #     """
    #     if task == 'risk_evaluation':
    #         prompt = self._build_risk_evaluation_prompt(context, applicant_info)
    #     elif task == 'premium_calculation':
    #         prompt = self._build_premium_calculation_prompt(context, applicant_info)
    #     else:
    #         raise ValueError(f"Unknown task: {task}")
        
    #     # Get LLM response
    #     response = self.llm.invoke(prompt)
        
    #     # Parse response content
    #     if hasattr(response, 'content'):
    #         response_text = response.content
    #     else:
    #         response_text = str(response)
        
    #     # Extract structured data from response
    #     structured_data = self._parse_llm_response(response_text, task)
        
    #     return structured_data
    
    def _build_risk_evaluation_prompt(self, context: str, applicant_info: Dict) -> str:
        """Build prompt for risk evaluation."""
        prompt = f"""You are an expert health insurance underwriter. Based on the policy rules provided, calculate risk POINTS (not premium rates) for this applicant.

    **Policy Rules Context:**
    {context}

    **Applicant Information:**
    - Age: {applicant_info.get('age', 'N/A')}
    - BMI: {applicant_info.get('bmi', 'N/A')}
    - Smoking Status: {applicant_info.get('smoking_status', 'N/A')}
    - Alcohol Consumption: {applicant_info.get('alcohol_consumption', 'N/A')}

    **Task:**
    Calculate RISK POINTS (0-100 scale) based on these rules:
    - Start with 0 risk points for a healthy baseline
    - Add risk points ONLY for adverse factors:
    * BMI >= 30: Add (bmi_loading_factor - 1.0) * 50 points
    * Smoking (if not non-smoker): Add (smoking_loading_factor - 1.0) * 50 points
    * Alcohol (if heavy consumption): Add appropriate risk points
    * Pre-existing conditions: Add risk points per condition

    **Important:**
    - DO NOT use the base premium rate (₹250, ₹300, etc.) as risk score
    - Base premium rate is for premium calculation, NOT risk scoring
    - A healthy young person should have LOW risk points (0-20)
    - Age alone should NOT add risk points unless elderly (>60 years)

    **Output Format (JSON-like structure):**
    {{
        "calculated_risk_points": <0-100>,
        "bmi_loading_factor": <number>,
        "smoking_loading_factor": <number>,
        "alcohol_loading_factor": <number>,
        "flagged_conditions": [<list of conditions to flag>],
        "risk_explanation": "<brief explanation of risk calculation>"
    }}

    Provide ONLY the structured output, no additional explanation."""
        
        return prompt

    
    def _build_premium_calculation_prompt(self, context: str, applicant_info: Dict) -> str:
        """Build prompt for premium calculation."""
        prompt = f"""You are an expert health insurance underwriter. Based on the policy rules provided, extract the specific premium calculation parameters for this applicant.

    **Policy Rules Context:**
    {context}

    **Applicant Information:**
    - Age: {applicant_info.get('age', 'N/A')}
    - Risk Category: {applicant_info.get('risk_category', 'N/A')}
    - Smoking Status: {applicant_info.get('smoking_status', 'N/A')}
    - BMI: {applicant_info.get('bmi', 'N/A')}

    **Task:**
    Based on the policy rules above, extract the following premium calculation parameters:

    1. **Base Morbidity Rate**: Find the base rate (₹ per ₹1 Lakh SI) for age {applicant_info.get('age')} from the age band table in the policy
    2. **Medical Loading Percentage**: Based on risk category "{applicant_info.get('risk_category')}", determine the medical loading percentage to apply
    3. **Lifestyle Discount**: Based on age, smoking status, and BMI, determine if any lifestyle discount applies
    4. **Recommended Plan**: Suggest an appropriate plan (STANDARD_PLAN, PREMIUM_PLAN, etc.)

    **Important Instructions:**
    - Look for the Age-Band Base Morbidity Rates table in the policy context
    - Match the applicant's age to the correct age band
    - Extract the EXACT numeric values from the policy rules
    - If smoking status is "Yes" or "Smoker", check for smoker loading factors
    - If BMI >= 30, check for high BMI loading factors
    - For lifestyle discounts, check the Health Lifestyle Discount section

    **Output Format (JSON structure - provide ONLY this, no other text):**
    {{
        "base_rate_per_lakh": <EXACT number from age band table>,
        "medical_loading_percentage": <number>,
        "lifestyle_discount_percentage": <number>,
        "recommended_plan": "<plan name>"
    }}

    Extract the values from the policy context and provide ONLY the JSON output."""
    
        return prompt

    
    def _parse_llm_response(self, response_text: str, task: str) -> Dict:
        """
        Parse LLM response into structured dictionary.
        Uses simple heuristics to extract values.
        """
        import re
        import json
        
        # Try to extract JSON-like content
        # Look for content between curly braces
        json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
        
        if json_match:
            try:
                # Try direct JSON parsing
                json_str = json_match.group(0)
                # Clean up the JSON string
                json_str = json_str.replace('\n', ' ').strip()
                parsed = json.loads(json_str)
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Fallback: Manual extraction
        if task == 'risk_evaluation':
            return self._manual_extract_risk_data(response_text)
        elif task == 'premium_calculation':
            return self._manual_extract_premium_data(response_text)
        
        return {}
    
    def _manual_extract_risk_data(self, text: str) -> Dict:
        """Manually extract risk evaluation data from text."""
        import re
        
        result = {
            "age_risk_score": 0,
            "bmi_loading_factor": 1.0,
            "smoking_loading_factor": 1.0,
            "alcohol_risk_note": "",
            "flagged_conditions": []
        }
        
        # Extract age risk score
        age_match = re.search(r'"age_risk_score":\s*(\d+)', text)
        if age_match:
            result["age_risk_score"] = int(age_match.group(1))
        
        # Extract BMI loading
        bmi_match = re.search(r'"bmi_loading_factor":\s*([\d.]+)', text)
        if bmi_match:
            result["bmi_loading_factor"] = float(bmi_match.group(1))
        
        # Extract smoking loading
        smoking_match = re.search(r'"smoking_loading_factor":\s*([\d.]+)', text)
        if smoking_match:
            result["smoking_loading_factor"] = float(smoking_match.group(1))
        
        return result


    def _manual_extract_premium_data(self, text: str) -> Dict:
        """Manually extract premium calculation data from text."""
        import re
        
        result = {
            "base_rate_per_lakh": None,  # ✅ Changed from 0 to None
            "medical_loading_percentage": 0,
            "lifestyle_discount_percentage": 0,
            "recommended_plan": "STANDARD_PLAN"
        }
        
        # Extract base rate - MORE FLEXIBLE PATTERNS
        # Try multiple patterns to catch different formats
        patterns = [
            r'"base_rate_per_lakh":\s*(\d+)',           # Standard JSON
            r'base_rate_per_lakh.*?(\d+)',              # Flexible spacing
            r'₹\s*(\d+)\s*per\s*₹\s*1L',                # From age band table
            r'Base\s+Rate:\s*₹\s*(\d+)',                # Natural language
            r'age\s+band.*?₹\s*(\d+)',                  # Age band context
        ]
        
        for pattern in patterns:
            base_match = re.search(pattern, text, re.IGNORECASE)
            if base_match:
                result["base_rate_per_lakh"] = int(base_match.group(1))
                break
        
        # Extract medical loading
        loading_match = re.search(r'"medical_loading_percentage":\s*([\d.]+)', text)
        if loading_match:
            result["medical_loading_percentage"] = float(loading_match.group(1))
        
        # Extract discount
        discount_match = re.search(r'"lifestyle_discount_percentage":\s*([\d.]+)', text)
        if discount_match:
            result["lifestyle_discount_percentage"] = float(discount_match.group(1))
        
        # Extract plan name
        plan_match = re.search(r'"recommended_plan":\s*"([^"]+)"', text)
        if plan_match:
            result["recommended_plan"] = plan_match.group(1)
        
        return result

    
    def _format_policy_context(self, results: List[Dict]) -> str:
        """Format retrieved policy chunks into context string."""
        if not results:
            return "No relevant policy rules found."
        
        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[Relevant Policy Section {i}]")
            context_parts.append(result['content'])
            context_parts.append("")  # Empty line for separation
        
        return "\n".join(context_parts)
    
    def _get_bmi_category(self, bmi: float) -> str:
        """Get BMI category for query building."""
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        elif bmi < 40:
            return "obese"
        else:
            return "morbidly obese"

import os
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from dotenv import load_dotenv
load_dotenv()


class ModelConfig:
    """Configuration for LLM models."""
    
    # Model settings
    REPO_ID = "openai/gpt-oss-20b"  # or "meta-llama/Llama-3.1-8B-Instruct"
    # REPO_ID = "Qwen/Qwen2.5-72B-Instruct"
    # REPO_ID = "deepseek-ai/DeepSeek-V3"
    TASK = "text-generation"
    TEMPERATURE = 0.7
    MAX_NEW_TOKENS = 2048
    
    @staticmethod
    def get_model():
        """Initialize and return the ChatHuggingFace model."""
        llm = HuggingFaceEndpoint(
            repo_id=ModelConfig.REPO_ID,
            task=ModelConfig.TASK,
            huggingfacehub_api_token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
            temperature=ModelConfig.TEMPERATURE,
            max_new_tokens=ModelConfig.MAX_NEW_TOKENS
        )
        return ChatHuggingFace(llm=llm)


# Directory configurations
DOCUMENTS_DIR = "D:\AI_HealthCare\insurance-underwriter\src\insurance_underwriter\Application_Form"  # Single folder containing all PDFs
OUTPUT_JSON_FILE = "extracted_medical_data.json"

# Risk Thresholds
RISK_THRESHOLDS = {
    'DECLINED': 80,
    'HIGH': 50,
    'MEDIUM': 25,
    'LOW': 0
}

# Premium Configuration (Annual)
BASE_PREMIUMS = {
    (0, 18): 8000,
    (18, 30): 10000,
    (30, 45): 15000,
    (45, 60): 25000,
    (60, 100): 40000
}

MEDICAL_LOADINGS = {
    'LOW': 0,
    'MEDIUM': 25,
    'HIGH': 60,
    'DECLINED': 0
}

# Human Review Triggers
HUMAN_REVIEW_CONFIG = {
    'high_risk_categories': ['HIGH', 'DECLINED'],
    'max_auto_flagged_conditions': 2,
    'medium_risk_score_threshold': 35
}

# Plan Recommendations
PLAN_MAPPING = {
    'DECLINED': 'APPLICATION_DECLINED',
    'HIGH': 'BRONZE_PLAN_WITH_EXCLUSIONS',
    'MEDIUM': 'SILVER_PLAN',
    'LOW': 'GOLD_PLAN'
}


# Defines the UnderwritingState (TypedDict)
from typing import TypedDict, List, Dict, Any

class UnderwritingState(TypedDict):
    """Single unified state containing all underwriting information"""
    
    # ===== INPUT DOCUMENTS =====
    application_form_path: str
    medical_documents_paths: List[str]
    
    # ===== APPLICANT INFORMATION =====
    applicant_name: str
    age: int
    gender: str
    contact_number: str
    email: str
    #address: str
    #occupation: str
    #annual_income: float
    
    # ===== HEALTH INFORMATION =====
    chronic_conditions: List[str]
    bmi: float
    smoking_status: str
    alcohol_consumption: str
    # family_history: List[str]
    # current_medications: List[str]
    # recent_hospitalizations: List[Dict[str, Any]]
    # lab_abnormalities: List[str]
    
    # ===== RISK ASSESSMENT =====
    risk_score: float
    risk_category: str
    flagged_conditions: List[str]
    exclusions: List[str]
    
    # ===== PREMIUM CALCULATION =====
    base_premium: float
    medical_loading_percentage: float
    final_premium: float
    recommended_plan: str
    
    # ===== WORKFLOW CONTROL =====
    requires_human_review: bool
    review_reason: str
    current_step: str
    errors: List[str]
    processing_timestamp: str


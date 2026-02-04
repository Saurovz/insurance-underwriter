# Defines the UnderwritingState (TypedDict)
from typing import TypedDict, List, Dict, Any

class UnderwritingState(TypedDict):
    # ===== APPLICANT INFORMATION =====
    applicant_name: str
    age: int
    gender: str
    contact_number: str
    email: str
    address: str
    occupation: str
    annual_income: float

    # ===== HEALTH INFORMATION =====
    bmi: float
    smoking_status: str
    alcohol_consumption: str

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

    # ===== KYC VERIFICATION FIELDS =====
    kyc_document_path: str  # Path to uploaded Aadhaar/PAN
    date_of_birth: str  # DOB from application form (DD/MM/YYYY)
    kyc_verification_status: str  # "VERIFIED", "MISMATCH", "NOT_PROVIDED", "ERROR"
    kyc_document_type: str  # "AADHAAR", "PAN", "Unknown"
    kyc_discrepancies: List[Dict[str, Any]]  # List of discrepancies found
    kyc_total_discrepancies: int  # Count of discrepancies
    kyc_verification_message: str  # Additional info/error messages

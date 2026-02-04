// src/types/application.ts
export interface ApplicationData {
  id: string;
  filename?: string;
  applicant_name: string;
  age: number;
  gender: string;
  contact_number: string;
  email: string;
  address: string;
  occupation: string;
  annual_income: number;
  date_of_birth?: string;
  bmi: number;
  smoking_status: string;
  alcohol_consumption: string;
  
  // Risk Assessment
  risk_score?: number;
  risk_category?: string;
  flagged_conditions?: string | string[];
  exclusions?: string | string[];
  
  // Premium Calculation
  base_premium?: number;
  medical_loading_percentage?: number;
  final_premium?: number;
  recommended_plan?: string;
  
  // Workflow Control
  requires_human_review?: boolean;
  review_reason?: string;
  
  // KYC Verification
  kyc_verification_status?: string;
  kyc_verification_message?: string;
  kyc_document_type?: string;
  kyc_discrepancies?: any[];
  kyc_total_discrepancies?: number;
  
  // Metadata
  upload_time?: string;
  processing_timestamp?: string;
  current_step?: string;
  errors?: string | string[];
}

export interface ProcessingStatus {
  step: string;
  message: string;
  progress: number;
  timestamp?: string;
}

export interface ChatMessage {
  user: string;
  assistant: string;
}

export interface UploadResponse {
  success: boolean;
  application_id: string;
  message: string;
  files: {
    application_form: string;
    medical_docs: string[];
    kyc_document: string | null;
    total_files: number;
  };
}

export interface ProcessResponse {
  success: boolean;
  application_id: string;
  data: Partial<ApplicationData>;
  message: string;
  errors?: string[];
}

export interface EvaluationResponse {
  success: boolean;
  application_id: string;
  results: {
    risk_score: number;
    risk_category: string;
    base_premium: number;
    medical_loading_percentage: number;
    final_premium: number;
    recommended_plan: string;
    requires_human_review: boolean;
    review_reason: string;
    flagged_conditions: string[];
    exclusions: string[];
    kyc_verification_status: string;
    kyc_verification_message: string;
  };
  message: string;
}

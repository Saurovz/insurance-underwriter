import os
import json
from datetime import datetime
from typing import List
import pdfplumber
from langchain_core.messages import HumanMessage, SystemMessage

from insurance_underwriter.core.Langgraph_state import UnderwritingState
from insurance_underwriter.config.config import ModelConfig, DOCUMENTS_DIR, OUTPUT_JSON_FILE


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from one PDF file."""
    all_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                all_text += text + "\n"
    return all_text


def extract_all_data_from_documents(documents_dir: str, model) -> dict:

    print("="*60)
    print("EXTRACTING DATA FROM ALL DOCUMENTS")
    print("="*60 + "\n")
    
    # Step 1: Extract text from all PDFs in the folder 
    print("Step 1: Extracting text from all PDF files...")
    combined_text = ""
    pdf_files = []
    pdf_count = 0
    
    if os.path.exists(documents_dir):
        for file in os.listdir(documents_dir):
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(documents_dir, file)
                print(f"  Processing: {file}")
                combined_text += f"\n{'='*50}\n"
                combined_text += f"DOCUMENT: {file}\n"
                combined_text += f"{'='*50}\n\n"
                combined_text += extract_text_from_pdf(pdf_path)
                combined_text += "\n"
                pdf_files.append(pdf_path)
                pdf_count += 1
    else:
        print(f"  WARNING: Documents directory not found at {documents_dir}")
    
    print(f"  Total PDFs processed: {pdf_count}\n")

    # Step 2: Create comprehensive prompt for LLM
    print("Step 2: Preparing comprehensive prompt for LLM...")
    
    system_message = SystemMessage(content="""You are an expert health insurance underwriting analyst.
Extract structured information from insurance application forms and medical records with high accuracy.""")
    
    user_prompt = f"""You are an expert health insurance underwriting analyst.

Analyze the provided documents (application form and medical records) and extract ALL the following information.

**APPLICANT INFORMATION:**
- name (full name)
- age (calculate from date of birth if needed)
- gender (Male/Female/Other)
- contact_number
- email
- address (complete address)
- occupation
- annual_income (number in rupees, or 0 if not found)

**HEALTH INFORMATION:**
- chronic_conditions (array of diseases: diabetes, hypertension, heart disease, cancer, kidney disease, COPD, asthma, thyroid disorders, etc.)
- bmi (Body Mass Index as number, or 0 if not calculable)
- smoking_status (exactly one of: "smoker", "non-smoker", "former smoker", "unknown")
- alcohol_consumption (exactly one of: "none", "moderate", "heavy", "unknown")

Return ONLY a valid JSON object with this exact structure (no markdown formatting, no explanations):
{{
    "applicant_name": "",
    "age": 0,
    "gender": "",
    "contact_number": "",
    "email": "",
    "address": "",
    "occupation": "",
    "annual_income": 0,
    "chronic_conditions": [],
    "bmi": 0,
    "smoking_status": "unknown",
    "alcohol_consumption": "unknown",
}}

Be thorough and accurate. Read all pages of all documents carefully.

DOCUMENTS:
----------
{combined_text}
"""
    
    human_message = HumanMessage(content=user_prompt)
    messages = [system_message, human_message]

    # Step 3: Send to LLM for extraction
    print("Step 3: Sending all documents to LLM for extraction...\n")
    response = model.invoke(messages)
    
    # Step 4: Parse JSON response
    print("Step 4: Parsing LLM response...")
    extracted_text = response.content
    
    # Clean up the response if it contains markdown code blocks
    try:
        extracted_data = json.loads(extracted_text)

    except json.JSONDecodeError:
        # Handle cases where the LLM wraps JSON with markdown fences
        if "```json" in extracted_text:
            extracted_text = extracted_text.split("```json")[1].split("```")[0]
        elif "```" in extracted_text:
            extracted_text = extracted_text.split("```")[1]

        extracted_data = json.loads(extracted_text.strip())

    
    print("  Parsing successful!\n")
    
    # Add PDF file paths to extracted data
    extracted_data["_pdf_files"] = pdf_files
    
    return extracted_data


def update_state_from_pdfs(state: UnderwritingState, documents_dir: str) -> UnderwritingState:

    print("="*60)
    print("UNDERWRITING DATA EXTRACTION WORKFLOW")
    print("="*60 + "\n")
    
    # Initialize model from config
    print("Initializing model from config...")
    model = ModelConfig.get_model()
    print("  Model initialized successfully!\n")
    
    errors = []
    extracted_data = {}
    
    try:
        # Extract all data from documents using single function
        extracted_data = extract_all_data_from_documents(
            documents_dir=documents_dir,
            model=model
        )
        
        # Get all PDF file paths
        pdf_files = extracted_data.pop("_pdf_files", [])
        
        # Update state with APPLICANT INFORMATION
        state["applicant_name"] = extracted_data.get("applicant_name", "")
        state["age"] = extracted_data.get("age", 0)
        state["gender"] = extracted_data.get("gender", "")
        state["contact_number"] = extracted_data.get("contact_number", "")
        state["email"] = extracted_data.get("email", "")
        state["address"] = extracted_data.get("address", "")
        state["occupation"] = extracted_data.get("occupation", "")
        state["annual_income"] = extracted_data.get("annual_income", 0.0)
        
        # Update state with HEALTH INFORMATION
        state["bmi"] = extracted_data.get("bmi", 0.0)
        state["smoking_status"] = extracted_data.get("smoking_status", "unknown")
        state["alcohol_consumption"] = extracted_data.get("alcohol_consumption", "unknown")
        
        print("="*60)
        print("STATE UPDATED SUCCESSFULLY")
        print("="*60 + "\n")
        
    except Exception as e:
        error_msg = f"Error extracting data from documents: {str(e)}"
        print(f"\n❌ {error_msg}\n")
        errors.append(error_msg)
    
    # Update workflow control fields
    state["errors"] = errors
    state["processing_timestamp"] = datetime.now().isoformat()
    state["current_step"] = "data_extraction_complete" if not errors else "data_extraction_failed"
    
    # Save extracted data to JSON file
    output_data = {
        "extracted_data": extracted_data,
        "timestamp": state["processing_timestamp"],
        "status": "success" if not errors else "failed",
        "errors": errors
    }
    
    with open(OUTPUT_JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=4, ensure_ascii=False)
    
    print("="*60)
    print(f"✓ Extracted data saved to: {OUTPUT_JSON_FILE}")
    print("="*60 + "\n")
    
    return state


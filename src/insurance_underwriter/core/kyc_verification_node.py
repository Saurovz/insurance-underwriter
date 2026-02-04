import json
from datetime import datetime
from pathlib import Path
from typing import Dict

try:
    import fitz  # PyMuPDF
except ImportError as e:
    print(f"Missing required package: {e}")
    print("Install with: pip install PyMuPDF")

from insurance_underwriter.config.config import ModelConfig
from insurance_underwriter.core.Langgraph_state import UnderwritingState


class KYCVerificationEngine:
    """KYC Document Verification using HuggingFace LLM (Text-based PDFs only)."""
    
    def __init__(self):
        """Initialize with HuggingFace model from config."""
        try:
            self.llm = ModelConfig.get_model()
            print("✅ KYC Verification Engine initialized")
        except Exception as e:
            raise ValueError(f"Failed to initialize HuggingFace model: {e}")
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract embedded text from PDF using PyMuPDF.
        Only works with digital/text-based PDFs, not scanned images.
        """
        try:
            text = ""
            with fitz.open(str(pdf_path)) as doc:
                for page in doc:
                    text += page.get_text()
            
            print(f"📄 Extracted {len(text.strip())} characters from PDF")
            return text.strip()
            
        except Exception as e:
            print(f"❌ Error extracting text: {str(e)}")
            return ""
    
    def create_extraction_prompt(self, document_text: str) -> str:
        """Create prompt for KYC data extraction."""
        today = datetime.now().strftime("%d/%m/%Y")
        
        return f"""You are an expert at reading Indian KYC documents (AADHAAR and PAN cards).

Below is the text extracted from a KYC document. Extract the following information:

1. Full Name (exactly as written)
2. Date of Birth (in DD/MM/YYYY format)
3. Age (calculate from DOB, today is {today})
4. Document Type (AADHAAR or PAN)

**Document Text:**
{document_text}

**IMPORTANT INSTRUCTIONS:**
- Look for patterns like "DOB:", "Date of Birth:", "Birth Date:", or dates in DD/MM/YYYY format
- For AADHAAR: Name is usually at the top in larger text
- For PAN: Name is in the format "Name: XXXX"
- Extract EXACTLY what you see, don't modify spelling
- If you cannot find a field, return "Not Found" for that field

Return ONLY a valid JSON object with this exact format:
{{
    "name": "extracted name or Not Found",
    "date_of_birth": "DD/MM/YYYY or Not Found",
    "age": "number or Not Found",
    "document_type": "AADHAAR or PAN or Unknown"
}}

Do not include any explanation, only return the JSON."""
    
    def extract_kyc_info(self, file_path: str) -> Dict[str, str]:
        """Extract KYC information from text-based PDF using LLM."""
        try:
            path = Path(file_path)
            if not path.exists():
                return {
                    "name": "Not Found",
                    "date_of_birth": "Not Found",
                    "age": "Not Found",
                    "document_type": "Unknown",
                    "error": f"File not found: {file_path}"
                }
            
            # Only support PDFs
            if path.suffix.lower() != '.pdf':
                return {
                    "name": "Not Found",
                    "date_of_birth": "Not Found",
                    "age": "Not Found",
                    "document_type": "Unknown",
                    "error": "Only PDF files supported"
                }
            
            # Extract text using PyMuPDF
            document_text = self.extract_text_from_pdf(path)
            
            # Debug: Show extracted text
            print("=" * 80)
            print("📄 DEBUG: EXTRACTED TEXT FROM PDF")
            print("=" * 80)
            if document_text:
                print(document_text[:500])  # First 500 characters
                print("..." if len(document_text) > 500 else "")
            else:
                print("⚠️  No text extracted!")
            print("=" * 80)
            print(f"Total text length: {len(document_text)} characters")
            print("=" * 80)
            
            # Check if text extraction succeeded
            if len(document_text) < 50:
                return {
                    "name": "Not Found",
                    "date_of_birth": "Not Found",
                    "age": "Not Found",
                    "document_type": "Unknown",
                    "error": "PDF appears to be scanned/image-based. Please upload a digital Aadhaar/PAN PDF with embedded text."
                }
            
            # Create prompt and invoke LLM
            prompt = self.create_extraction_prompt(document_text)
            response = self.llm.invoke(prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            
            # Parse JSON response
            result = self.parse_response(content)
            result.update({
                "file_path": str(path),
                "processed_at": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            return {
                "name": "Not Found",
                "date_of_birth": "Not Found",
                "age": "Not Found",
                "document_type": "Unknown",
                "error": f"Processing failed: {str(e)}"
            }
    
    def parse_response(self, content: str) -> Dict[str, str]:
        """Parse LLM response to JSON."""
        try:
            # Remove markdown code blocks if present
            if "```" in content:
                lines = content.strip().split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.startswith('```'):
                        in_json = not in_json
                        continue
                    if in_json:
                        json_lines.append(line)
                content = '\n'.join(json_lines)
            
            # Find JSON object
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            
            return json.loads(content)
            
        except json.JSONDecodeError:
            return {
                "name": "Not Found",
                "date_of_birth": "Not Found",
                "age": "Not Found",
                "document_type": "Unknown",
                "error": "Failed to parse LLM response"
            }
    
    def compare_with_application(self, kyc_data: Dict[str, str], app_name: str, app_age: int, app_dob: str) -> Dict:
        """Compare KYC data with application form data."""
        discrepancies = []
        verification_status = "VERIFIED"
        
        # Compare Name - STRICT EXACT MATCH
        kyc_name = kyc_data.get("name", "").strip().lower()
        app_name_lower = app_name.strip().lower()
        
        # Debug prints
        print("=" * 80)
        print("🔍 DEBUG: NAME COMPARISON")
        print("=" * 80)
        print(f"KYC Name (extracted): '{kyc_name}'")
        print(f"App Name (from form): '{app_name_lower}'")
        print(f"Are they equal? {kyc_name == app_name_lower}")
        print("=" * 80)
        
        if kyc_name != "not found" and app_name:
            if kyc_name != app_name_lower:
                # Names are different
                print(f"⚠️  Names are DIFFERENT!")
                discrepancies.append({
                    "field": "name",
                    "kyc_value": kyc_data.get("name", ""),
                    "application_value": app_name,
                    "severity": "HIGH"
                })
                verification_status = "MISMATCH"
                print(f"❌ MISMATCH DETECTED - Adding to discrepancies")
        else:
            print(f"⚠️  SKIPPING NAME CHECK - kyc_name is 'not found' or app_name is empty")
        
        # Compare Age (with 1-year tolerance)
        kyc_age_str = str(kyc_data.get("age", "Not Found"))
        if kyc_age_str != "Not Found" and app_age:
            try:
                kyc_age = int(kyc_age_str)
                if abs(kyc_age - app_age) > 1:  # More than 1 year difference
                    discrepancies.append({
                        "field": "age",
                        "kyc_value": kyc_age,
                        "application_value": app_age,
                        "severity": "MEDIUM"
                    })
                    if verification_status == "VERIFIED":
                        verification_status = "MISMATCH"
            except ValueError:
                pass
        
        # Compare Date of Birth - STRICT EXACT MATCH
        kyc_dob = kyc_data.get("date_of_birth", "Not Found")
        if kyc_dob != "Not Found" and app_dob and app_dob != "Not Found":
            if kyc_dob != app_dob:
                discrepancies.append({
                    "field": "date_of_birth",
                    "kyc_value": kyc_dob,
                    "application_value": app_dob,
                    "severity": "HIGH"
                })
                verification_status = "MISMATCH"
        
        return {
            "verification_status": verification_status,
            "kyc_document_type": kyc_data.get("document_type", "Unknown"),
            "discrepancies": discrepancies,
            "total_discrepancies": len(discrepancies)
        }


def kyc_verification_node(state: UnderwritingState) -> UnderwritingState:
    """
    LangGraph node for KYC verification.
    Runs after document extraction to verify identity documents.
    Supports digital/text-based PDFs only.
    """
    print("🔍 Running KYC Verification Node...")
    
    # Check if KYC document was uploaded
    kyc_path = state.get("kyc_document_path", "")
    if not kyc_path or kyc_path == "":
        print("⚠️  No KYC document provided - skipping verification")
        state["kyc_verification_status"] = "NOT_PROVIDED"
        state["kyc_document_type"] = None
        state["kyc_discrepancies"] = []
        state["kyc_total_discrepancies"] = 0
        state["kyc_verification_message"] = "No KYC document uploaded"
        state["current_step"] = "kyc_verification_skipped"
        return state
    
    try:
        # Initialize verification engine
        verifier = KYCVerificationEngine()
        
        # Extract KYC data
        print(f"📄 Extracting data from: {kyc_path}")
        kyc_data = verifier.extract_kyc_info(kyc_path)
        
        # Debug output
        print("=" * 80)
        print("🔍 DEBUG: KYC EXTRACTION RESULT")
        print("=" * 80)
        print(f"KYC Data: {kyc_data}")
        print(f"  - Name: {kyc_data.get('name', 'N/A')}")
        print(f"  - DOB: {kyc_data.get('date_of_birth', 'N/A')}")
        print(f"  - Age: {kyc_data.get('age', 'N/A')}")
        print(f"  - Document Type: {kyc_data.get('document_type', 'N/A')}")
        print(f"  - Error: {kyc_data.get('error', 'None')}")
        print("=" * 80)
        
        if "error" in kyc_data:
            print(f"❌ KYC extraction error: {kyc_data['error']}")
            state["kyc_verification_status"] = "ERROR"
            state["kyc_verification_message"] = kyc_data["error"]
            state["errors"].append(f"KYC Verification Error: {kyc_data['error']}")
        else:
            # Check if extraction succeeded
            kyc_name = kyc_data.get("name", "Not Found")
            
            if kyc_name == "Not Found":
                print("❌ CRITICAL: Failed to extract name from KYC document")
                state["kyc_verification_status"] = "ERROR"
                state["kyc_verification_message"] = "Could not read KYC document. Please upload a digital (text-based) Aadhaar/PAN PDF, not a scanned image."
                state["kyc_document_type"] = "Unreadable"
                state["kyc_discrepancies"] = []
                state["kyc_total_discrepancies"] = 0
                state["errors"].append("KYC Error: Document unreadable - please upload digital PDF")
                state["requires_human_review"] = True
                state["review_reason"] = "KYC document could not be processed - manual verification required"
            else:
                # Compare with application data
                print("🔄 Comparing KYC data with application form...")
                comparison = verifier.compare_with_application(
                    kyc_data=kyc_data,
                    app_name=state.get("applicant_name", ""),
                    app_age=state.get("age", 0),
                    app_dob=state.get("date_of_birth", "")
                )
                
                # Update state
                state["kyc_verification_status"] = comparison["verification_status"]
                state["kyc_document_type"] = comparison["kyc_document_type"]
                state["kyc_discrepancies"] = comparison["discrepancies"]
                state["kyc_total_discrepancies"] = comparison["total_discrepancies"]
                
                # Flag for human review if critical discrepancies found
                high_severity_count = sum(1 for d in comparison["discrepancies"] if d.get("severity") == "HIGH")
                if high_severity_count > 0:
                    state["requires_human_review"] = True
                    state["review_reason"] = f"KYC verification failed: {high_severity_count} critical discrepancy(s) found"
                    state["flagged_conditions"].append("KYC_VERIFICATION_FAILED")
                    print(f"❌ KYC MISMATCH: {high_severity_count} critical discrepancies")
                else:
                    print("✅ KYC verification passed")
                
                state["kyc_verification_message"] = f"Verification complete: {comparison['verification_status']}"
        
        state["current_step"] = "kyc_verification_complete"
        
    except Exception as e:
        print(f"❌ KYC Verification Node Error: {str(e)}")
        state["kyc_verification_status"] = "ERROR"
        state["kyc_verification_message"] = f"Verification failed: {str(e)}"
        state["errors"].append(f"KYC Node Error: {str(e)}")
        state["current_step"] = "kyc_verification_error"
    
    return state

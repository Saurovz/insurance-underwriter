# streamlit_app/pages/1_📝_Application.py

import streamlit as st
import os
import uuid
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path to import your modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from insurance_underwriter.core.document_extract_node import update_state_from_pdfs
from insurance_underwriter.config.initial_state import create_initial_state
from insurance_underwriter.core.risk_evaluation_node import RiskEvaluationEngine
from insurance_underwriter.core.premium_calculation_node import PremiumCalculator
from insurance_underwriter.core.routers import route_decision, human_review_node, final_output_node

# Import database functions
sys.path.insert(0, str(Path(__file__).parent.parent))
from streamlit_app.database import (
    init_db, 
    save_extracted_data, 
    get_application_by_id, 
    get_state_from_db,
    update_premium_data
)


st.set_page_config(
    page_title="Application",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Data Application Page")
st.write("Use this page to input or process your data.")


def application_upload():
    """Handle file upload with separate sections for application form and medical documents"""
    
    st.subheader("Application Upload")
    
    # Initialize session state for file tracking
    if "application_form_uploaded" not in st.session_state:
        st.session_state.application_form_uploaded = False
    if "medical_docs_uploaded" not in st.session_state:
        st.session_state.medical_docs_uploaded = False
    if "application_form_file" not in st.session_state:
        st.session_state.application_form_file = None
    if "medical_docs_files" not in st.session_state:
        st.session_state.medical_docs_files = []
    
    # Generate unique ID once per session
    if "unique_id" not in st.session_state:
        st.session_state.unique_id = str(uuid.uuid4())
    
    # Section 1: Application Form Upload (Mandatory)
    st.markdown("### 1. Application Form Upload <span style='color:red;'>*</span>", unsafe_allow_html=True)
    st.caption("Upload the insurance application form (Required)")
    
    application_form = st.file_uploader(
        "Application Form",
        type=["pdf"],
        key="app_form_uploader",
        help="Upload the completed application form (PDF only)",
        label_visibility="collapsed"
    )
    
    if application_form:
        file_size_mb = len(application_form.getvalue()) / (1024 * 1024)
        st.success(f"✓ {application_form.name} - {file_size_mb:.2f} MB")
        st.session_state.application_form_uploaded = True
        st.session_state.application_form_file = application_form
    else:
        st.session_state.application_form_uploaded = False
        st.session_state.application_form_file = None
    
    st.divider()
    
    # Section 2: Medical Documents Upload (Mandatory, Multiple files)
    st.markdown("### 2. Medical Documents Upload <span style='color:red;'>*</span>", unsafe_allow_html=True)
    st.caption("Upload medical reports, test results, prescriptions, etc. (Required - at least 1 file)")
    
    medical_docs = st.file_uploader(
        "Medical Documents",
        type=["pdf"],
        accept_multiple_files=True,
        key="medical_docs_uploader",
        help="Upload one or more medical documents (PDF only)",
        label_visibility="collapsed"
    )
    
    if medical_docs and len(medical_docs) > 0:
        st.success(f"✓ {len(medical_docs)} medical document(s) uploaded")
        
        # Display uploaded medical documents
        with st.expander("📄 View Uploaded Medical Documents", expanded=True):
            for idx, doc in enumerate(medical_docs, 1):
                file_size_mb = len(doc.getvalue()) / (1024 * 1024)
                st.write(f"{idx}. {doc.name} - {file_size_mb:.2f} MB")
        
        st.session_state.medical_docs_uploaded = True
        st.session_state.medical_docs_files = medical_docs
    else:
        st.session_state.medical_docs_uploaded = False
        st.session_state.medical_docs_files = []
    
    st.divider()
    
    # Check if both required uploads are complete
    both_uploaded = (st.session_state.application_form_uploaded and 
                     st.session_state.medical_docs_uploaded)
    
    # Display file path info if files are uploaded
    if both_uploaded:
        project_root = Path(__file__).parent.parent.parent
        save_dir = project_root / "Document" / st.session_state.unique_id
        
        total_files = 1 + len(st.session_state.medical_docs_files)
        st.info(f"📁 {total_files} file(s) ready to be processed. Files will be saved to `{save_dir}`")
    else:
        # Show warning about missing files
        missing = []
        if not st.session_state.application_form_uploaded:
            missing.append("Application Form")
        if not st.session_state.medical_docs_uploaded:
            missing.append("Medical Documents (at least 1 required)")
        
        st.warning(f"⚠️ Please upload the following required documents: {', '.join(missing)}")
    
    # Submit button - only enabled if both uploads are complete
    submit_button = st.button(
        "Submit", 
        type="primary", 
        disabled=not both_uploaded,
        use_container_width=False
    )
    
    if submit_button:
        if both_uploaded:
            # Reset processing flags
            st.session_state.processing_complete = False
            st.session_state.premium_calculated = False
            
            # Save all files and process
            process_multiple_documents(
                application_id=st.session_state.unique_id,
                application_form=st.session_state.application_form_file,
                medical_docs=st.session_state.medical_docs_files
            )
        else:
            st.error("Please upload both Application Form and Medical Documents before submitting.")
    
    # Display extracted data if processing is complete
    if st.session_state.get("processing_complete", False):
        st.divider()
        display_extracted_data(st.session_state.unique_id)
        
        # Show Calculate Premium button only after data extraction is complete
        st.divider()
        show_premium_calculation_button(st.session_state.unique_id)
    
    # Display premium results if calculation is complete
    if st.session_state.get("premium_calculated", False):
        st.divider()
        display_premium_results(st.session_state.unique_id)


def process_multiple_documents(application_id: str, application_form, medical_docs: list):
    """Process application form and multiple medical documents"""
    
    try:
        with st.status("Processing documents...", expanded=True) as status:
            
            # Step 1: Save all files to disk
            st.write("💾 Saving files to disk...")
            
            project_root = Path(__file__).parent.parent.parent
            save_dir = project_root / "Document" / application_id
            save_dir.mkdir(parents=True, exist_ok=True)
            
            # Save application form
            app_form_path = save_dir / application_form.name
            with open(app_form_path, "wb") as f:
                f.write(application_form.getvalue())
            st.write(f"  ✓ Saved: {application_form.name}")
            
            # Save medical documents
            for doc in medical_docs:
                doc_path = save_dir / doc.name
                with open(doc_path, "wb") as f:
                    f.write(doc.getvalue())
                st.write(f"  ✓ Saved: {doc.name}")
            
            total_files = 1 + len(medical_docs)
            st.write(f"✓ All {total_files} files saved successfully")
            
            # Step 2: Create initial state
            st.write("📋 Creating initial state...")
            state = create_initial_state()
            
            # Step 3: Extract data from all PDFs
            st.write(f"🔍 Extracting data from {total_files} PDF file(s) using LLM...")
            updated_state = update_state_from_pdfs(state, str(save_dir))
            
            # Step 4: Check for errors
            if updated_state.get("errors"):
                st.write("⚠️ Errors detected during extraction")
                for error in updated_state["errors"]:
                    st.write(f"  - {error}")
            else:
                st.write("✓ Data extracted successfully from all documents")
            
            # Step 5: Save to database
            st.write("💾 Saving extracted data to database...")
            
            # Create comma-separated filename list for database
            all_filenames = [application_form.name] + [doc.name for doc in medical_docs]
            combined_filename = ", ".join(all_filenames)
            
            success = save_extracted_data(application_id, combined_filename, updated_state)
            
            if success:
                st.write("✓ Data saved to database")
                status.update(label="✅ Processing complete!", state="complete", expanded=False)
                st.session_state.processing_complete = True
                st.rerun()
            else:
                status.update(label="❌ Failed to save to database", state="error")
                st.error("Failed to save data to database")
                
    except Exception as e:
        st.error(f"❌ Error processing documents: {str(e)}")
        st.exception(e)


def show_premium_calculation_button(application_id: str):
    """Display Calculate Premium button after data extraction"""
    
    st.subheader("💰 Premium Calculation")
    st.write("Click the button below to evaluate risk and calculate premium")
    
    if st.button("Calculate Premium", type="primary", use_container_width=False):
        st.session_state.premium_calculated = False
        execute_underwriting_workflow(application_id)


def execute_underwriting_workflow(application_id: str):
    """Execute the complete underwriting workflow: risk evaluation → premium calculation → routing"""
    
    try:
        with st.status("Executing underwriting workflow...", expanded=True) as status:
            
            # Step 1: Retrieve state from database
            st.write("📂 Retrieving application data from database...")
            state = get_state_from_db(application_id)
            
            if not state:
                st.error("Failed to retrieve application data")
                status.update(label="❌ Workflow failed", state="error")
                return
            
            st.write("✓ Application data retrieved")
            
            # Step 2: Risk Evaluation
            st.write("⚖️ Evaluating risk...")
            risk_evaluator = RiskEvaluationEngine()
            state = risk_evaluator.evaluate_risk(state)
            st.write(f"✓ Risk Score: {state['risk_score']:.0f}/100 ({state['risk_category']})")
            
            # Step 3: Premium Calculation
            st.write("💵 Calculating premium...")
            premium_calculator = PremiumCalculator()
            state = premium_calculator.calculate_premium(state)
            st.write(f"✓ Final Premium: ₹{state['final_premium']:,.0f}")
            
            # Step 4: Router Decision
            st.write("🔀 Determining approval route...")
            decision = route_decision(state)
            
            if decision == "human_review":
                state = human_review_node(state)
                st.write(f"👤 Routed to Human Review: {state['review_reason']}")
            else:
                state = final_output_node(state)
                st.write("✅ Auto-approved")
            
            # Step 5: Update database with premium data
            st.write("💾 Saving premium calculation results...")
            success = update_premium_data(application_id, state)
            
            if success:
                st.write("✓ Premium data saved to database")
                status.update(label="✅ Workflow complete!", state="complete", expanded=False)
                st.session_state.premium_calculated = True
                st.rerun()
            else:
                status.update(label="⚠️ Workflow completed but failed to save", state="error")
                st.warning("Premium calculated but failed to save to database")
                
    except Exception as e:
        st.error(f"❌ Error executing workflow: {str(e)}")
        st.exception(e)


def display_extracted_data(application_id: str):
    """Display extracted data in a table format"""
    
    st.subheader("📊 Extracted Application Data")
    
    # Retrieve data from database
    data = get_application_by_id(application_id)
    
    if not data:
        st.warning("No data found for this application")
        return
    
    # Create two columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 👤 Applicant Information")
        applicant_df = pd.DataFrame({
            "Field": [
                "Name",
                "Age",
                "Gender",
                "Contact Number",
                "Email",
                "Address",
                "Occupation",
                "Annual Income"
            ],
            "Value": [
                data["applicant_name"] or "Not extracted",
                data["age"] if data["age"] > 0 else "Not extracted",
                data["gender"] or "Not extracted",
                data["contact_number"] or "Not extracted",
                data["email"] or "Not extracted",
                data["address"] or "Not extracted",
                data["occupation"] or "Not extracted",
                f"₹{data['annual_income']:,.0f}" if data['annual_income'] > 0 else "Not extracted"
            ]
        })
        st.dataframe(applicant_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### ⚕️ Health Information")
        health_df = pd.DataFrame({
            "Field": [
                "BMI",
                "Smoking Status",
                "Alcohol Consumption"
            ],
            "Value": [
                f"{data['bmi']:.1f}" if data['bmi'] > 0 else "Not extracted",
                data["smoking_status"] or "Not extracted",
                data["alcohol_consumption"] or "Not extracted"
            ]
        })
        st.dataframe(health_df, use_container_width=True, hide_index=True)
    
    # Show metadata in expandable section
    with st.expander("📋 Processing Metadata", expanded=False):
        metadata_df = pd.DataFrame({
            "Field": ["Application ID", "Filename", "Upload Time", "Processing Time", "Current Step"],
            "Value": [
                data["id"],
                data["filename"],
                data["upload_time"],
                data["processing_timestamp"],
                data["current_step"]
            ]
        })
        st.dataframe(metadata_df, use_container_width=True, hide_index=True)
    
    # Show errors if any
    if data.get("errors"):
        st.warning("⚠️ Processing Errors/Warnings:")
        st.text(data["errors"])


def display_premium_results(application_id: str):
    """Display premium calculation results"""
    
    st.subheader("💵 Premium Calculation Results")
    
    # Retrieve data from database
    data = get_application_by_id(application_id)
    
    if not data:
        st.warning("No premium data found")
        return
    
    # Create columns for risk and premium info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚖️ Risk Assessment")
        risk_df = pd.DataFrame({
            "Field": [
                "Risk Score",
                "Risk Category",
                "Flagged Conditions"
            ],
            "Value": [
                f"{data['risk_score']:.0f}/100" if data.get('risk_score') else "Not calculated",
                data.get('risk_category', "Not calculated"),
                data.get('flagged_conditions', "None") or "None"
            ]
        })
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 💰 Premium Details")
        premium_df = pd.DataFrame({
            "Field": [
                "Base Premium",
                "Medical Loading",
                "Final Premium",
                "Recommended Plan"
            ],
            "Value": [
                f"₹{data['base_premium']:,.0f}" if data.get('base_premium') else "Not calculated",
                f"{data['medical_loading_percentage']:.0f}%" if data.get('medical_loading_percentage') is not None else "Not calculated",
                f"₹{data['final_premium']:,.0f}" if data.get('final_premium') else "Not calculated",
                data.get('recommended_plan', "Not assigned")
            ]
        })
        st.dataframe(premium_df, use_container_width=True, hide_index=True)
    
    # Show approval status
    st.markdown("#### ✅ Approval Status")
    
    if data.get('requires_human_review'):
        st.warning(f"👤 **Requires Human Review**")
        st.write(f"**Reason:** {data.get('review_reason', 'Not specified')}")
    else:
        st.success(f"✅ **Auto-Approved**")
        st.write(f"**Status:** {data.get('current_step', 'Completed')}")
    
    # Show exclusions if any
    if data.get('exclusions'):
        st.info(f"📋 **Policy Exclusions:** {data['exclusions']}")


# Initialize database on app load
init_db()

# Main application
application_upload()

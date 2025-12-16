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
# NEW: Import the complete workflow graph instead of individual nodes
from insurance_underwriter.core.graph import build_underwriting_workflow

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

def hide_menuItem():
    st.markdown(
        """
        <style>
        /* Target the menu item and make it invisible */
        span[label="Configure"] {
            visibility: hidden; /* hide background */
            display: none; /* hide the entire element */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
#Hide the "Configure" menu item
hide_menuItem()

# Page Header
st.markdown("""
<div style='background: #e3f2fd; padding: 8px; border-radius: 10px; margin-top: 4px;'>
    <h3 style='color: #174ea6; font-weight: 500;'>📝 1Customer Underwriting Management</h3>
</div>
""", unsafe_allow_html=True)
st.write("Processes **Application Form** and **Lab Reports** for underwriter decision-making and offering best premium.")


def application_upload():
    """Handle file upload with separate sections for application form and medical documents"""
    
    # ✅ IMPROVED: Check if we need to reset for new application FIRST
    if st.session_state.get("reset_for_new_application", False):
        # Clear everything
        for key in ['unique_id', 'processing_complete', 'premium_calculated',
                    'application_form_uploaded', 'medical_docs_uploaded',
                    'application_form_file', 'medical_docs_files']:
            if key in st.session_state:
                del st.session_state[key]
        st.session_state.reset_for_new_application = False
    
    # Initialize session state for file tracking
    if "application_form_uploaded" not in st.session_state:
        st.session_state.application_form_uploaded = False
    if "medical_docs_uploaded" not in st.session_state:
        st.session_state.medical_docs_uploaded = False
    if "application_form_file" not in st.session_state:
        st.session_state.application_form_file = None
    if "medical_docs_files" not in st.session_state:
        st.session_state.medical_docs_files = []
    
    # ✅ FIXED: Only generate unique_id once when it doesn't exist
    if "unique_id" not in st.session_state:
        st.session_state.unique_id = str(uuid.uuid4())
        st.session_state.processing_complete = False
        st.session_state.premium_calculated = False
        print(f"\n🆕 NEW APPLICATION ID: {st.session_state.unique_id}")
    
    # # ✅ ADD: Display current application ID for debugging
    # with st.expander("🔍 Debug Info", expanded=False):
    #     st.code(f"Current Application ID: {st.session_state.unique_id}")
    #     st.code(f"Processing Complete: {st.session_state.get('processing_complete', False)}")
    #     st.code(f"Premium Calculated: {st.session_state.get('premium_calculated', False)}")

    # Section 1: Application Form Upload (Mandatory)
    st.markdown("##### 1. Application Upload *", unsafe_allow_html=True)
    #st.caption("Upload the insurance application form (Required)")
    
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
    
    #st.divider()
    
    # Section 2: Medical Documents Upload (Mandatory, Multiple files)
    st.markdown("##### 2. Lab Reports Upload *", unsafe_allow_html=True)
    st.caption("Upload one or more medical documents ")
    
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
    
    #st.divider()
    
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
        "Process Documents",
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
    st.subheader("💰 Review and Underwriting")
    st.write("Access risk and decision making")
    
    if st.button("Evaluate", type="primary", use_container_width=False):
        st.session_state.premium_calculated = False
        execute_underwriting_workflow(application_id)


def execute_underwriting_workflow(application_id: str):
    """Execute the complete underwriting workflow using LangGraph with RAG"""
    try:
        with st.status("Executing underwriting workflow...", expanded=True) as status:
            # Step 1: Retrieve state from database
            st.write("📂 Retrieving application data from database...")
            state = get_state_from_db(application_id)
            
            if not state:
                st.error("Failed to retrieve application data")
                status.update(label="❌ Workflow failed", state="error")
                return
            
            # ✅ Debug output
            st.write(f"✓ Retrieved data for: {state['applicant_name']}")
            st.write(f"  Application ID: {application_id}")
            st.write(f"  Age: {state['age']}, BMI: {state['bmi']}")
            st.write(f"  Smoking: {state['smoking_status']}, Alcohol: {state['alcohol_consumption']}")
            
            # Step 2: Build workflow WITHOUT document parsing
            st.write("🔧 Building underwriting workflow graph...")
            # ✅ KEY CHANGE: skip_document_parsing=True
            workflow = build_underwriting_workflow(skip_document_parsing=True)
            st.write("✓ Workflow graph built (starting from risk evaluation)")
            
            # Step 3: Execute workflow starting from risk evaluation
            st.write("🚀 Executing workflow with RAG-powered analysis...")
            st.write("  → Running risk evaluation with RAG...")
            st.write("  → Running premium calculation with RAG...")
            st.write("  → Applying routing logic...")
            
            final_state = workflow.invoke(state)
            
            # Step 4: Display workflow results
            st.write("✓ Workflow execution complete")
            st.write(f"  → Risk Score: {final_state['risk_score']:.0f}/100 ({final_state['risk_category']})")
            st.write(f"  → Final Premium: ₹{final_state['final_premium']:,.0f}")
            
            if final_state['requires_human_review']:
                st.write(f"  → Status: Requires Human Review")
                st.write(f"  → Reason: {final_state['review_reason']}")
            else:
                st.write("  → Status: Auto-Approved")
            
            # Step 5: Update database with complete workflow results
            st.write("💾 Saving workflow results to database...")
            success = update_premium_data(application_id, final_state)
            
            if success:
                st.write("✓ All results saved to database")
                status.update(label="✅ Workflow complete!", state="complete", expanded=False)
                st.session_state.premium_calculated = True
                st.rerun()
            else:
                status.update(label="⚠️ Workflow completed but failed to save", state="error")
                st.warning("Workflow completed but failed to save to database")
                
    except Exception as e:
        st.error(f"❌ Error executing workflow: {str(e)}")
        st.exception(e)


def display_extracted_data(application_id: str):
    """Display extracted data in a table format"""
    st.subheader("📊 Application Data Extract")
    
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
    st.subheader("💵 Decision Making")
    
    # Retrieve data from database
    data = get_application_by_id(application_id)
    
    if not data:
        st.warning("No premium data found")
        return
    
    # Create columns for risk and premium info
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚖️ Risk Assessment")
        
        risk_score_value = data.get('risk_score')
        if risk_score_value is not None:
            risk_score_display = f"{risk_score_value:.0f}/100"
        else:
            risk_score_display = "Not calculated"
        
        risk_df = pd.DataFrame({
            "Field": [
                "Risk Score",
                "Risk Category",
                "Flagged Conditions"
            ],
            "Value": [
                risk_score_display,
                data.get('risk_category', "Not calculated"),
                data.get('flagged_conditions', "None") or "None"
            ]
        })
        st.dataframe(risk_df, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("#### 💰 Best Offer")
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
    
    # ✅ FIX: Show proper approval status based on database values
    st.markdown("#### ✅ Approval Status")
    
    # Determine status from database
    risk_category = data.get('risk_category', '').upper()
    requires_review = data.get('requires_human_review')
    review_reason = data.get('review_reason', 'Not specified')
    current_step = data.get('current_step', '')
    
    # Display appropriate status
    if risk_category == 'DECLINED':
        st.error("### ❌ APPLICATION DECLINED")
        st.markdown(f"""
        **Risk Score:** {data.get('risk_score', 0):.0f}/100  
        **Risk Category:** {risk_category}  
        **Reason:** Application exceeds maximum acceptable risk threshold
        """)
        if data.get('flagged_conditions'):
            st.markdown("**Flagged Issues:**")
            st.warning(data.get('flagged_conditions'))
    
    elif requires_review:
        st.warning("### 👤 REQUIRES HUMAN REVIEW")
        st.markdown(f"""
        **Status:** Pending Manual Review  
        **Risk Category:** {risk_category}  
        **Risk Score:** {data.get('risk_score', 0):.0f}/100  
        **Review Reason:** {review_reason}
        """)
        if data.get('flagged_conditions'):
            st.markdown("**Flagged Conditions:**")
            st.info(data.get('flagged_conditions'))
    
    else:
        st.success("##### ✅ AUTO-APPROVED")
        st.markdown(f"""
        **Status:** Application Approved  
        **Plan:** {data.get('recommended_plan', 'Not assigned')}  
        **Premium:** ₹{data.get('final_premium', 0):,.0f}/year  
        **Risk Category:** {risk_category}
        """)
    
    # Show exclusions if any
    if data.get('exclusions'):
        st.divider()
        st.info(f"📋 **Policy Exclusions:** {data['exclusions']}")

    # ✅ ADD: Button to start new application
    st.divider()
    if st.button("📝 New Application", type="primary"):
        st.session_state.reset_for_new_application = True
        st.session_state.application_form_uploaded = False
        st.session_state.medical_docs_uploaded = False
        st.session_state.application_form_file = None
        st.session_state.medical_docs_files = []
        st.rerun()



# Initialize database on app load
init_db()

# Main application
application_upload()

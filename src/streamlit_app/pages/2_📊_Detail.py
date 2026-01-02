import streamlit as st
import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import base64  # Add this import
import os     # Add this import



sys.path.insert(0, str(Path(__file__).parent.parent))
from streamlit_app.database import get_all_applications, get_application_by_id


def display_pdf_preview(file_path: Path, document_name: str):
    """Display PDF preview with scrollable view"""
    try:
        if not file_path.exists():
            st.error(f"❌ Document not found: {document_name}")
            return
        
        # Read PDF file
        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
        
        # Convert to base64
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        
        # Create expandable section for each document
        with st.expander(f"📄 {document_name}", expanded=False):
            # Embed PDF with scrollable iframe
            pdf_display = f'''
            <iframe 
                src="data:application/pdf;base64,{base64_pdf}" 
                width="100%" 
                height="800px" 
                type="application/pdf"
                style="border: 1px solid #ccc; border-radius: 5px;">
            </iframe>
            '''
            st.markdown(pdf_display, unsafe_allow_html=True)
            
            # Add download button
            st.download_button(
                label=f"⬇️ Download {document_name}",
                data=pdf_bytes,
                file_name=document_name,
                mime="application/pdf"
            )
    
    except Exception as e:
        st.error(f"Error loading PDF: {str(e)}")



def get_approval_status(app_data):
    """Determine approval status based on risk category and review requirements"""
    risk_category = app_data.get('risk_category', '').upper()
    requires_review = app_data.get('requires_human_review')
    current_step = app_data.get('current_step', '')
    
    # Check 1: Human declined
    if current_step == 'human_declined':
        return "Human Declined", "❌", "red"
    
    # Check 2: DECLINED applications (system declined)
    if risk_category == 'DECLINED':
        return "Application Declined", "❌", "red"
    
    # Check 3: Processing not complete
    if requires_review is None:
        return "Processing Incomplete", "⏳", "gray"
    
    # Check 4: Requires human review (HIGH or other review triggers)
    elif requires_review:
        return "Requires Human Review", "👤", "orange"
    
    # Check 5: Human or Auto-approved
    elif current_step == 'completed':
        return "Approved", "✅", "green"
    
    # Check 6: Auto-approved (LOW/MEDIUM without review flags)
    else:
        return "Auto-Approved", "✅", "green"




def display_applications_table():
    """Display table of all applications with premium calculations complete"""
    
    # Retrieve all applications from database
    all_applications = get_all_applications()
    
    if not all_applications:
        st.warning("📭 No applications found in the database.")
        st.info("👉 Please process applications on the **Application** page first.")
        return
    
    # ✅ FIX: Filter to show applications with premium calculation complete
    # Include approved, auto-approved, human declined, and system declined applications
    completed_apps = [
        app for app in all_applications
        if (app.get('final_premium') is not None and
            app.get('risk_score') is not None and
            app.get('current_step') in [
                'premium_calculation_complete', 
                'pending_human_review', 
                'completed',
                'human_declined'  # ← ADD THIS LINE
            ])
    ]
    
    if not completed_apps:
        st.warning("📭 No completed applications found.")
        st.info("👉 Applications must complete the premium calculation process to appear here.")
        return
    
    st.success(f"📋 Found **{len(completed_apps)}** completed application(s)")
    
    # Create filters section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_term = st.text_input(
            "🔍 Search by Name or ID",
            placeholder="Enter applicant name or unique ID...",
            key="search_box"
        )
    
    with col2:
        status_filter = st.selectbox(
            "Filter by Status",
            options=[
                "All", 
                "Auto-Approved", 
                "Requires Human Review", 
                "Human Declined",  # ← ADD THIS OPTION
                "Application Declined"
            ],
            key="status_filter"
        )
    
    with col3:
        sort_order = st.selectbox(
            "Sort by Date",
            options=["Newest First", "Oldest First"],
            key="sort_order"
        )
    
    # Apply filters
    filtered_apps = completed_apps.copy()
    
    # Search filter
    if search_term:
        filtered_apps = [
            app for app in filtered_apps
            if (search_term.lower() in app.get('applicant_name', '').lower() or
                search_term.lower() in app.get('id', '').lower())
        ]
    
    # Status filter
    if status_filter != "All":
        if status_filter == "Auto-Approved":
            filtered_apps = [
                app for app in filtered_apps
                if not app.get('requires_human_review') 
                and app.get('risk_category') != 'DECLINED'
                and app.get('current_step') != 'human_declined'  # ← ADD THIS
            ]
        
        elif status_filter == "Requires Human Review":
            filtered_apps = [
                app for app in filtered_apps
                if app.get('requires_human_review') 
                and app.get('risk_category') != 'DECLINED'
            ]
        
        # ← ADD THIS NEW FILTER
        elif status_filter == "Human Declined":
            filtered_apps = [
                app for app in filtered_apps
                if app.get('current_step') == 'human_declined'
            ]
        
        elif status_filter == "Application Declined":
            filtered_apps = [
                app for app in filtered_apps
                if app.get('risk_category') == 'DECLINED'
            ]
    
    # Sort by date
    filtered_apps = sorted(
        filtered_apps,
        key=lambda x: x.get('upload_time', ''),
        reverse=(sort_order == "Newest First")
    )
    
    if not filtered_apps:
        st.warning("No applications match your search criteria.")
        return
    
    st.write(f"Showing **{len(filtered_apps)}** application(s)")
    
    # Create DataFrame for display
    table_data = []
    for app in filtered_apps:
        status_text, status_icon, status_color = get_approval_status(app)
        
        table_data.append({
            "Unique ID": app.get('id', 'N/A')[:8] + "...",  # Show first 8 chars
            "Name": app.get('applicant_name', 'N/A'),
            "Age": app.get('age', 'N/A'),
            "Gender": app.get('gender', 'N/A'),
            "Contact": app.get('contact_number', 'N/A'),
            "Final Premium": f"₹{app.get('final_premium', 0):,.0f}",
            "Plan": app.get('recommended_plan', 'N/A'),
            "Status": f"{status_icon} {status_text}",
            "_full_id": app.get('id', '')  # Hidden field for click action
        })
    
    # Display table
    df = pd.DataFrame(table_data)
    
    # Use Streamlit's dataframe with column configuration
    st.dataframe(
        df.drop(columns=['_full_id']),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Unique ID": st.column_config.TextColumn("Unique ID", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Age": st.column_config.NumberColumn("Age", width="small"),
            "Gender": st.column_config.TextColumn("Gender", width="small"),
            "Contact": st.column_config.TextColumn("Contact", width="medium"),
            "Final Premium": st.column_config.TextColumn("Final Premium", width="medium"),
            "Plan": st.column_config.TextColumn("Plan", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
        }
    )
    
    st.divider()
    
    # Application Selection for Detailed View
    st.subheader("🔍 View Detailed Information")
    
    # Create selection dropdown
    app_options = {
        f"{app.get('applicant_name', 'Unknown')} ({app.get('id', 'N/A')[:8]}...)": app.get('id')
        for app in filtered_apps
    }
    
    selected_display = st.selectbox(
        "Select an application to view details:",
        options=list(app_options.keys()),
        key="app_selector"
    )
    
    if selected_display:
        selected_id = app_options[selected_display]
        display_detailed_view(selected_id)


def display_detailed_view(application_id: str):
    """Display detailed view of a selected application"""
    data = get_application_by_id(application_id)
    
    if not data:
        st.error("Failed to load application details")
        return
    
    # Get approval status
    status_text, status_icon, status_color = get_approval_status(data)
    
    # Display header with status
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Application Details: {data.get('applicant_name', 'N/A')}")
    
    with col2:
        if status_color == "red":
            st.error(f"{status_icon} {status_text}")
        elif status_color == "orange":
            st.warning(f"{status_icon} {status_text}")
        elif status_color == "green":
            st.success(f"{status_icon} {status_text}")
        else:
            st.info(f"{status_icon} {status_text}")
    
    # ============ HUMAN IN THE LOOP - APPROVE/DECLINE BUTTONS ============
    if data.get('requires_human_review') and data.get('risk_category') != 'DECLINED':
        st.divider()
        st.markdown("### 👤 Human Review Decision")
        st.info(f"**Review Reason:** {data.get('review_reason', 'Not specified')}")
        
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("✅ Approve Application", type="primary", use_container_width=True):
                # Import the new function
                from streamlit_app.database import update_human_review_decision
                
                success = update_human_review_decision(application_id, 'approved')
                
                if success:
                    st.success("✅ Application approved successfully!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to approve application")
        
        with col2:
            if st.button("❌ Decline Application", type="secondary", use_container_width=True):
                # Import the new function
                from streamlit_app.database import update_human_review_decision
                
                success = update_human_review_decision(application_id, 'declined')
                
                if success:
                    st.error("❌ Application declined")
                    st.rerun()
                else:
                    st.error("❌ Failed to decline application")
        
        st.divider()
    # ============ END HUMAN IN THE LOOP ============
    
    # Create tabs for organized display
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 Personal Info",
        "⚕️ Health & Risk",
        "💰 Premium Details",
        "📋 Metadata"
    ])
    
    # ... rest of your existing tab code remains the same ...
    
    with tab1:
        st.markdown("#### Personal Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Full Name:** {data.get('applicant_name', 'N/A')}")
            st.markdown(f"**Age:** {data.get('age', 'N/A')}")
            st.markdown(f"**Gender:** {data.get('gender', 'N/A')}")
            st.markdown(f"**Contact Number:** {data.get('contact_number', 'N/A')}")
        
        with col2:
            st.markdown(f"**Email:** {data.get('email', 'N/A')}")
            st.markdown(f"**Occupation:** {data.get('occupation', 'N/A')}")
            st.markdown(f"**Annual Income:** ₹{data.get('annual_income', 0):,.0f}")
        
        st.markdown("**Address:**")
        st.info(data.get('address', 'N/A'))
    
    with tab2:
        st.markdown("#### Health Assessment")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Health Metrics**")
            st.markdown(f"- **BMI:** {data.get('bmi', 0):.1f}")
            st.markdown(f"- **Smoking Status:** {data.get('smoking_status', 'N/A')}")
            st.markdown(f"- **Alcohol Consumption:** {data.get('alcohol_consumption', 'N/A')}")
        
        with col2:
            st.markdown("**Risk Assessment**")
            st.markdown(f"- **Risk Score:** {data.get('risk_score', 0):.0f}/100")
            st.markdown(f"- **Risk Category:** {data.get('risk_category', 'N/A')}")
        
        # Flagged Conditions
        if data.get('flagged_conditions'):
            st.markdown("**🚩 Flagged Conditions:**")
            conditions = data.get('flagged_conditions', '').split('; ')
            for condition in conditions:
                if condition:
                    st.warning(f"- {condition}")
        else:
            st.success("✅ No flagged conditions")
        
        # Exclusions
        if data.get('exclusions'):
            st.markdown("**📋 Policy Exclusions:**")
            exclusions = data.get('exclusions', '').split('; ')
            for exclusion in exclusions:
                if exclusion:
                    st.info(f"- {exclusion}")
    
    with tab3:
        st.markdown("#### Premium Calculation Breakdown")
        
        # Special handling for DECLINED applications
        if data.get('risk_category') == 'DECLINED':
            st.error("### ❌ APPLICATION DECLINED")
            st.markdown(f"""
This application has been **declined** due to high risk assessment.

**Risk Score:** {data.get('risk_score', 0):.0f}/100  
**Risk Category:** {data.get('risk_category', 'N/A')}  
**Recommended Action:** {data.get('recommended_plan', 'N/A')}
""")
            
            if data.get('flagged_conditions'):
                st.markdown("**Decline Reasons:**")
                conditions = data.get('flagged_conditions', '').split('; ')
                for condition in conditions:
                    if condition:
                        st.warning(f"- {condition}")
        else:
            # Normal premium display for accepted applications
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric(
                    label="Base Premium",
                    value=f"₹{data.get('base_premium', 0):,.0f}"
                )
                
                st.metric(
                    label="Medical Loading",
                    value=f"{data.get('medical_loading_percentage', 0):.0f}%"
                )
            
            with col2:
                st.metric(
                    label="Final Annual Premium",
                    value=f"₹{data.get('final_premium', 0):,.0f}",
                    delta=f"+₹{data.get('final_premium', 0) - data.get('base_premium', 0):,.0f}"
                )
                
                st.metric(
                    label="Recommended Plan",
                    value=data.get('recommended_plan', 'N/A')
                )
    
    with tab4:
        st.markdown("#### Processing Metadata")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Application ID:** `{data.get('id', 'N/A')}`")
            st.markdown(f"**Upload Time:** {data.get('upload_time', 'N/A')}")
            st.markdown(f"**Processing Time:** {data.get('processing_timestamp', 'N/A')}")
        
        with col2:
            st.markdown(f"**Current Step:** {data.get('current_step', 'N/A')}")
        
        # Document Preview Section
        st.divider()
        st.markdown("#### 📄 Application Documents")
        
        filename_str = data.get('filename', '')
        application_id = data.get('id', '')
        
        if filename_str and filename_str != 'N/A':
            document_names = [name.strip() for name in filename_str.split(',')]
            project_root = Path(__file__).parent.parent.parent
            document_dir = project_root / "Document" / application_id
            
            st.info(f"Found **{len(document_names)}** document(s)")
            
            for doc_name in document_names:
                if doc_name:
                    doc_path = document_dir / doc_name
                    display_pdf_preview(doc_path, doc_name)
        else:
            st.warning("⚠️ No documents found for this application")
        
        # Errors section
        if data.get('errors'):
            st.divider()
            st.markdown("**⚠️ Processing Errors/Warnings:**")
            st.code(data.get('errors', ''), language='text')

# ============= FLOATING CHATBOT =============
from streamlit_app.components.chatbot_widget import render_floating_chatbot

# Render floating chatbot widget
render_floating_chatbot()


# Main execution
display_applications_table()

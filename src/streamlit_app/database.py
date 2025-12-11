# streamlit_app/database.py

import sqlite3
from datetime import datetime
from typing import Dict, Optional, List


DB_PATH = 'underwriting.db'


def init_db():
    """Initialize the database with proper schema for underwriting data"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create applications table with all extracted fields + premium fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            filename TEXT,
            
            -- Applicant Information
            applicant_name TEXT,
            age INTEGER,
            gender TEXT,
            contact_number TEXT,
            email TEXT,
            address TEXT,
            occupation TEXT,
            annual_income REAL,
            
            -- Health Information
            bmi REAL,
            smoking_status TEXT,
            alcohol_consumption TEXT,
            
            -- Risk Assessment (NEW)
            risk_score REAL,
            risk_category TEXT,
            flagged_conditions TEXT,
            exclusions TEXT,
            
            -- Premium Calculation (NEW)
            base_premium REAL,
            medical_loading_percentage REAL,
            final_premium REAL,
            recommended_plan TEXT,
            
            -- Workflow Control (NEW)
            requires_human_review BOOLEAN,
            review_reason TEXT,
            
            -- Metadata
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processing_timestamp TEXT,
            current_step TEXT,
            errors TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✓ Database initialized successfully")


def save_extracted_data(application_id: str, filename: str, state: Dict) -> bool:
    """Save extracted underwriting data to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Convert errors list to string for storage
        errors_str = "; ".join(state.get("errors", [])) if state.get("errors") else ""
        
        c.execute('''
            INSERT INTO applications (
                id, filename,
                applicant_name, age, gender, contact_number, email, address, occupation, annual_income,
                bmi, smoking_status, alcohol_consumption,
                processing_timestamp, current_step, errors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_id,
            filename,
            state.get("applicant_name", ""),
            state.get("age", 0),
            state.get("gender", ""),
            state.get("contact_number", ""),
            state.get("email", ""),
            state.get("address", ""),
            state.get("occupation", ""),
            state.get("annual_income", 0.0),
            state.get("bmi", 0.0),
            state.get("smoking_status", ""),
            state.get("alcohol_consumption", ""),
            state.get("processing_timestamp", datetime.now().isoformat()),
            state.get("current_step", ""),
            errors_str
        ))
        
        conn.commit()
        conn.close()
        print(f"✓ Data saved to database for application ID: {application_id}")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False


def update_premium_data(application_id: str, state: Dict) -> bool:
    """Update application record with premium calculation results"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Convert lists to strings for storage
        flagged_conditions_str = "; ".join(state.get("flagged_conditions", [])) if state.get("flagged_conditions") else ""
        exclusions_str = "; ".join(state.get("exclusions", [])) if state.get("exclusions") else ""
        errors_str = "; ".join(state.get("errors", [])) if state.get("errors") else ""
        
        c.execute('''
            UPDATE applications SET
                risk_score = ?,
                risk_category = ?,
                flagged_conditions = ?,
                exclusions = ?,
                base_premium = ?,
                medical_loading_percentage = ?,
                final_premium = ?,
                recommended_plan = ?,
                requires_human_review = ?,
                review_reason = ?,
                current_step = ?,
                errors = ?
            WHERE id = ?
        ''', (
            state.get("risk_score", 0.0),
            state.get("risk_category", ""),
            flagged_conditions_str,
            exclusions_str,
            state.get("base_premium", 0.0),
            state.get("medical_loading_percentage", 0.0),
            state.get("final_premium", 0.0),
            state.get("recommended_plan", ""),
            state.get("requires_human_review", False),
            state.get("review_reason", ""),
            state.get("current_step", ""),
            errors_str,
            application_id
        ))
        
        conn.commit()
        conn.close()
        print(f"✓ Premium data updated for application ID: {application_id}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating premium data: {e}")
        return False


def get_application_by_id(application_id: str) -> Optional[Dict]:
    """Retrieve application data from database by ID"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM applications WHERE id = ?', (application_id,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return None
        
        # Convert Row object to dictionary
        return dict(row)
        
    except Exception as e:
        print(f"❌ Error retrieving data: {e}")
        return None


def get_state_from_db(application_id: str) -> Optional[Dict]:
    """Reconstruct UnderwritingState from database for workflow execution"""
    data = get_application_by_id(application_id)
    
    if not data:
        return None
    
    # Reconstruct state dictionary matching UnderwritingState structure
    state = {
        "applicant_name": data.get("applicant_name", ""),
        "age": data.get("age", 0),
        "gender": data.get("gender", ""),
        "contact_number": data.get("contact_number", ""),
        "email": data.get("email", ""),
        "address": data.get("address", ""),
        "occupation": data.get("occupation", ""),
        "annual_income": data.get("annual_income", 0.0),
        "bmi": data.get("bmi", 0.0),
        "smoking_status": data.get("smoking_status", ""),
        "alcohol_consumption": data.get("alcohol_consumption", ""),
        "risk_score": data.get("risk_score", 0.0),
        "risk_category": data.get("risk_category", ""),
        "flagged_conditions": data.get("flagged_conditions", "").split("; ") if data.get("flagged_conditions") else [],
        "exclusions": data.get("exclusions", "").split("; ") if data.get("exclusions") else [],
        "base_premium": data.get("base_premium", 0.0),
        "medical_loading_percentage": data.get("medical_loading_percentage", 0.0),
        "final_premium": data.get("final_premium", 0.0),
        "recommended_plan": data.get("recommended_plan", ""),
        "requires_human_review": bool(data.get("requires_human_review", False)),
        "review_reason": data.get("review_reason", ""),
        "current_step": data.get("current_step", ""),
        "errors": data.get("errors", "").split("; ") if data.get("errors") else [],
        "processing_timestamp": data.get("processing_timestamp", "")
    }
    
    return state


def get_all_applications():
    """Retrieve all applications from database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        
        c.execute('SELECT * FROM applications ORDER BY upload_time DESC')
        rows = c.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
        
    except Exception as e:
        print(f"❌ Error retrieving applications: {e}")
        return []

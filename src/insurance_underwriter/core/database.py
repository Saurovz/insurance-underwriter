import sqlite3
import json
from datetime import datetime
from typing import Dict, Optional, List

DB_PATH = 'D:\\Ai_React\\insurance-underwriter\\src\\insurance_underwriter\\underwriting.db'

def auto_migrate_database():
    """Automatically migrate database schema if needed - runs on app startup"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check if table exists first
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='applications'")
        if not c.fetchone():
            conn.close()
            return

        # Check existing columns
        c.execute("PRAGMA table_info(applications)")
        columns = [col[1] for col in c.fetchall()]

        # List of columns that should exist
        required_columns = {
            "kyc_filename": "TEXT",
            "date_of_birth": "TEXT",
            "kyc_document_path": "TEXT",
            "kyc_verification_status": "TEXT",
            "kyc_document_type": "TEXT",
            "kyc_discrepancies": "TEXT",
            "kyc_total_discrepancies": "INTEGER",
            "kyc_verification_message": "TEXT"
        }

        # Add missing columns
        for col_name, col_type in required_columns.items():
            if col_name not in columns:
                c.execute(f"ALTER TABLE applications ADD COLUMN {col_name} {col_type}")
                print(f"✅ Auto-migrated: Added column '{col_name}'")

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"⚠️ Auto-migration error: {e}")


def init_db():
    """Initialize the database with proper schema for underwriting data"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create applications table with all extracted fields + premium fields + KYC fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            filename TEXT,
            kyc_filename TEXT,

            -- Applicant Information
            applicant_name TEXT,
            age INTEGER,
            gender TEXT,
            contact_number TEXT,
            email TEXT,
            address TEXT,
            occupation TEXT,
            annual_income REAL,
            date_of_birth TEXT,

            -- Health Information
            bmi REAL,
            smoking_status TEXT,
            alcohol_consumption TEXT,

            -- KYC Verification Fields
            kyc_document_path TEXT,
            kyc_verification_status TEXT,
            kyc_document_type TEXT,
            kyc_discrepancies TEXT,
            kyc_total_discrepancies INTEGER,
            kyc_verification_message TEXT,

            -- Risk Assessment
            risk_score REAL,
            risk_category TEXT,
            flagged_conditions TEXT,
            exclusions TEXT,

            -- Premium Calculation
            base_premium REAL,
            medical_loading_percentage REAL,
            final_premium REAL,
            recommended_plan TEXT,

            -- Workflow Control
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

    # Auto-migrate existing tables if needed
    auto_migrate_database()


def save_extracted_data(application_id: str, filename: str, state: Dict, kyc_filename: str = None) -> bool:
    """Save extracted underwriting data to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Convert errors list to string for storage
        errors_str = "; ".join(state.get("errors", [])) if state.get("errors") else ""

        # Convert KYC discrepancies to JSON string
        kyc_discrepancies_str = json.dumps(state.get("kyc_discrepancies", []))

        c.execute('''
            INSERT INTO applications (
                id, filename, kyc_filename,
                applicant_name, age, gender, contact_number, email, address, occupation, annual_income, date_of_birth,
                bmi, smoking_status, alcohol_consumption, kyc_document_path,
                kyc_verification_status, kyc_document_type, kyc_discrepancies, kyc_total_discrepancies, kyc_verification_message,
                processing_timestamp, current_step, errors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_id,
            filename,
            kyc_filename,
            state.get("applicant_name", ""),
            state.get("age", 0),
            state.get("gender", ""),
            state.get("contact_number", ""),
            state.get("email", ""),
            state.get("address", ""),
            state.get("occupation", ""),
            state.get("annual_income", 0.0),
            state.get("date_of_birth", ""),
            state.get("bmi", 0.0),
            state.get("smoking_status", ""),
            state.get("alcohol_consumption", ""),
            state.get("kyc_document_path", ""),
            state.get("kyc_verification_status", "NOT_PROVIDED"),
            state.get("kyc_document_type", "None"),
            kyc_discrepancies_str,
            state.get("kyc_total_discrepancies", 0),
            state.get("kyc_verification_message", ""),
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

        # Convert KYC discrepancies to JSON string
        kyc_discrepancies_str = json.dumps(state.get("kyc_discrepancies", []))

        c.execute('''
            UPDATE applications SET
                kyc_verification_status = ?,
                kyc_document_type = ?,
                kyc_discrepancies = ?,
                kyc_total_discrepancies = ?,
                kyc_verification_message = ?,
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
            state.get("kyc_verification_status", "NOT_PROVIDED"),
            state.get("kyc_document_type", "None"),
            kyc_discrepancies_str,
            state.get("kyc_total_discrepancies", 0),
            state.get("kyc_verification_message", ""),
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
        data = dict(row)

        # Parse JSON discrepancies back to list
        if data.get("kyc_discrepancies"):
            try:
                data["kyc_discrepancies"] = json.loads(data["kyc_discrepancies"])
            except:
                data["kyc_discrepancies"] = []
        else:
            data["kyc_discrepancies"] = []

        return data

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
        "date_of_birth": data.get("date_of_birth", ""),
        "bmi": data.get("bmi", 0.0),
        "smoking_status": data.get("smoking_status", ""),
        "alcohol_consumption": data.get("alcohol_consumption", ""),

        # KYC fields
        # "kyc_document_path": "",  # Not stored in DB, only during processing
        "kyc_document_path": data.get("kyc_document_path", ""),
        "kyc_verification_status": data.get("kyc_verification_status", "NOT_PROVIDED"),
        "kyc_document_type": data.get("kyc_document_type", "None"),
        "kyc_discrepancies": data.get("kyc_discrepancies", []),
        "kyc_total_discrepancies": data.get("kyc_total_discrepancies", 0),
        "kyc_verification_message": data.get("kyc_verification_message", ""),

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

        # Convert rows and parse KYC discrepancies
        applications = []
        for row in rows:
            data = dict(row)
            if data.get("kyc_discrepancies"):
                try:
                    data["kyc_discrepancies"] = json.loads(data["kyc_discrepancies"])
                except:
                    data["kyc_discrepancies"] = []
            applications.append(data)

        return applications

    except Exception as e:
        print(f"❌ Error retrieving applications: {e}")
        return []


def update_human_review_decision(application_id: str, decision: str, reviewer_name: str = None) -> bool:
    """
    Update application with human review decision

    Args:
        application_id: Unique application ID
        decision: 'approved' or 'declined'
        reviewer_name: Optional name of the reviewer

    Returns:
        bool: Success status
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Determine new status based on decision
        if decision.lower() == 'approved':
            new_status = 'completed'
            requires_review = False
        elif decision.lower() == 'declined':
            new_status = 'human_declined'
            requires_review = False
        else:
            raise ValueError(f"Invalid decision: {decision}")

        # Update application
        c.execute('''
            UPDATE applications SET
                requires_human_review = ?,
                current_step = ?,
                processing_timestamp = ?
            WHERE id = ?
        ''', (
            requires_review,
            new_status,
            datetime.now().isoformat(),
            application_id
        ))

        conn.commit()
        conn.close()
        print(f"✓ Human review decision '{decision}' recorded for application ID: {application_id}")
        return True

    except Exception as e:
        print(f"❌ Error updating human review decision: {e}")
        return False

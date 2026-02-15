# src/backend/api/main.py

from fastapi import FastAPI, File, UploadFile, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional
from contextlib import asynccontextmanager
import sys
from pathlib import Path
import uuid
import json
from datetime import datetime
import shutil

# Add project root to path
project_root = Path(__file__).resolve().parents[1]

# Add Backend/src to Python path
sys.path.insert(0, str(project_root / "src"))

from src.insurance_underwriter.core.document_extract_node import update_state_from_pdfs
from src.insurance_underwriter.core.policy_knowledge_base import PolicyKnowledgeBase
from src.insurance_underwriter.config.initial_state import create_initial_state
from src.insurance_underwriter.core.graph import build_underwriting_workflow
from src.insurance_underwriter.core.chatbot_service import get_chatbot_service
from src.insurance_underwriter.core.database import (
    init_db,
    save_extracted_data,
    get_application_by_id,
    get_state_from_db,
    update_premium_data,
    get_all_applications
)

# ✅ Lifespan event handler (replaces deprecated on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting Insurance Underwriting API...")
    init_db()
    print("✅ Database initialized")
    print("🚀 API Server running on http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    yield
    # Shutdown
    print("🛑 Shutting down...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Insurance Underwriting API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - Allow React apps to communicate
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:3000",  # Landingzone
        "http://localhost:3001",  # Insurance Frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"✅ WebSocket connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"❌ WebSocket disconnected: {client_id}")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception as e:
                print(f"Error sending message to {client_id}: {e}")

manager = ConnectionManager()

# ============= ENDPOINTS =============

@app.get("/")
async def root():
    return {
        "message": "Insurance Underwriting API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/api/upload",
            "process": "/api/process-documents/{application_id}",
            "evaluate": "/api/evaluate/{application_id}",
            "application": "/api/application/{application_id}",
            "chatbot": "/api/chatbot",
            "configuration": "/api/configuration/*",
            "docs": "/docs"
        }
    }

@app.post("/api/upload")
async def upload_files(
    application_form: UploadFile = File(...),
    medical_docs: List[UploadFile] = File(...),
    kyc_document: Optional[UploadFile] = File(None)
):
    """Upload application form, medical documents, and optional KYC document"""
    try:
        # Generate unique application ID
        application_id = str(uuid.uuid4())
        
        # Create save directory
        save_dir = project_root / "Document" / application_id
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Save application form
        app_form_path = save_dir / application_form.filename
        with open(app_form_path, "wb") as f:
            content = await application_form.read()
            f.write(content)
        print(f"✅ Saved: {application_form.filename}")
        
        # Save medical documents
        medical_filenames = []
        for doc in medical_docs:
            doc_path = save_dir / doc.filename
            with open(doc_path, "wb") as f:
                content = await doc.read()
                f.write(content)
            medical_filenames.append(doc.filename)
            print(f"✅ Saved: {doc.filename}")
        
        # Save KYC document if provided
        kyc_filename = None
        if kyc_document:
            kyc_path = save_dir / kyc_document.filename
            with open(kyc_path, "wb") as f:
                content = await kyc_document.read()
                f.write(content)
            kyc_filename = kyc_document.filename
            print(f"✅ Saved KYC: {kyc_document.filename}")
        
        total_files = 1 + len(medical_filenames) + (1 if kyc_filename else 0)
        
        return JSONResponse({
            "success": True,
            "application_id": application_id,
            "message": f"Successfully uploaded {total_files} file(s)",
            "files": {
                "application_form": application_form.filename,
                "medical_docs": medical_filenames,
                "kyc_document": kyc_filename,
                "total_files": total_files
            }
        })
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/api/process-documents/{application_id}")
async def process_documents(application_id: str):
    """Extract data from uploaded PDFs using LLM"""
    try:
        print(f"🔄 Processing documents for: {application_id}")
        
        # Get document directory
        doc_dir = project_root / "Document" / application_id
        if not doc_dir.exists():
            raise HTTPException(status_code=404, detail="Documents not found")
        
        # Send WebSocket update - Starting
        await manager.send_message(application_id, {
            "step": "extraction",
            "message": "Extracting data from PDFs using LLM...",
            "progress": 20
        })
        
        # Create initial state
        state = create_initial_state()
        
        # Extract data from PDFs
        updated_state = update_state_from_pdfs(state, str(doc_dir))
        
        # Send WebSocket update - Extraction complete
        await manager.send_message(application_id, {
            "step": "extraction",
            "message": "Data extraction completed",
            "progress": 50
        })
        
        # Check for errors
        if updated_state.get("errors"):
            return JSONResponse({
                "success": False,
                "errors": updated_state["errors"],
                "message": "Data extraction completed with errors"
            })
        
        # Save extracted data to database
        all_files = list(doc_dir.glob("*.pdf")) + list(doc_dir.glob("*.jpg")) + list(doc_dir.glob("*.jpeg")) + list(doc_dir.glob("*.png"))
        combined_filename = ", ".join([f.name for f in all_files])
        
        # Get KYC filename if exists
        kyc_files = [f for f in all_files if "kyc" in f.name.lower() or "aadhaar" in f.name.lower() or "pan" in f.name.lower()]
        kyc_filename = kyc_files[0].name if kyc_files else None
        
        # Send WebSocket update - Saving
        await manager.send_message(application_id, {
            "step": "saving",
            "message": "Saving to database...",
            "progress": 70
        })
        
        success = save_extracted_data(
            application_id,
            combined_filename,
            updated_state,
            kyc_filename=kyc_filename
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save to database")
        
        # Send WebSocket update - Complete
        await manager.send_message(application_id, {
            "step": "complete",
            "message": "Processing complete!",
            "progress": 100
        })
        
        print(f"✅ Processing complete for: {application_id}")
        
        return JSONResponse({
            "success": True,
            "application_id": application_id,
            "data": {
                "applicant_name": updated_state.get("applicant_name"),
                "age": updated_state.get("age"),
                "gender": updated_state.get("gender"),
                "bmi": updated_state.get("bmi"),
                "smoking_status": updated_state.get("smoking_status"),
                "alcohol_consumption": updated_state.get("alcohol_consumption"),
                "contact_number": updated_state.get("contact_number"),
                "email": updated_state.get("email"),
                "address": updated_state.get("address"),
                "occupation": updated_state.get("occupation"),
                "annual_income": updated_state.get("annual_income"),
            },
            "message": "Data extracted successfully"
        })
    except Exception as e:
        print(f"❌ Processing error: {str(e)}")
        await manager.send_message(application_id, {
            "step": "error",
            "message": f"Error: {str(e)}",
            "progress": 0
        })
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/evaluate/{application_id}")
async def evaluate_application(application_id: str):
    """Execute underwriting workflow (risk evaluation + premium calculation)"""
    try:
        print(f"🔄 Evaluating application: {application_id}")
        
        # Retrieve state from database
        state = get_state_from_db(application_id)
        if not state:
            raise HTTPException(status_code=404, detail="Application not found")
        
        # Send WebSocket update - Risk evaluation
        await manager.send_message(application_id, {
            "step": "risk_evaluation",
            "message": "Evaluating risk with RAG...",
            "progress": 30
        })
        
        # Build and execute workflow
        workflow = build_underwriting_workflow(skip_document_parsing=True)
        
        # Send WebSocket update - Premium calculation
        await manager.send_message(application_id, {
            "step": "premium_calculation",
            "message": "Calculating premium...",
            "progress": 60
        })
        
        final_state = workflow.invoke(state)
        
        # Send WebSocket update - Saving results
        await manager.send_message(application_id, {
            "step": "saving_results",
            "message": "Saving results...",
            "progress": 85
        })
        
        # Save workflow results to database
        success = update_premium_data(application_id, final_state)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save results")
        
        # Send WebSocket update - Complete
        await manager.send_message(application_id, {
            "step": "complete",
            "message": "Evaluation complete!",
            "progress": 100
        })
        
        print(f"✅ Evaluation complete for: {application_id}")
        
        return JSONResponse({
            "success": True,
            "application_id": application_id,
            "results": {
                "risk_score": final_state.get("risk_score"),
                "risk_category": final_state.get("risk_category"),
                "base_premium": final_state.get("base_premium"),
                "medical_loading_percentage": final_state.get("medical_loading_percentage"),
                "final_premium": final_state.get("final_premium"),
                "recommended_plan": final_state.get("recommended_plan"),
                "requires_human_review": final_state.get("requires_human_review"),
                "review_reason": final_state.get("review_reason"),
                "flagged_conditions": final_state.get("flagged_conditions", []),
                "exclusions": final_state.get("exclusions", []),
                "kyc_verification_status": final_state.get("kyc_verification_status"),
                "kyc_verification_message": final_state.get("kyc_verification_message"),
            },
            "message": "Evaluation completed successfully"
        })
    except Exception as e:
        print(f"❌ Evaluation error: {str(e)}")
        await manager.send_message(application_id, {
            "step": "error",
            "message": f"Error: {str(e)}",
            "progress": 0
        })
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/api/application/{application_id}")
async def get_application(application_id: str):
    """Get application data by ID"""
    try:
        data = get_application_by_id(application_id)
        if not data:
            raise HTTPException(status_code=404, detail="Application not found")
        
        return JSONResponse({
            "success": True,
            "data": data
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve application: {str(e)}")

@app.get("/api/applications")
async def get_applications():
    """Get all applications"""
    try:
        applications = get_all_applications()
        return JSONResponse({
            "success": True,
            "count": len(applications),
            "applications": applications
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve applications: {str(e)}")

@app.post("/api/chatbot")
async def chatbot_query(query: dict):
    """Handle chatbot queries about policy rules"""
    try:
        user_query = query.get("message")
        chat_history = query.get("history", [])
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Get chatbot service
        chatbot_service = get_chatbot_service()
        
        # Generate response
        response = chatbot_service.generate_chatbot_response(
            user_query=user_query,
            conversation_history=chat_history
        )
        
        return JSONResponse({
            "success": True,
            "response": response
        })
    except Exception as e:
        print(f"❌ Chatbot error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chatbot error: {str(e)}")

# ============= CONFIGURATION ENDPOINTS =============

@app.post("/api/configuration/check-policy")
async def check_policy_exists():
    """Check if policy knowledge base already exists"""
    try:
        from src.insurance_underwriter.config.config import CHROMA_DB_PATH
        kb = PolicyKnowledgeBase(db_path=CHROMA_DB_PATH)
        existing_collections = [col.name for col in kb.client.list_collections()]
        exists = kb.collection_name in existing_collections
        
        return JSONResponse({
            "success": True,
            "exists": exists,
            "collection_name": kb.collection_name,
            "db_path": CHROMA_DB_PATH
        })
    except Exception as e:
        print(f"❌ Error checking policy: {str(e)}")
        return JSONResponse({
            "success": False,
            "exists": False,
            "error": str(e)
        })

@app.post("/api/configuration/upload-policy")
async def upload_policy_document(
    policy_pdf: UploadFile = File(...),
    force_reload: bool = False
):
    """Upload and process policy PDF to create ChromaDB knowledge base"""
    try:
        print(f"📄 Uploading policy document: {policy_pdf.filename}")
        
        # Validate file type
        if not policy_pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save policy PDF to Document directory
        policy_dir = project_root / "Document" / "PolicyDocs"
        policy_dir.mkdir(parents=True, exist_ok=True)
        policy_path = policy_dir / policy_pdf.filename
        
        with open(policy_path, "wb") as f:
            content = await policy_pdf.read()
            f.write(content)
        
        print(f"✅ Saved policy PDF to: {policy_path}")
        
        # Send initial progress
        await manager.send_message("policy_upload", {
            "step": "upload",
            "message": "Policy PDF uploaded successfully",
            "progress": 10
        })
        
        # Initialize PolicyKnowledgeBase
        from src.insurance_underwriter.config.config import CHROMA_DB_PATH
        kb = PolicyKnowledgeBase(db_path=CHROMA_DB_PATH)
        
        # Check if collection exists
        existing_collections = [col.name for col in kb.client.list_collections()]
        if kb.collection_name in existing_collections:
            if force_reload:
                print(f"🗑️ Deleting existing collection: {kb.collection_name}")
                kb.client.delete_collection(kb.collection_name)
                await manager.send_message("policy_upload", {
                    "step": "deleting",
                    "message": "Deleting existing policy knowledge base...",
                    "progress": 20
                })
            else:
                return JSONResponse({
                    "success": False,
                    "message": "Policy knowledge base already exists. Set force_reload=true to overwrite.",
                    "exists": True
                })
        
        # Load and index policy
        await manager.send_message("policy_upload", {
            "step": "processing",
            "message": "Processing policy document and creating embeddings...",
            "progress": 30
        })
        
        kb.load_and_index_policy(str(policy_path), force_reload=force_reload)
        
        await manager.send_message("policy_upload", {
            "step": "complete",
            "message": "Policy knowledge base created successfully!",
            "progress": 100
        })
        
        print(f"✅ Policy knowledge base created successfully")
        
        return JSONResponse({
            "success": True,
            "message": "Policy knowledge base created successfully",
            "db_path": CHROMA_DB_PATH,
            "collection_name": kb.collection_name,
            "file_path": str(policy_path)
        })
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Policy upload error: {str(e)}")
        await manager.send_message("policy_upload", {
            "step": "error",
            "message": f"Error: {str(e)}",
            "progress": 0
        })
        raise HTTPException(status_code=500, detail=f"Policy upload failed: {str(e)}")

@app.get("/api/documents/{application_id}/{filename}")
async def get_document(application_id: str, filename: str):
    """Serve uploaded documents"""
    try:
        doc_path = project_root / "Document" / application_id / filename
        if not doc_path.exists():
            raise HTTPException(status_code=404, detail="Document not found")
        return FileResponse(doc_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket for real-time updates during processing"""
    await manager.connect(websocket, client_id)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # You can handle incoming messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

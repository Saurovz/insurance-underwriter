from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from pathlib import Path
from chatbot import chatbot
import os
from datetime import datetime
import shutil
import json


# Import your existing functions from main.py
from main import (
    Config,
    transcribe_and_detect_language,
    translate_to_english,
    extract_patient_info_from_transcript,
    parse_doctor_advice_structured,
    generate_questcare_prescription_html,
    create_patient_record,
    save_patient_metadata,
    extract_audio  # Added for video processing
)


from xhtml2pdf import pisa


# Initialize FastAPI
app = FastAPI(title="Medical Consultation API")


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Setup directories
Config.setup_directories()
Config.validate_api_key()


# Directories
AUDIO_DIR = Path("./audio")
PATIENT_RECORDS_DIR = Path("./patient_records")
AUDIO_DIR.mkdir(exist_ok=True)
PATIENT_RECORDS_DIR.mkdir(exist_ok=True)


# In-memory session storage (replace with Redis/DB in production)
session_data = {}


# Request Models
class DoctorAdviceRequest(BaseModel):
    patient_id: str
    doctor_advice: str
    input_type: str  # "text" or "voice"


class PrescriptionRequest(BaseModel):
    patient_id: str


@app.get("/")
async def root():
    return {"message": "Medical Consultation API", "status": "running"}


@app.post("/upload-video")
async def upload_video(video: UploadFile = File(...)):
    """Upload patient video, extract audio, and automatically transcribe"""
    try:
        # Generate unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        patient_id = f"patient_{timestamp}"
        
        # Create patient directory
        patient_dir = PATIENT_RECORDS_DIR / patient_id
        patient_dir.mkdir(exist_ok=True, parents=True)
        
        # Save video file
        video_filename = f"{patient_id}_video{Path(video.filename).suffix}"
        video_path = patient_dir / video_filename
        
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(video.file, buffer)
        
        print(f"📹 Video uploaded: {video_path}")
        
        # Extract audio from video using main.py function
        audio_filename = f"{patient_id}_audio.mp3"
        audio_path = patient_dir / audio_filename
        
        print("🎵 Extracting audio from video...")
        extraction_success = extract_audio(str(video_path), str(audio_path))
        
        if not extraction_success:
            raise HTTPException(status_code=500, detail="Audio extraction failed")
        
        print(f"✓ Audio extracted: {audio_path}")
        
        # Automatically start transcription
        print("🗣️ Starting transcription...")
        transcription, detected_lang, lang_code = transcribe_and_detect_language(str(audio_path))
        
        if not transcription:
            raise HTTPException(status_code=500, detail="Transcription failed")
        
        print(f"✓ Transcription complete: {transcription[:100]}...")
        
        # Translate to English if needed
        english_symptoms = transcription
        if detected_lang != 'en':
            english_symptoms = translate_to_english(str(audio_path))
        
        # Extract patient info
        patient_info = extract_patient_info_from_transcript(transcription)
        
        # Store in session
        session_data[patient_id] = {
            "patient_id": patient_id,
            "video_path": str(video_path),
            "audio_path": str(audio_path),
            "original_symptoms": transcription,
            "english_symptoms": english_symptoms,
            "detected_language": detected_lang,
            "patient_info": patient_info,
            "timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "patient_id": patient_id,
            "transcription": transcription,
            "english_transcription": english_symptoms,
            "detected_language": detected_lang,
            "patient_info": patient_info,
            "video_url": f"/patient-media/{patient_id}/{video_filename}",
            "audio_url": f"/patient-media/{patient_id}/{audio_filename}"
        }
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/patient-media/{patient_id}/{filename}")
async def get_patient_media(patient_id: str, filename: str):
    """Serve patient video/audio files"""
    file_path = PATIENT_RECORDS_DIR / patient_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


@app.post("/doctor-advice")
async def save_doctor_advice(request: DoctorAdviceRequest):
    """Save doctor's advice (text or voice)"""
    try:
        patient_id = request.patient_id
        
        if patient_id not in session_data:
            raise HTTPException(status_code=404, detail="Patient session not found")
        
        # Store doctor's advice
        session_data[patient_id]["doctor_advice"] = request.doctor_advice
        session_data[patient_id]["advice_input_type"] = request.input_type
        
        return {
            "success": True,
            "message": "Doctor's advice saved",
            "patient_id": patient_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-prescription")
async def generate_prescription(request: PrescriptionRequest):
    """Generate prescription PDF"""
    try:
        patient_id = request.patient_id
        
        if patient_id not in session_data:
            raise HTTPException(status_code=404, detail="Patient session not found")
        
        session = session_data[patient_id]
        
        # Check if doctor's advice exists
        if "doctor_advice" not in session:
            raise HTTPException(status_code=400, detail="Doctor's advice not provided")
        
        print("📋 Parsing medical information...")
        
        # Parse doctor's advice
        parsed_advice = parse_doctor_advice_structured(
            session["doctor_advice"],
            session["english_symptoms"]
        )
        
        print(f"✓ Parsed {len(parsed_advice.get('medicines', []))} medicines")
        
        # Create patient record directory (use existing one)
        patient_dir = PATIENT_RECORDS_DIR / patient_id
        
        # Generate HTML
        patient_data = {
            "patient_id": patient_id,
            "language": session["detected_language"]
        }
        
        html_content = generate_questcare_prescription_html(
            session["patient_info"],
            parsed_advice,
            patient_data
        )
        
        # Save HTML
        html_path = patient_dir / "prescription.html"
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        
        # Generate PDF
        pdf_path = patient_dir / "prescription.pdf"
        with open(pdf_path, "wb") as pdf_file:
            pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)
        
        if pisa_status.err:
            print("⚠ PDF generation had issues, but HTML saved")
        
        # Save metadata
        metadata = {
            "patient_id": patient_id,
            "timestamp": session["timestamp"],
            "detected_language": session["detected_language"],
            "patient_info": session["patient_info"],
            "original_symptoms": session["original_symptoms"],
            "english_symptoms": session["english_symptoms"],
            "doctor_advice": session["doctor_advice"],
            "parsed_prescription": parsed_advice,
            "video_path": session.get("video_path", "N/A"),
            "audio_path": session.get("audio_path", "N/A")
        }
        
        save_patient_metadata(patient_dir, metadata)
        
        print(f"✓ Prescription generated: {pdf_path}")
        
        return {
            "success": True,
            "message": "Prescription generated successfully",
            "patient_id": patient_id,
            "pdf_url": f"/prescription/{patient_id}/prescription.pdf",
            "video_url": f"/prescription/{patient_id}/prescription.html",
            "parsed_data": parsed_advice
        }
        
    except Exception as e:
        print(f"❌ Error generating prescription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/prescription/{patient_folder}/{filename}")
async def get_prescription_file(patient_folder: str, filename: str):
    """Serve prescription files (PDF or HTML)"""
    file_path = PATIENT_RECORDS_DIR / patient_folder / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


@app.get("/session/{patient_id}")
async def get_session(patient_id: str):
    """Get session data for a patient"""
    if patient_id not in session_data:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session_data[patient_id]


@app.post("/chatbot/init")
async def initialize_chatbot(request: dict):
    """Initialize chatbot with patient transcription"""
    try:
        patient_id = request.get("patient_id")
        
        if patient_id not in session_data:
            raise HTTPException(status_code=404, detail="Patient session not found")
        
        session = session_data[patient_id]
        
        # Add transcription to ChromaDB
        success = chatbot.add_patient_transcription(
            patient_id=patient_id,
            transcription=session["english_symptoms"],
            patient_info=session["patient_info"]
        )
        
        if success:
            return {
                "success": True,
                "message": "Chatbot initialized with patient data",
                "patient_id": patient_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize chatbot")
            
    except Exception as e:
        print(f"❌ Chatbot init error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chatbot/query")
async def chatbot_query(request: dict):
    """Query chatbot with a question"""
    try:
        patient_id = request.get("patient_id")
        question = request.get("question")
        
        if not patient_id or not question:
            raise HTTPException(status_code=400, detail="Missing patient_id or question")
        
        if patient_id not in session_data:
            raise HTTPException(status_code=404, detail="Patient session not found")
        
        session = session_data[patient_id]
        
        # Generate answer using RAG
        answer = chatbot.generate_answer(
            patient_id=patient_id,
            question=question,
            patient_info=session["patient_info"]
        )
        
        return {
            "success": True,
            "question": question,
            "answer": answer,
            "patient_id": patient_id
        }
        
    except Exception as e:
        print(f"❌ Chatbot query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/chatbot/cleanup/{patient_id}")
async def cleanup_chatbot(patient_id: str):
    """Clean up chatbot data for a patient"""
    try:
        chatbot.delete_patient_collection(patient_id)
        return {
            "success": True,
            "message": f"Chatbot data cleaned up for {patient_id}"
        }
    except Exception as e:
        print(f"⚠ Cleanup warning: {str(e)}")
        return {
            "success": True,
            "message": "Cleanup attempted"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

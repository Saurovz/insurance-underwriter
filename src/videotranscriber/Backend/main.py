import os
import sys
import json
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# FFmpeg setup
ffmpeg_path = r"D:\Dependices\ffmpeg-master-latest-win64-gpl-shared\ffmpeg-master-latest-win64-gpl-shared\bin"
os.environ["PATH"] += os.pathsep + ffmpeg_path
load_dotenv()

import whisper
from moviepy import VideoFileClip
import speech_recognition as sr
from xhtml2pdf import pisa

# =========================
# CONFIGURATION
# =========================
class Config:
    HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

    # Model endpoints
    TRANSLATION_MODEL = "ai4bharat/indictrans2-en-indic-1B"
    MEDITRON_MODEL = "mistralai/Mistral-7B-Instruct-v0.2"
    TTS_MODEL = "facebook/mms-tts-hin"

    # Directories
    BASE_DIR = Path("./patient_records")
    VIDEOS_DIR = Path("./videos")
    AUDIO_DIR = Path("./audio")  # Changed to audio directory

    WHISPER_MODEL = "medium"

    @staticmethod
    def setup_directories():
        Config.BASE_DIR.mkdir(exist_ok=True)
        Config.VIDEOS_DIR.mkdir(exist_ok=True)
        Config.AUDIO_DIR.mkdir(exist_ok=True)

    @staticmethod
    def validate_api_key():
        if not Config.HF_API_KEY:
            print("❌ ERROR: HUGGINGFACE_API_KEY not found in .env file!")
            print("\nPlease create a .env file with:")
            print("HUGGINGFACE_API_KEY=your_actual_key_here")
            return False
        print(f"✓ API Key loaded: {Config.HF_API_KEY[:10]}...{Config.HF_API_KEY[-4:]}")
        return True

# =========================
# AUDIO EXTRACTION (Kept for backward compatibility if needed)
# =========================
def extract_audio(video_path, output_audio_path):
    """Extract audio from video file"""
    try:
        video = VideoFileClip(video_path)
        audio = video.audio

        audio.write_audiofile(
            output_audio_path,
            codec='mp3',
            bitrate='192k',
            fps=44100,
            nbytes=2,
            logger=None
        )

        audio.close()
        video.close()
        print(f"✓ Audio extracted: {output_audio_path}")
        return True

    except Exception as e:
        print(f"✗ Audio extraction error: {e}")
        try:
            print("Trying alternative method...")
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(output_audio_path)
            audio.close()
            video.close()
            print(f"✓ Audio extracted (alternative method): {output_audio_path}")
            return True
        except Exception as e2:
            print(f"✗ Alternative method also failed: {e2}")
            return False

# =========================
# LANGUAGE DETECTION & TRANSCRIPTION
# =========================
def transcribe_and_detect_language(audio_path):
    """Transcribe audio and detect language using Whisper"""
    try:
        print("Loading Whisper model...")
        model = whisper.load_model(Config.WHISPER_MODEL)

        print("Transcribing and detecting language...")
        result = model.transcribe(str(audio_path))

        detected_lang = result['language']
        transcribed_text = result['text']

        print(f"✓ Detected language: {detected_lang}")
        print(f"✓ Transcription: {transcribed_text[:100]}...")

        return transcribed_text, detected_lang, detected_lang

    except Exception as e:
        print(f"✗ Transcription error: {e}")
        return None, None, None

def translate_to_english(audio_path):
    """Translate audio to English using Whisper"""
    try:
        print("Loading Whisper model for translation...")
        model = whisper.load_model(Config.WHISPER_MODEL)

        print("Translating to English...")
        result = model.transcribe(str(audio_path), task="translate")
        english_text = result['text']

        print(f"✓ English translation: {english_text[:100]}...")
        return english_text

    except Exception as e:
        print(f"✗ Translation error: {e}")
        return None

# =========================
# DOCTOR VOICE INPUT
# =========================
def record_doctor_advice():
    """Record doctor's voice advice and convert to text"""
    recognizer = sr.Recognizer()
    full_advice = []

    print("\n=== DOCTOR ADVICE RECORDING ===")
    print("Say 'stop recording' to finish\n")

    while True:
        try:
            with sr.Microphone() as source:
                print("🎤 Listening... (speak now)")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = recognizer.listen(source, timeout=10, phrase_time_limit=15)

                print("🔄 Recognizing...")
                text = recognizer.recognize_google(audio_data, language='en-US')

                if "stop recording" in text.lower():
                    print("✓ Recording stopped")
                    break

                full_advice.append(text)
                print(f"✓ Captured: {text}\n")

        except sr.WaitTimeoutError:
            print("⏱ Timeout - say something or 'stop recording' to finish")
            continue
        except sr.UnknownValueError:
            print("⚠ Could not understand - please repeat")
            continue
        except Exception as e:
            print(f"✗ Error: {e}")
            break

    final_advice = " ".join(full_advice)
    return final_advice

# =========================
# HUGGING FACE API CALLS
# =========================
def call_huggingface_api(model_id, payload):
    """Generic HuggingFace API caller - UPDATED for 2026"""
    headers = {
        "Authorization": f"Bearer {Config.HF_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Use the NEW router endpoint (api-inference is deprecated)
    api_url = f"https://api-inference.huggingface.co/models/{model_id}"
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        # Check if we need to use the router endpoint instead
        if response.status_code == 410:
            print("⚠ Switching to router endpoint...")
            api_url = f"https://router.huggingface.co/models/{model_id}"
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 503:
            # Model is loading, wait and retry
            print("⏳ Model is loading, waiting 20 seconds...")
            import time
            time.sleep(20)
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                return response.json()
        
        print(f"✗ API Error ({response.status_code}): {response.text[:200]}")
        return None
        
    except Exception as e:
        print(f"✗ API Exception: {e}")
        return None

# =========================
# PATIENT INFO EXTRACTION
# =========================
def extract_patient_info_from_transcript(transcription_text):
    """Extract patient name and age from transcription"""
    print("🔍 Extracting patient information from transcript...")

    # Pattern matching for name and age
    name_match = re.search(r"(?:I'm|I am|my name is|this is)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)", transcription_text, re.IGNORECASE)
    age_match = re.search(r"(\d{1,3})\s+(?:years?\s+old|year|yr)", transcription_text, re.IGNORECASE)

    patient_info = {
        "name": name_match.group(1) if name_match else "N/A",
        "age": age_match.group(1) if age_match else "N/A"
    }

    # If pattern matching fails, try AI extraction
    if patient_info["name"] == "N/A" or patient_info["age"] == "N/A":
        try:
            prompt = f"""Extract patient information from this transcript. 
Transcript: {transcription_text[:500]}

Return ONLY valid JSON format:
{{"name": "patient_name", "age": "age_in_years"}}

If not found, use "N/A"."""

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.3,
                    "return_full_text": False
                }
            }

            result = call_huggingface_api(Config.MEDITRON_MODEL, payload)

            if result:
                response_text = result[0]['generated_text'].strip()
                json_match = re.search(r'\{[^}]+\}', response_text)
                if json_match:
                    ai_info = json.loads(json_match.group())
                    if patient_info["name"] == "N/A":
                        patient_info["name"] = ai_info.get("name", "N/A")
                    if patient_info["age"] == "N/A":
                        patient_info["age"] = ai_info.get("age", "N/A")
        except Exception as e:
            print(f"⚠ AI extraction failed: {e}")

    print(f"✓ Extracted - Name: {patient_info.get('name')}, Age: {patient_info.get('age')}")
    return patient_info

# =========================
# DOCTOR ADVICE PARSING
# =========================
def parse_doctor_advice_structured(doctor_advice, patient_symptoms):
    """Parse doctor's advice into structured prescription format with comprehensive medicine extraction"""
    print("🤖 Parsing doctor's advice with AI...")
    
    # Try AI first
    prompt = f"""[INST] You are a medical prescription parser. Extract ALL medicines from doctor's advice.

Patient Symptoms: {patient_symptoms[:300]}

Doctor's Advice: {doctor_advice}

Extract and return ONLY valid JSON:
{{
  "complaint": "brief patient complaint",
  "observations": "clinical symptoms: pain type, triggers, etc",
  "investigations": ["test1", "test2"] or ["N/A"],
  "diagnosis": "condition name",
  "medicines": [
    {{"medicine": "Tab Name Xmg", "dosage": "1-0-0", "duration": "X days", "measure": "", "instructions": "timing"}}
  ],
  "remarks": "advice"
}}

Extract ALL medicines including tablets, syrups, capsules. [/INST]"""

    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 800, "temperature": 0.3, "top_p": 0.9, "return_full_text": False}
    }
    
    result = call_huggingface_api(Config.MEDITRON_MODEL, payload)
    
    if result:
        try:
            if isinstance(result, list) and len(result) > 0:
                response_text = result[0].get('generated_text', '')
            else:
                response_text = result.get('generated_text', '') if isinstance(result, dict) else str(result)
            
            print(f"📝 LLM Response: {response_text[:120]}...")
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                parsed_data = json.loads(json_match.group())
                print(f"✓ AI extracted {len(parsed_data.get('medicines', []))} medicine(s)")
                return parsed_data
        except:
            pass
    
    print("⚠ Using enhanced fallback parser...")
    
    # COMPREHENSIVE MEDICINE EXTRACTION
    medicines = []
    seen_medicines = set()  # Avoid duplicates
    
    # Preprocess: Split by common separators
    advice_lower = doctor_advice.lower()
    
    # Pattern 1: Standard tablet format with mg
    # "Pantoprazole 40 mg, one tablet once daily before breakfast for 7 days"
    pattern1 = re.finditer(
        r'([A-Z][a-zA-Z]{3,}(?:zole|tac|cin|dene|mol|fen|ine|ate)?)\s+(\d+\s*mg).*?'
        r'(?:one\s+tablet|tablet|take).*?'
        r'(once|twice|three\s+times).*?'
        r'(daily|day|a\s+day).*?'
        r'(?:for\s+)?(\d+\s+(?:to\s+\d+\s+)?days?)',
        doctor_advice,
        re.IGNORECASE
    )
    
    for match in pattern1:
        med_name = match.group(1)
        dosage_mg = match.group(2)
        frequency = match.group(3)
        duration = match.group(5)
        
        # Get the full sentence for timing context
        start_pos = max(0, match.start() - 50)
        end_pos = min(len(doctor_advice), match.end() + 50)
        context = doctor_advice[start_pos:end_pos].lower()
        
        # Determine dosage pattern
        if 'three' in frequency.lower():
            freq_pattern = '1-1-1'
        elif 'twice' in frequency.lower():
            freq_pattern = '1-0-1'
        else:
            freq_pattern = '1-0-0'
        
        # Determine timing
        timing = "As directed"
        if 'before breakfast' in context or 'in the morning' in context:
            timing = "Before breakfast"
        elif 'after breakfast' in context:
            timing = "After breakfast"
        elif 'at night' in context or 'after dinner' in context or 'night' in context:
            timing = "After dinner"
        elif 'after meals' in context:
            timing = "After meals"
        elif 'before meals' in context:
            timing = "Before meals"
        
        med_key = f"{med_name}_{dosage_mg}"
        if med_key not in seen_medicines:
            medicines.append({
                "medicine": f"Tab {med_name} {dosage_mg}",
                "dosage": freq_pattern,
                "duration": duration,
                "measure": "",
                "instructions": timing
            })
            seen_medicines.add(med_key)
    
    # Pattern 2: Catch medicines without full detail (backup)
    # "You should also take Rantac 150 mg, one tablet at night after dinner for 5 days"
    pattern2 = re.finditer(
        r'(?:take|prescribing)\s+([A-Z][a-zA-Z]{3,})\s+(\d+\s*mg).*?'
        r'(?:for\s+)?(\d+\s+(?:to\s+\d+\s+)?days?)',
        doctor_advice,
        re.IGNORECASE
    )
    
    for match in pattern2:
        med_name = match.group(1)
        dosage_mg = match.group(2)
        duration = match.group(3)
        
        med_key = f"{med_name}_{dosage_mg}"
        if med_key not in seen_medicines:
            # Get context for timing
            start_pos = max(0, match.start() - 30)
            end_pos = min(len(doctor_advice), match.end() + 60)
            context = doctor_advice[start_pos:end_pos].lower()
            
            # Determine frequency from context
            freq_pattern = '1-0-0'
            if 'twice' in context:
                freq_pattern = '1-0-1'
            elif 'three times' in context:
                freq_pattern = '1-1-1'
            
            # Determine timing
            timing = "As directed"
            if 'at night' in context or 'after dinner' in context:
                timing = "After dinner"
            elif 'before breakfast' in context or 'morning' in context:
                timing = "Before breakfast"
            elif 'after meals' in context:
                timing = "After meals"
            
            medicines.append({
                "medicine": f"Tab {med_name} {dosage_mg}",
                "dosage": freq_pattern,
                "duration": duration,
                "measure": "",
                "instructions": timing
            })
            seen_medicines.add(med_key)
    
    # Pattern 3: Liquid medicines (syrup, suspension)
    # "Gelusil or Digene syrup, two teaspoons after meals, twice daily for 3 to 5 days"
    pattern3 = re.finditer(
        r'([A-Z][a-zA-Z]{3,})(?:\s+or\s+[A-Z][a-zA-Z]+)?\s+(syrup|suspension|liquid).*?'
        r'(one|two|three)?\s*(teaspoon|tablespoon|ml)?.*?'
        r'(?:for\s+)?(\d+\s+(?:to\s+\d+\s+)?days?)',
        doctor_advice,
        re.IGNORECASE
    )
    
    for match in pattern3:
        med_name = match.group(1)
        med_type = match.group(2)
        quantity = match.group(3) if match.group(3) else "two"
        unit = match.group(4) if match.group(4) else "teaspoons"
        duration = match.group(5)
        
        # Get context for frequency
        start_pos = max(0, match.start() - 20)
        end_pos = min(len(doctor_advice), match.end() + 40)
        context = doctor_advice[start_pos:end_pos].lower()
        
        freq_pattern = '1-0-1'  # Default for syrups
        if 'three times' in context:
            freq_pattern = '1-1-1'
        elif 'twice' in context:
            freq_pattern = '1-0-1'
        elif 'once' in context:
            freq_pattern = '1-0-0'
        
        timing = "After meals"
        if 'before meals' in context:
            timing = "Before meals"
        
        med_key = f"{med_name}_{med_type}"
        if med_key not in seen_medicines:
            medicines.append({
                "medicine": f"{med_type.capitalize()} {med_name}",
                "dosage": freq_pattern,
                "duration": duration,
                "measure": f"{quantity.capitalize()} {unit}",
                "instructions": timing
            })
            seen_medicines.add(med_key)
    
    # Extract clinical observations
    observations = "N/A"
    symptom_keywords = {
        'burning': 'Burning sensation',
        'cramping': 'Cramping pain',
        'bloated': 'Bloating',
        'acidity': 'Acidity',
        'worse after eating': 'Pain worsens after eating',
        'reduced appetite': 'Reduced appetite',
        'nausea': 'Nausea',
        'vomiting': 'Vomiting'
    }
    
    found_symptoms = []
    patient_lower = patient_symptoms.lower()
    for keyword, description in symptom_keywords.items():
        if keyword in patient_lower:
            found_symptoms.append(description)
    
    if found_symptoms:
        observations = ', '.join(found_symptoms[:4])
    
    # Extract diagnosis
    diagnosis = "N/A"
    if 'gastritis' in advice_lower or 'stomach irritation' in advice_lower:
        diagnosis = 'Gastritis'
    elif 'acid reflux' in advice_lower or 'gerd' in advice_lower:
        diagnosis = 'Acid Reflux / GERD'
    elif 'fever' in advice_lower:
        diagnosis = 'Fever'
    
    # Extract investigations
    investigations = []
    if re.search(r'blood\s+(work|test)', advice_lower):
        investigations.append("Blood Test")
    if 'ultrasound' in advice_lower:
        investigations.append("Ultrasound")
    if 'x-ray' in advice_lower or 'xray' in advice_lower:
        investigations.append("X-Ray")
    
    if not investigations:
        investigations = ["N/A"]
    
    # Extract remarks
    sentences = [s.strip() for s in doctor_advice.split('.') if s.strip()]
    advice_keywords = ['avoid', 'drink', 'eat', 'do not', "don't", 'if']
    remarks_sentences = [s for s in sentences if any(kw in s.lower() for kw in advice_keywords)]
    remarks = '. '.join(remarks_sentences[:4]) + '.' if remarks_sentences else "Follow general health precautions"
    
    print(f"✓ Extracted {len(medicines)} medicine(s): {[m['medicine'] for m in medicines]}")
    
    return {
        "complaint": patient_symptoms[:150] if patient_symptoms else "N/A",
        "observations": observations,
        "investigations": investigations,
        "diagnosis": diagnosis,
        "medicines": medicines,
        "remarks": remarks
    }

# =========================
# QUEST CARE PRESCRIPTION GENERATOR
# =========================
def generate_questcare_prescription_html(patient_info, parsed_advice, patient_data):
    """Generate Quest Care style prescription HTML - xhtml2pdf compatible"""
    current_date = datetime.now().strftime('%d-%m-%Y')
    follow_up_date = (datetime.now() + timedelta(days=3)).strftime('%A %B %d, %Y %I:%M %p')
    
    gender = "N/A"
    
    # Build medicines table rows - MUST be simple for xhtml2pdf
    medicine_rows = ""
    if parsed_advice.get('medicines') and len(parsed_advice['medicines']) > 0:
        for med in parsed_advice['medicines']:
            med_name = med.get('medicine', 'N/A')
            dosage = med.get('dosage', 'N/A')
            duration = med.get('duration', 'N/A')
            measure = med.get('measure', '')
            instructions = med.get('instructions', 'N/A')
            
            medicine_rows += f"""
            <tr>
                <td>{med_name}</td>
                <td>{dosage}</td>
                <td>{duration}</td>
                <td>{measure if measure else '-'}</td>
                <td>{instructions}</td>
            </tr>
            """
    else:
        medicine_rows = '<tr><td colspan="5" align="center">No medications prescribed</td></tr>'
    
    # Build investigations list as simple text
    investigations_text = ""
    if parsed_advice.get('investigations') and parsed_advice['investigations'][0] != "N/A":
        for inv in parsed_advice['investigations']:
            investigations_text += f"• {inv}<br/>"
    else:
        investigations_text = "• No investigations required"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial;
                margin: 15px;
                font-size: 11pt;
            }}
            .header {{
                border-bottom: 3px solid #c41e3a;
                padding-bottom: 10px;
                margin-bottom: 15px;
            }}
            .clinic-name {{
                font-size: 22pt;
                font-weight: bold;
                color: #2c3e50;
            }}
            .clinic-address {{
                font-size: 10pt;
                color: #555;
                margin-top: 5px;
            }}
            .info-box {{
                background-color: #f0f0f0;
                padding: 10px;
                margin: 15px 0;
                border: 1px solid #ddd;
            }}
            .section {{
                margin: 12px 0;
            }}
            .section-title {{
                font-weight: bold;
                font-size: 11pt;
                color: #2c3e50;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 10px 0;
            }}
            th {{
                background-color: #c41e3a;
                color: white;
                padding: 8px;
                text-align: left;
                font-size: 10pt;
            }}
            td {{
                border: 1px solid #ccc;
                padding: 6px;
                font-size: 9pt;
            }}
        </style>
    </head>
    <body>
        <!-- Header -->
        <div class="header">
            <div class="clinic-name">Quest Care Medical Clinic</div>
            <div class="clinic-address">
                Anand Society, Dindayal Road, Ghatkopar<br/>
                Mumbai, 368585 · Ph: 08097700800
            </div>
        </div>
        
        <!-- Patient Info -->
        <div class="info-box">
            <b>Patient: {patient_info.get('name', 'N/A')}</b><br/>
            Gender: {gender} | Age: {patient_info.get('age', 'N/A')} years | Date: {current_date}<br/>
            Patient ID: {patient_data.get('patient_id', 'N/A')}
        </div>
        
        <!-- Doctor Info -->
        <div class="info-box">
            <b>Dr. David</b> | M.D.S. | Registration No.: A-77363
        </div>
        
        <!-- Complaint -->
        <div class="section">
            <div class="section-title">Complaint:</div>
            <div>{parsed_advice.get('complaint', 'N/A')}</div>
        </div>
        
        <!-- Observations -->
        <div class="section">
            <div class="section-title">Observations:</div>
            <div>{parsed_advice.get('observations', 'N/A')}</div>
        </div>
        
        <!-- Investigations -->
        <div class="section">
            <div class="section-title">Investigations Suggested:</div>
            <div>{investigations_text}</div>
        </div>
        
        <!-- Diagnosis -->
        <div class="section">
            <div class="section-title">Diagnosis:</div>
            <div>{parsed_advice.get('diagnosis', 'N/A')}</div>
        </div>
        
        <!-- Medications Table -->
        <div class="section">
            <div class="section-title">Rx - Medications:</div>
            <table>
                <tr>
                    <th width="28%">Medicine</th>
                    <th width="12%">Dosage</th>
                    <th width="12%">Duration</th>
                    <th width="10%">Measure</th>
                    <th width="38%">Instructions</th>
                </tr>
                {medicine_rows}
            </table>
        </div>
        
        <!-- Remarks -->
        <div class="section">
            <div class="section-title">Remarks:</div>
            <div>{parsed_advice.get('remarks', 'N/A')}</div>
        </div>
        
        <!-- Follow-up -->
        <div class="section">
            <div class="section-title">Next follow-up date:</div>
            <div>{follow_up_date}</div>
        </div>
        
        <!-- Signature -->
        <div style="text-align: right; margin-top: 30px;">
            <b>Authorised Signature</b>
        </div>
        
        <!-- Footer -->
        <div style="text-align: center; font-size: 9pt; color: #777; margin-top: 20px;">
            <i>This is a computer generated document</i>
        </div>
    </body>
    </html>
    """
    
    return html_content

# =========================
# TRANSLATION & TTS
# =========================
def translate_english_to_indic(text, target_language):
    """Translate English text to target Indic language"""
    print(f"Translating to {target_language}...")

    payload = {
        "inputs": text,
        "parameters": {
            "src_lang": "eng_Latn",
            "tgt_lang": map_whisper_to_indictrans(target_language)
        }
    }

    result = call_huggingface_api(Config.TRANSLATION_MODEL, payload)

    if result and isinstance(result, list) and len(result) > 0:
        translated = result[0].get('translation_text', text)
        print(f"✓ Translation: {translated[:100]}...")
        return translated

    print("⚠ Translation failed, using original text")
    return text

def text_to_speech(text, language_code):
    """Convert text to speech"""
    print(f"Generating speech for language: {language_code}...")

    tts_model = map_whisper_to_tts(language_code)

    payload = {"inputs": text}
    result = call_huggingface_api(tts_model, payload)

    if result:
        print("✓ Speech generated")
        return result

    print("⚠ TTS failed")
    return None

# =========================
# PATIENT RECORD MANAGEMENT
# =========================
def create_patient_record():
    """Create unique patient directory"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    patient_id = f"patient_{timestamp}"
    patient_dir = Config.BASE_DIR / patient_id
    patient_dir.mkdir(exist_ok=True)

    return patient_dir, patient_id

def save_patient_metadata(patient_dir, metadata):
    """Save patient metadata as JSON"""
    metadata_path = patient_dir / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"✓ Metadata saved: {metadata_path}")

# =========================
# LANGUAGE MAPPING
# =========================
def map_whisper_to_indictrans(whisper_lang):
    """Map Whisper language codes to IndicTrans2 codes"""
    mapping = {
        "hi": "hin_Deva",
        "bn": "ben_Beng",
        "ta": "tam_Taml",
        "te": "tel_Telu",
        "mr": "mar_Deva",
        "gu": "guj_Gujr",
        "kn": "kan_Knda",
        "ml": "mal_Mlym",
        "pa": "pan_Guru",
        "or": "ory_Orya",
    }
    return mapping.get(whisper_lang, "hin_Deva")

def map_whisper_to_tts(whisper_lang):
    """Map Whisper language codes to TTS model IDs"""
    mapping = {
        "hi": "facebook/mms-tts-hin",
        "bn": "facebook/mms-tts-ben",
        "ta": "facebook/mms-tts-tam",
        "te": "facebook/mms-tts-tel",
        "mr": "facebook/mms-tts-mar",
        "gu": "facebook/mms-tts-guj",
        "kn": "facebook/mms-tts-kan",
        "ml": "facebook/mms-tts-mal",
    }
    return mapping.get(whisper_lang, "facebook/mms-tts-hin")

# =========================
# MAIN WORKFLOW - UPDATED FOR AUDIO INPUT
# =========================
def main():
    """Main consultation workflow - Now accepts audio files directly"""
    print("\n" + "="*60)
    print("🏥 MULTILINGUAL MEDICAL CONSULTATION SYSTEM")
    print("="*60 + "\n")

    # Setup
    Config.setup_directories()

    if not Config.validate_api_key():
        return

    # Get audio file
    print("\n🎵 AUDIO INPUT")
    audio_path = input("Enter patient audio file path (MP3) or press Enter for audio/patient_audio.mp3: ").strip()

    if not audio_path:
        audio_path = Config.AUDIO_DIR / "patient_audio.mp3"
    else:
        audio_path = Path(audio_path)

    if not audio_path.exists():
        print(f"✗ Audio file not found: {audio_path}")
        return

    print(f"✓ Audio file loaded: {audio_path}")

    # Create patient record
    patient_dir, patient_id = create_patient_record()
    print(f"\n✓ Patient record created: {patient_id}")

    # Copy audio to patient directory
    patient_audio = patient_dir / "patient_audio.mp3"
    import shutil
    shutil.copy(audio_path, patient_audio)
    print(f"✓ Audio copied to: {patient_audio}")

    # Transcribe and detect language
    print("\n🗣️ TRANSCRIBING PATIENT SYMPTOMS...")
    original_symptoms, detected_lang, lang_code = transcribe_and_detect_language(patient_audio)

    if not original_symptoms:
        print("✗ Transcription failed")
        return

    # Translate to English
    print("\n🌐 TRANSLATING TO ENGLISH...")
    english_symptoms = translate_to_english(patient_audio)

    if not english_symptoms:
        english_symptoms = original_symptoms

    # Extract patient info from transcript
    print("\n👤 EXTRACTING PATIENT INFORMATION...")
    patient_info = extract_patient_info_from_transcript(original_symptoms)

    # Record doctor's advice
    print("\n🩺 DOCTOR'S ADVICE")
    print("Choose input method:")
    print("1. Voice recording")
    print("2. Text input")
    choice = input("Enter choice (1/2): ").strip()

    if choice == "1":
        doctor_advice_english = record_doctor_advice()
    else:
        print("\nEnter doctor's advice (press Enter twice when done):")
        lines = []
        while True:
            line = input()
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        doctor_advice_english = "\n".join(lines).strip()

    if not doctor_advice_english:
        print("✗ No doctor advice provided")
        return

    # Parse doctor's advice
    print("\n📋 PARSING MEDICAL INFORMATION...")
    parsed_advice = parse_doctor_advice_structured(doctor_advice_english, english_symptoms)

    # Generate Quest Care prescription
    print("\n📄 GENERATING QUEST CARE PRESCRIPTION...")
    patient_data = {
        "patient_id": patient_id,
        "language": detected_lang
    }

    html_content = generate_questcare_prescription_html(patient_info, parsed_advice, patient_data)

    # Save HTML
    prescription_html_path = patient_dir / "prescription.html"
    with open(prescription_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Convert to PDF
    prescription_pdf_path = patient_dir / "prescription.pdf"
    with open(prescription_pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(html_content, dest=pdf_file)

    if not pisa_status.err:
        print(f"✓ Quest Care prescription generated: {prescription_pdf_path}")
    else:
        print("⚠ PDF generation had issues, but HTML saved")

    # Translate doctor's advice back to patient's language
    print(f"\n🌐 TRANSLATING ADVICE TO {detected_lang.upper()}...")
    doctor_advice_translated = translate_english_to_indic(doctor_advice_english, detected_lang)

    # Generate TTS
    print("\n🔊 GENERATING AUDIO RESPONSE...")
    audio_response = text_to_speech(doctor_advice_translated, detected_lang)

    if audio_response:
        audio_output_path = patient_dir / "doctor_advice_audio.mp3"
        with open(audio_output_path, "wb") as f:
            f.write(audio_response)
        print(f"✓ Audio saved: {audio_output_path}")

    # Save metadata
    metadata = {
        "patient_id": patient_id,
        "timestamp": datetime.now().isoformat(),
        "detected_language": detected_lang,
        "patient_info": patient_info,
        "original_symptoms": original_symptoms,
        "english_symptoms": english_symptoms,
        "doctor_advice_english": doctor_advice_english,
        "doctor_advice_translated": doctor_advice_translated,
        "parsed_prescription": parsed_advice
    }

    save_patient_metadata(patient_dir, metadata)

    # Save translated advice
    translated_advice_path = patient_dir / "doctor_advice_translated.txt"
    with open(translated_advice_path, "w", encoding="utf-8") as f:
        f.write(doctor_advice_translated)

    print("\n" + "="*60)
    print("✅ CONSULTATION COMPLETE!")
    print("="*60)
    print(f"\n📁 All files saved in: {patient_dir}")
    print(f"   - Patient audio: patient_audio.mp3")
    print(f"   - Doctor advice audio: doctor_advice_audio.mp3")
    print(f"   - Prescription PDF: prescription.pdf")
    print(f"   - Prescription HTML: prescription.html")
    print(f"   - Metadata: metadata.json")
    print(f"   - Translated advice: doctor_advice_translated.txt")

if __name__ == "__main__":
    main()

# voice/stt.py — replace entire file with this
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import tempfile
from faster_whisper import WhisperModel
from config import settings

_model = None

def _get_model():
    global _model
    if _model is None:
        print(f"🎙️  Loading Whisper '{settings.WHISPER_MODEL}' model...")
        # device="cpu", compute_type="int8" → fastest on CPU, lowest RAM
        _model = WhisperModel(
            settings.WHISPER_MODEL,
            device="cpu",
            compute_type="int8"
        )
        print("🎙️  Whisper ready.")
    return _model

def transcribe(audio_bytes: bytes, language: str = "en") -> str:
    if not audio_bytes:
        return ""

    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        model = _get_model()
        # faster-whisper returns a generator of segments
        segments, _ = model.transcribe(
            tmp_path,
            language=language,
            beam_size=1,      # beam_size=1 → fastest on CPU
        )
        return " ".join(seg.text for seg in segments).strip()
    except Exception as e:
        print(f"[STT Error] {e}")
        return ""
    finally:
        os.unlink(tmp_path)

"""
Text-to-Speech using pyttsx3 — 100% local, no internet, uses OS voice engine.
  Windows : SAPI5
  Linux   : espeak-ng  (install: sudo apt install espeak-ng)
  macOS   : NSSpeechSynthesizer

Output: WAV bytes → played in Streamlit via st.audio()
"""
import pyttsx3
import tempfile
import os
import io


_engine = None


def _get_engine():
    global _engine
    if _engine is None:
        _engine = pyttsx3.init()
        _engine.setProperty("rate",   160)   # words per minute (default ~200)
        _engine.setProperty("volume", 0.9)   # 0.0 – 1.0
        # Pick a female voice if available
        voices = _engine.getProperty("voices")
        for v in voices:
            if "female" in v.name.lower() or "zira" in v.name.lower():
                _engine.setProperty("voice", v.id)
                break
    return _engine


def speak(text: str) -> bytes:
    """
    Convert text → WAV audio bytes.
    Returns bytes that can be passed directly to st.audio(bytes, format='audio/wav').
    Returns empty bytes on failure.
    """
    if not text:
        return b""

    engine = _get_engine()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as f:
            return f.read()
    except Exception as e:
        print(f"[TTS Error] {e}")
        return b""
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

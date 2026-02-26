"""
Streamlit UI — entry point that users interact with.
Supports both:
  1. 🎙️  Voice input  (mic button → Whisper STT → agent → pyttsx3 TTS)
  2. 💬  Text input   (type directly → agent → displayed as text)

Communicates with the Books Agent via the AdvisorRouter (A2A protocol).
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from audio_recorder_streamlit import audio_recorder
from orchestrator.network import build_network
from orchestrator.router  import AdvisorRouter
from voice.stt import transcribe
from voice.tts import speak

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title = "📚 Paige — Your Book Advisor",
    page_icon  = "📚",
    layout     = "wide",
)

# ── Cached resources (initialised once per session) ──────────────────────────
@st.cache_resource(show_spinner="🔌 Connecting to Book Advisor Agent...")
def get_router():
    network = build_network()
    return AdvisorRouter(network)


# ── Session state defaults ────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []   # [{role: user|assistant, content: str}]
if "last_audio" not in st.session_state:
    st.session_state.last_audio = None


# ── Helpers ───────────────────────────────────────────────────────────────────
def handle_query(user_text: str):
    """Send query to router, get response, update chat history + play TTS."""
    if not user_text.strip():
        return

    # Append user message
    st.session_state.messages.append({"role": "user", "content": user_text})

    # Route to Books Agent via A2A
    with st.spinner("📖 Paige is thinking..."):
        try:
            router   = get_router()
            response = router.route(user_text)
        except Exception as e:
            response = f"⚠️ Agent error: {e}"

    # Append assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

    # TTS — generate audio bytes and store in session_state
    audio_bytes = speak(response)
    if audio_bytes:
        st.session_state.last_audio = audio_bytes


# ── UI Layout ─────────────────────────────────────────────────────────────────
st.title("📚 Paige — Your Personal Book Advisor")
st.caption("Powered by Mistral · ChromaDB · OpenLibrary · A2A Protocol")
st.divider()

col_chat, col_side = st.columns([3, 1])

with col_side:
    st.subheader("🎙️ Voice Input")
    st.caption("Click the mic, speak, click again to stop.")
    audio_bytes = audio_recorder(
        text           = "",
        recording_color= "#e8b4b8",
        neutral_color  = "#6aa3d5",
        icon_size      = "2x",
    )

    # Only process if NEW audio arrived (avoid re-processing on page re-runs)
    if audio_bytes and audio_bytes != st.session_state.last_audio:
        with st.spinner("🎙️ Transcribing..."):
            transcribed = transcribe(audio_bytes)
        if transcribed:
            st.success(f"You said: *{transcribed}*")
            handle_query(transcribed)
            st.rerun()
        else:
            st.warning("Could not transcribe audio. Please try again.")

    st.divider()
    st.subheader("📋 Quick Lists")
    list_choice = st.selectbox(
        "View list:",
        ["—", "liked", "disliked", "wishlist", "not_interested"],
    )
    if list_choice != "—":
        handle_query(f"Show me my {list_choice} list")
        st.rerun()

with col_chat:
    # ── Chat history ─────────────────────────────────────────────────────────
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "📚"):
                st.markdown(msg["content"])

    # ── Play latest TTS audio ─────────────────────────────────────────────────
    if st.session_state.last_audio:
        st.audio(st.session_state.last_audio, format="audio/wav")

    # ── Text input ────────────────────────────────────────────────────────────
    user_input = st.chat_input("Ask Paige anything about books...")
    if user_input:
        handle_query(user_input)
        st.rerun()

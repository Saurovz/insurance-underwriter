# File: streamlit_app/_chatbot_widget.py

import streamlit as st
from typing import List, Dict
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from insurance_underwriter.core.chatbot_service import get_chatbot_service


def initialize_chatbot_session_state():
    """Initialize session state variables for chatbot."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'chatbot_service' not in st.session_state:
        try:
            st.session_state.chatbot_service = get_chatbot_service()
        except Exception as e:
            st.session_state.chatbot_service = None
            st.session_state.chatbot_error = str(e)
    
    if 'chatbot_dialog_open' not in st.session_state:
        st.session_state.chatbot_dialog_open = False
    
    # Counter to force input field recreation
    if 'input_counter' not in st.session_state:
        st.session_state.input_counter = 0
    
    # Track if currently processing
    if 'is_processing' not in st.session_state:
        st.session_state.is_processing = False


@st.dialog("🏥 Policy Assistant", width="large")
def chatbot_dialog():
    """Render chatbot in a modal dialog."""
    
    if st.session_state.chatbot_service is None:
        st.error("❌ Chatbot service unavailable. Please ensure the policy knowledge base is set up.")
        if hasattr(st.session_state, 'chatbot_error'):
            st.error(f"Error: {st.session_state.chatbot_error}")
        
        if st.button("Close", key="close_error_dialog"):
            st.session_state.chatbot_dialog_open = False
            st.rerun()
        return
    
    st.caption("Ask me about policy rules and risk factors")
    st.markdown("---")
    
    # Display chat history
    if len(st.session_state.chat_history) == 0:
        st.info("""👋 **Hello!**

I can help you understand policy rules, risk factors, and premium calculations.

**Try asking:**
- What is the risk score for a moderate smoker?
- How is BMI considered in risk evaluation?
- What are the age-based premium rates?""")
    else:
        for turn in st.session_state.chat_history:
            with st.chat_message("user"):
                st.write(turn['user'])
            
            with st.chat_message("assistant", avatar="🏥"):
                st.write(turn['assistant'])
    
    # Show processing indicator if processing
    # Replace the spinner section with this for more detailed feedback
    if st.session_state.is_processing:
        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner(""):
                st.markdown("""
                🔍 **Analyzing your question...**
                
                ⏳ Searching policy database...
                
                🤖 Generating response...
                """)

    
    st.markdown("---")
    
    # Input area
    user_input = st.text_input(
        "Your question:",
        placeholder="E.g., What is the loading factor for smokers?",
        key=f"chat_input_dialog_{st.session_state.input_counter}",
        disabled=st.session_state.is_processing  # Disable input while processing
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        send_button = st.button(
            "Send 📤" if not st.session_state.is_processing else "Processing ⏳",
            key="send_msg_dialog",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.is_processing  # Disable button while processing
        )
        
        if send_button and user_input.strip():
            # Set processing flag
            st.session_state.is_processing = True
            st.rerun()
    
    with col2:
        if st.button("Clear 🗑️", key="clear_chat_dialog", use_container_width=True,
                    disabled=st.session_state.is_processing):
            st.session_state.chat_history = []
            st.session_state.input_counter += 1
            st.session_state.chatbot_dialog_open = True
            st.rerun()
    
    with col3:
        if st.button("Close ✖", key="close_chat_dialog", use_container_width=True,
                    disabled=st.session_state.is_processing):
            st.session_state.chatbot_dialog_open = False
            st.session_state.input_counter += 1
            st.rerun()
    
    # Process message if flag is set (after rerun)
    if st.session_state.is_processing:
        # Get the user input from the previous state
        # We need to retrieve it from session state before increment
        input_key = f"chat_input_dialog_{st.session_state.input_counter}"
        if input_key in st.session_state and st.session_state[input_key].strip():
            user_query = st.session_state[input_key]
            
            # Process the message
            handle_user_message(user_query)
            
            # Clear input and reset processing flag
            st.session_state.input_counter += 1
            st.session_state.is_processing = False
            st.session_state.chatbot_dialog_open = True
            st.rerun()


def render_floating_chatbot():
    """Render floating chatbot button that opens a dialog."""
    initialize_chatbot_session_state()
    
    st.markdown("""
    <style>
    div[data-testid="column"]:has(button[kind="secondary"].chat-float-btn) {
        position: fixed;
        bottom: 30px;
        right: 30px;
        z-index: 9999;
        width: auto;
    }
    
    button[kind="secondary"].chat-float-btn {
        width: 70px !important;
        height: 70px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: 3px solid rgba(255, 255, 255, 0.3) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
        font-size: 36px !important;
        padding: 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    button[kind="secondary"].chat-float-btn:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.7) !important;
    }
    
    @keyframes pulse {
        0%, 100% {
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }
        50% {
            box-shadow: 0 6px 30px rgba(102, 126, 234, 0.8);
        }
    }
    
    button[kind="secondary"].chat-float-btn {
        animation: pulse 2s infinite;
    }
    </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns([10, 1])
    
    with cols[1]:
        if st.button("💬", key="open_chatbot", help="AI Policy Assistant", 
                    type="secondary", use_container_width=False):
            st.session_state.chatbot_dialog_open = True
            st.rerun()
    
    if st.session_state.chatbot_dialog_open:
        chatbot_dialog()


def handle_user_message(user_input: str):
    """Handle user message and generate chatbot response."""
    try:
        chatbot_service = st.session_state.chatbot_service
        
        # Generate response (this is where the time is spent)
        response = chatbot_service.generate_chatbot_response(
            user_query=user_input,
            conversation_history=st.session_state.chat_history
        )
        
        st.session_state.chat_history.append({
            'user': user_input,
            'assistant': response
        })
        
    except Exception as e:
        error_msg = f"Sorry, I encountered an error: {str(e)}"
        st.session_state.chat_history.append({
            'user': user_input,
            'assistant': error_msg
        })

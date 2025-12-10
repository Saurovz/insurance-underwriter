import streamlit as st

def show_sidebar():
    """Adds custom content to the Streamlit sidebar."""
    with st.sidebar:
        st.header("⚙️ App Settings")
        st.info("Custom content placed *above* the auto-generated navigation.")

        # Example: a widget shared across pages
        if 'api_key' not in st.session_state:
            st.session_state.api_key = ''
            
        st.session_state.api_key = st.text_input(
            "Enter API Key", 
            type="password",
            value=st.session_state.api_key,
            help="This API key will be accessible in all pages."
        )

        st.divider()
        st.markdown("---") # Visual separator below the custom content
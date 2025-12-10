# pages/1_app_input.py   The prefix 1_ controls the order in the sidebar.
import streamlit as st
from components.sidebar import show_sidebar

st.set_page_config(
    page_title="Application",
    page_icon="📝",
    layout="wide"
)

# You can call show_sidebar() here too if you want the custom elements, 
# but it's often best to put shared sidebar code in the entry point only 
# to avoid redundancy or unexpected behavior. Let's just focus on the page content.

st.title("📝 Data Application Page")
st.write("Use this page to input or process your data.")

if st.session_state.api_key:
    st.success("API Key is set! Ready to proceed.")
else:
    st.warning("Please set the API Key in the sidebar.")

# Example input for session state sharing
if 'user_input' not in st.session_state:
    st.session_state.user_input = "Default Value"

st.session_state.user_input = st.text_area(
    "Enter text for processing:",
    value=st.session_state.user_input
)

if st.button("Process"):
    st.session_state.processed_text = f"Processed: {st.session_state.user_input.upper()}"
    st.info("Data processed! Navigate to the 'Result' page to see the output.")
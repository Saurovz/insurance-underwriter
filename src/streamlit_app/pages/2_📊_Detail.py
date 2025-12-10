import streamlit as st

st.set_page_config(
    page_title="Result",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Application Result")
st.write("This page displays the result of the processing.")

# Access and display data from the session state
if 'processed_text' in st.session_state:
    st.code(st.session_state.processed_text, language='text')
else:
    st.error("No processed data found. Please run the process on the 'Application' page first.")

st.divider()

st.subheader("Shared Input Example")
st.write(f"The current value of the shared input (from 'Application' page) is: **{st.session_state.get('user_input', 'N/A')}**")
# pages/1_app_input.py   The prefix 1_ controls the order in the sidebar.
import streamlit as st
from components.sidebar import show_sidebar
import os

st.set_page_config(
    page_title="Application",
    page_icon="📝",
    layout="wide"
)

# You can call show_sidebar() here too if you want the custom elements, 
# but it's often best to put shared sidebar code in the entry point only 
# to avoid redundancy or unexpected behavior. Let's just focus on the page content.

st.title("📝 Policy Configuration")
st.write("Prepares the system for underwriting workflows.")



def policy_process(file_path):
            if st.button("Process Policies"):
                # ****TBD: RAG Processing
                st.success("Policy data processed.")
                st.toast('Data has been updated!', icon='🎉')
               

def policy_upload():
    uploaded_files = st.file_uploader("Policy guideline Upload", type=None, accept_multiple_files=True)

    if uploaded_files:
        
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        documents_dir = os.path.join(project_root, "Document")
        if not os.path.exists(documents_dir):
            os.makedirs(documents_dir)

        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.getvalue()
            file_path = os.path.join(documents_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(file_bytes)
        st.markdown(f"<span style='font-size: 0.9em; color: #a31515; font-style: italic;'>Documents uploaded to {documents_dir}</span>", unsafe_allow_html=True)

        policy_process(file_path)
        
policy_upload()


# if st.session_state.api_key:
#     st.success("API Key is set! Ready to proceed.")
# else:
#     st.warning("Please set the API Key in the sidebar.")

# # Example input for session state sharing
# if 'user_input' not in st.session_state:
#     st.session_state.user_input = "Default Value"

# st.session_state.user_input = st.text_area(
#     "Enter text for processing:",
#     value=st.session_state.user_input
# )

# if st.button("Process"):
#     st.session_state.processed_text = f"Processed: {st.session_state.user_input.upper()}"
#     st.info("Data processed! Navigate to the 'Result' page to see the output.")


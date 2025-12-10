# pages/1_app_input.py   The prefix 1_ controls the order in the sidebar.
import streamlit as st
import sqlite3
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

# --- Application Upload Section ---
import uuid
import os
import subprocess
import json

def init_db():
    conn = sqlite3.connect('underwriting.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS application (
            id TEXT PRIMARY KEY,
            filename TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def application_process(file_path):
    if st.button("Submit"):
        # Run ingestApplication.py and capture output
        # result = subprocess.run(
        #     ["python", "ingestApplication.py", file_path],
        #     capture_output=True,
        #     text=True
        # )
        # try:
        #     output_json = json.loads(result.stdout)
        #     names = output_json.get("names")
        #     age = output_json.get("age")
        #     st.write("Names:", names)
        #     st.write("Age:", age)
        # except Exception as e:
        #     st.error(f"Error parsing output: {e}")
        #     st.text(result.stdout)

        # CALL THE EXTRACT_PDF_NODE and Applicationprocess fuction which returns the JSON and save in db
        conn = sqlite3.connect('underwriting.db')
        c = conn.cursor()
        c.execute("INSERT INTO application (id, filename) VALUES (?, ?)",
                  (st.session_state.unique_id, file_path))
        conn.commit()
        conn.close()
        st.success("Application data processed and saved to database.")

def application_upload():
    uploaded_file = st.file_uploader("Application Upload", type=None)

    if uploaded_file:
        # Generate unique ID and store in session state
        if "unique_id" not in st.session_state:
            st.session_state.unique_id = str(uuid.uuid4())

        # Save file in memory (BytesIO)
        file_bytes = uploaded_file.getvalue()

        # Prepare path (Document folder inside project root)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        documents_dir = os.path.join(project_root, "Document")
        save_dir = os.path.join(documents_dir, st.session_state.unique_id)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        file_path = os.path.join(save_dir, uploaded_file.name)

        # Save file physically
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        st.success(f"File uploaded and saved to {file_path}")

        # Show submit button and process
        application_process(file_path)


# Call db
init_db()
# Call the function in the page
application_upload()


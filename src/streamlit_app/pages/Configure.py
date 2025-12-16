# pages/Configure.py
import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from insurance_underwriter.core.policy_knowledge_base import PolicyKnowledgeBase

st.set_page_config(
    page_title="Configuration",
    page_icon="⚙️",
    layout="wide"
)

st.title("📝 Policy Configuration")
st.write("Prepares the system for underwriting workflows.")

def check_collection_exists():
    """Check if policy collection already exists in ChromaDB"""
    try:
        kb = PolicyKnowledgeBase()
        existing_collections = [col.name for col in kb.client.list_collections()]
        return kb.collection_name in existing_collections
    except Exception as e:
        st.error(f"Error checking collection: {str(e)}")
        return False

def process_policy_document(file_path, force_reload=False):
    """Process the policy PDF and create ChromaDB"""
    
    # Create containers for progress updates
    progress_container = st.empty()
    status_container = st.empty()
    progress_bar = st.progress(0)
    
    try:
        with status_container.status("🔄 Initializing Policy Knowledge Base...", expanded=True) as status:
            # Initialize PolicyKnowledgeBase
            st.write("📦 Loading embedding model...")
            kb = PolicyKnowledgeBase(
                db_path="./chroma_db",
                collection_name="policy_rules",
                embedding_model="sentence-transformers/all-MiniLM-L6-v2"
            )
            progress_bar.progress(10)
            
            # Check if collection exists
            existing_collections = [col.name for col in kb.client.list_collections()]
            
            if kb.collection_name in existing_collections:
                if force_reload:
                    st.write(f"🗑️ Deleting existing collection: {kb.collection_name}")
                    kb.client.delete_collection(kb.collection_name)
                    progress_bar.progress(20)
                else:
                    st.warning("✅ Policy knowledge base already exists.")
                    progress_bar.progress(100)
                    status.update(label="✅ Policy already configured", state="complete")
                    return True
            
            # Load PDF
            st.write(f"📄 Loading policy PDF from: {file_path}")
            from langchain_community.document_loaders import PyPDFLoader
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            st.write(f"📖 Loaded {len(documents)} pages from policy PDF")
            progress_bar.progress(30)
            
            # Split into chunks
            st.write("✂️ Splitting document into chunks...")
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = text_splitter.split_documents(documents)
            st.write(f"📑 Created {len(chunks)} chunks from policy document")
            progress_bar.progress(50)
            
            # Prepare data for ChromaDB
            texts = [chunk.page_content for chunk in chunks]
            metadatas = [
                {
                    "page": chunk.metadata.get("page", 0),
                    "source": chunk.metadata.get("source", "policy"),
                    "chunk_id": i
                }
                for i, chunk in enumerate(chunks)
            ]
            ids = [f"policy_chunk_{i}" for i in range(len(chunks))]
            
            # Create collection
            st.write("🔄 Creating ChromaDB collection...")
            collection = kb.client.get_or_create_collection(
                name=kb.collection_name,
                metadata={"description": "Health Insurance Policy Rules and Regulations"}
            )
            progress_bar.progress(60)
            
            # Add documents in batches
            st.write("🧠 Creating embeddings and storing in ChromaDB...")
            batch_size = 100
            total_batches = (len(texts) - 1) // batch_size + 1
            
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i+batch_size]
                batch_metadatas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]
                
                # Generate embeddings
                batch_embeddings = kb.embeddings.embed_documents(batch_texts)
                
                # Add to collection
                collection.add(
                    documents=batch_texts,
                    metadatas=batch_metadatas,
                    ids=batch_ids,
                    embeddings=batch_embeddings
                )
                
                # Update progress
                batch_num = i // batch_size + 1
                progress_percentage = 60 + int((batch_num / total_batches) * 40)
                progress_bar.progress(progress_percentage)
                st.write(f"✅ Processed batch {batch_num}/{total_batches}")
            
            # Complete
            progress_bar.progress(100)
            status.update(label="✅ Policy Knowledge Base Created Successfully!", state="complete")
            
            st.success(f"""
            **Policy Configuration Complete!** 
            - 📍 Database location: `{kb.db_path}`
            - 📊 Total chunks indexed: {len(texts)}
            - 🎯 Collection name: `{kb.collection_name}`
            """)
            # st.balloons()
            
            return True
            
    except Exception as e:
        progress_bar.progress(0)
        st.error(f"❌ **Error processing policy document:** {str(e)}")
        st.exception(e)
        return False

def policy_upload():
    """Handle policy document upload"""
    
    # Check if collection already exists
    collection_exists = check_collection_exists()
    
    if collection_exists:
        st.info("ℹ️ A policy knowledge base already exists in the system.")
        show_overwrite = st.checkbox("Upload new policy document (will overwrite existing)", value=False)
        if not show_overwrite:
            st.stop()
    
    st.markdown("---")
    st.subheader("📤 Upload Policy Document")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Policy Guideline Upload",
        type=["pdf"],
        accept_multiple_files=False,
        help="Upload the Health Insurance Policy Rules & Regulations PDF document"
    )
    
    if uploaded_file is not None:
        # Validate file type
        if not uploaded_file.name.endswith('.pdf'):
            st.error("❌ Please upload a PDF file only!")
            return
        
        # Check file size (limit to 200MB as per your UI)
        file_size_mb = uploaded_file.size / (1024 * 1024)
        if file_size_mb > 200:
            st.error(f"❌ File size ({file_size_mb:.2f}MB) exceeds the 200MB limit!")
            return
        
        st.info(f"📄 File uploaded: **{uploaded_file.name}** ({file_size_mb:.2f}MB)")
        
        # Save file to Document directory
        try:
            documents_dir = project_root / "Document"
            documents_dir.mkdir(exist_ok=True)
            
            file_path = documents_dir / uploaded_file.name
            
            # Write file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.success(f"✅ Document saved to: `{file_path}`")
            
            # Confirmation before processing
            st.markdown("---")
            if collection_exists:
                st.warning("⚠️ This will delete the existing policy knowledge base and create a new one!")
            
            col1, col2 = st.columns([1, 4])
            
            with col1:
                if st.button("🚀 Process Policy", type="primary", use_container_width=True):
                    force_reload = collection_exists
                    success = process_policy_document(str(file_path), force_reload=force_reload)
                    
                    if success:
                        st.session_state['policy_configured'] = True
                        st.toast('🎉 Policy Knowledge Base Updated!', icon='✅')
            
            with col2:
                if st.button("🗑️ Cancel", use_container_width=True):
                    # Remove uploaded file
                    if file_path.exists():
                        file_path.unlink()
                    st.rerun()
                    
        except Exception as e:
            st.error(f"❌ **Error saving file:** {str(e)}")
            st.exception(e)

# Main execution
policy_upload()

# Show current status
st.markdown("---")
st.subheader("📊 System Status")

col1, col2 = st.columns(2)

with col1:
    if check_collection_exists():
        st.success("✅ Policy Knowledge Base: **Configured**")
    else:
        st.warning("⚠️ Policy Knowledge Base: **Not Configured**")

with col2:
    db_path = Path("./chroma_db")
    if db_path.exists():
        st.info(f"📂 Database Path: `{db_path.absolute()}`")
    else:
        st.warning("📂 Database Path: **Not Created**")

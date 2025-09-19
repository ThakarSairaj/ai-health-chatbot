import streamlit as st
import hashlib
import chromadb
from PDF_ProcessingModule import PDFExtraction, TextChunking, TextCleaning
import uuid
from datetime import datetime
import tempfile
import os

# Initialize components
pd = PDFExtraction
tclean = TextCleaning
tchuk = TextChunking

def compute_content_hash(content):
    """Compute a hash for the content (e.g., cleaned text)."""
    hash_md5 = hashlib.md5()
    hash_md5.update(content.encode('utf-8'))
    return hash_md5.hexdigest()

def check_existing_hash(collection, pdf_hash):
    """Check if a document with this hash already exists in the collection."""
    try:
        results = collection.get(where={"pdf_hash": pdf_hash}, limit=1)
        return len(results["documents"]) > 0
    except Exception as e:
        st.error(f"Error checking for existing hash: {e}")
        return False

def generate_unique_ids(collection_name, content_hash, num_chunks):
    """Generate unique IDs that won't collide."""
    base_id = f"{collection_name}_{content_hash[:8]}"
    return [f"{base_id}_chunk_{i}" for i in range(num_chunks)]

def process_and_store_pdf_streamlit(
    uploaded_file,
    chroma_path: str = "./brain_medical_database",
    collection_name: str = "brain_anatomy",
    metadata_template: dict = None
):
    """
    Streamlit version: Extracts text from uploaded PDF, cleans it, chunks it, and stores it in ChromaDB.
    """
    
    # Create containers for different sections
    status_container = st.container()
    progress_container = st.container()
    
    with status_container:
        st.info("🚀 Starting PDF processing...")
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(uploaded_file.read())
            pdf_path = tmp_file.name
        
        # Progress tracking
        progress_bar = progress_container.progress(0)
        status_text = progress_container.empty()
        
        # Step 1: Extract text
        status_text.text("📄 Extracting text from PDF...")
        progress_bar.progress(20)
        raw_data = pd.pdf_extract(pdf_path)
        
        if not raw_data.strip():
            st.error("❌ No text could be extracted from the PDF. Please check if the PDF contains readable text.")
            return False
        
        # Step 2: Clean text
        status_text.text("🧹 Cleaning extracted text...")
        progress_bar.progress(40)
        clean_data = tclean.text_clean(raw_data)
        
        # Step 3: Compute hash
        status_text.text("🔍 Computing content hash...")
        progress_bar.progress(50)
        content_hash = compute_content_hash(clean_data)
        
        # Step 4: Initialize ChromaDB
        status_text.text("🗄️ Initializing ChromaDB...")
        progress_bar.progress(60)
        client = chromadb.PersistentClient(path=chroma_path)
        collection = client.get_or_create_collection(name=collection_name)
        
        # Step 5: Check for duplicates
        status_text.text("🔄 Checking for duplicate content...")
        progress_bar.progress(70)
        
        if check_existing_hash(collection, content_hash):
            progress_bar.progress(100)
            status_text.empty()
            st.warning("⚠️ This PDF's content already exists in the database. Skipping insertion.")
            
            # Show duplicate info in expander
            with st.expander("📊 Duplicate Detection Details"):
                st.write(f"**Content Hash:** `{content_hash[:16]}...`")
                st.write(f"**Collection:** {collection_name}")
                st.write("**Status:** Content already processed")
            
            return True
        
        # Step 6: Chunk text
        status_text.text("✂️ Chunking cleaned text...")
        progress_bar.progress(80)
        chunk_data = tchuk.text_chunks(clean_data)
        
        if not chunk_data:
            st.error("❌ No chunks were generated. Please check your text chunking configuration.")
            return False
        
        # Step 7: Generate IDs and metadata
        status_text.text("🏷️ Generating unique identifiers...")
        progress_bar.progress(85)
        
        if metadata_template is None:
            metadata_template = {
                "organ": "brain",
                "source": uploaded_file.name,
                "content_type": "medical_anatomy",
                "processed_date": datetime.now().isoformat()
            }
        
        unique_ids = generate_unique_ids(collection_name, content_hash, len(chunk_data))
        
        # Double-check IDs
        try:
            existing_check = collection.get(ids=unique_ids[:1])
            if len(existing_check["documents"]) > 0:
                unique_ids = [f"{collection_name}_{uuid.uuid4().hex[:12]}_chunk_{i}" 
                             for i in range(len(chunk_data))]
        except:
            pass
        
        # Step 8: Store in ChromaDB
        status_text.text(f"💾 Storing {len(chunk_data)} chunks in ChromaDB...")
        progress_bar.progress(90)
        
        collection.add(
            documents=chunk_data,
            ids=unique_ids,
            metadatas=[
                {
                    **metadata_template, 
                    "chunk_number": i, 
                    "pdf_hash": content_hash,
                    "total_chunks": len(chunk_data)
                }
                for i in range(len(chunk_data))
            ]
        )
        
        # Complete
        progress_bar.progress(100)
        status_text.empty()
        
        # Success message and stats
        st.success("✅ PDF successfully processed and stored!")
        
        # Display processing statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 Chunks Created", len(chunk_data))
        with col2:
            st.metric("🔍 Content Hash", f"{content_hash[:8]}...")
        with col3:
            st.metric("📁 Collection", collection_name)
        
        # Show details in expander
        with st.expander("📊 Processing Details"):
            st.write(f"**Original Text Length:** {len(raw_data):,} characters")
            st.write(f"**Cleaned Text Length:** {len(clean_data):,} characters")
            st.write(f"**Number of Chunks:** {len(chunk_data)}")
            st.write(f"**Content Hash:** `{content_hash}`")
            st.write(f"**Database Path:** `{chroma_path}`")
        
        return True
        
    except Exception as e:
        st.error(f"❌ Error processing PDF: {str(e)}")
        return False
    
    finally:
        # Cleanup temporary file
        if 'pdf_path' in locals():
            try:
                os.unlink(pdf_path)
            except:
                pass

def main():
    st.set_page_config(
        page_title="PDF to ChromaDB Processor",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🧠 Medical PDF Processing System")
    st.markdown("Upload PDF files to extract, clean, chunk, and store medical content in ChromaDB")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        chroma_path = st.text_input(
            "ChromaDB Path", 
            value="./brain_medical_database",
            help="Directory where ChromaDB will store the data"
        )
        
        collection_name = st.text_input(
            "Collection Name", 
            value="brain_anatomy",
            help="Name of the ChromaDB collection"
        )
        
        st.subheader("📋 Metadata Settings")
        organ = st.selectbox("Organ", ["brain", "heart", "liver", "kidney", "lung"])
        content_type = st.selectbox("Content Type", ["medical_anatomy", "clinical_notes", "research_paper"])
        
        st.markdown("---")
        st.markdown("**🔍 Duplicate Detection:** Enabled")
        st.markdown("**🔐 Content Hashing:** MD5")
        st.markdown("**📊 Chunking:** Automatic")
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📁 File Upload")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload medical PDF documents for processing"
        )
        
        if uploaded_file is not None:
            # Show file info
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.1f} KB",
                "File type": uploaded_file.type
            }
            
            st.write("**📄 File Information:**")
            for key, value in file_details.items():
                st.write(f"- **{key}:** {value}")
            
            # Process button
            if st.button("🚀 Process PDF", type="primary", use_container_width=True):
                metadata_template = {
                    "organ": organ,
                    "source": uploaded_file.name,
                    "content_type": content_type,
                    "processed_date": datetime.now().isoformat()
                }
                
                success = process_and_store_pdf_streamlit(
                    uploaded_file,
                    chroma_path=chroma_path,
                    collection_name=collection_name,
                    metadata_template=metadata_template
                )
                
                if success:
                    st.balloons()
    
    with col2:
        st.subheader("ℹ️ System Info")
        st.info(
            """
            **Features:**
            - 🔍 Automatic duplicate detection
            - 🧹 Text cleaning & preprocessing  
            - ✂️ Intelligent text chunking
            - 🗄️ ChromaDB vector storage
            - 📊 Processing statistics
            - ⚡ Real-time progress tracking
            """
        )
        
        st.subheader("🛡️ Duplicate Protection")
        st.success(
            """
            **Multi-layer Protection:**
            - Content hash verification
            - Database duplicate checking
            - Early exit on duplicates
            - Unique ID collision prevention
            """
        )

if __name__ == "__main__":
    main()

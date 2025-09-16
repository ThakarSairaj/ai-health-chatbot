import hashlib
import chromadb
from PDF_ProcessingModule import PDFExtraction, TextChunking, TextCleaning
import uuid
from datetime import datetime

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
        # Use get() with where filter instead of query()
        results = collection.get(where={"pdf_hash": pdf_hash}, limit=1)
        return len(results["documents"]) > 0
    except Exception as e:
        print(f"Error checking for existing hash: {e}")
        return False

def generate_unique_ids(collection_name, content_hash, num_chunks):
    """Generate unique IDs that won't collide."""
    base_id = f"{collection_name}_{content_hash[:8]}"
    return [f"{base_id}_chunk_{i}" for i in range(num_chunks)]

def process_and_store_pdf(
    pdf_path: str,
    chroma_path: str = "./brain_medical_database",
    collection_name: str = "brain_anatomy",
    metadata_template: dict = None
):
    """
    Extracts text from a PDF, cleans it, chunks it, and stores it in ChromaDB.
    Checks for duplicate content before storing.
    """
    print("Extracting text from PDF.....")
    raw_data = pd.pdf_extract(pdf_path)

    print("Cleaning extracted text.....")
    clean_data = tclean.text_clean(raw_data)

    # Compute a hash of the cleaned text content
    content_hash = compute_content_hash(clean_data)
    print(f"Content hash: {content_hash[:12]}...")

    print("Chunking cleaned text.....")
    chunk_data = tchuk.text_chunks(clean_data)

    print(f"Initializing ChromaDB at {chroma_path}...")
    client = chromadb.PersistentClient(path=chroma_path)

    # Get or create the collection safely
    collection = client.get_or_create_collection(name=collection_name)
    print(f"Using collection: {collection_name}")

    # Check if the PDF's content hash already exists
    if check_existing_hash(collection, content_hash):
        print("⚠️ This PDF's content already exists in the database. Skipping insertion.")
        return

    # Default metadata if none provided
    if metadata_template is None:
        metadata_template = {
            "organ": "brain",
            "source": pdf_path,  # Use actual file path
            "content_type": "medical_anatomy",
            "processed_date": datetime.now().isoformat()
        }

    # Generate unique IDs to prevent collisions
    unique_ids = generate_unique_ids(collection_name, content_hash, len(chunk_data))

    # Double-check that these IDs don't already exist
    try:
        existing_check = collection.get(ids=unique_ids[:1])  # Check first ID
        if len(existing_check["documents"]) > 0:
            print("⚠️ Generated IDs already exist. This shouldn't happen!")
            # Generate completely unique IDs as fallback
            unique_ids = [f"{collection_name}_{uuid.uuid4().hex[:12]}_chunk_{i}" 
                         for i in range(len(chunk_data))]
    except:
        pass  # IDs don't exist, which is what we want

    print(f"Storing {len(chunk_data)} chunks in ChromaDB..... this might take a moment")
    
    try:
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
        print(f"✅ Successfully stored {len(chunk_data)} chunks in ChromaDB!")
        
    except Exception as e:
        print(f"❌ Error storing chunks: {e}")
        # You might want to add cleanup logic here
        raise

if __name__ == "__main__":
    process_and_store_pdf("Brain_Facts_BookHighRes.pdf")

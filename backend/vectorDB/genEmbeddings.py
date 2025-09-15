from PDF_ProcessingModule.PDFExtraction import pdf_extract
from PDF_ProcessingModule.TextCleaning import text_clean
from PDF_ProcessingModule.TextChunking import text_chunks
import chromadb


raw_data = pdf_extract('Brain_Facts_BookHighRes.pdf')
clean_data = text_clean(raw_data)
chunk_data = text_chunks(clean_data)

# Create ChromaDB client
client = chromadb.PersistentClient(path="./brain_medical_database")

# Create a collection for your brain data
collection = client.create_collection(name="brain_anatomy")

# Store your chunks (assuming your chunks are in variable 'chunkss')
collection.add(
    documents=chunk_data,  # Your text chunks
    ids=[f"brain_chunk_{i}" for i in range(len(chunk_data))],  # Unique IDs
    metadatas=[{
        "organ": "brain",
        "source": "Di_Ieva_anatomy_booklet", 
        "chunk_number": i,
        "content_type": "medical_anatomy"
    } for i in range(len(chunk_data))]
)

print(f"✅ Successfully stored {len(chunk_data)} chunks in ChromaDB!")
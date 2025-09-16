# File: vectorDB/genEmbeddings.py

from PDF_ProcessingModule import PDFExtraction, TextChunking, TextCleaning
import chromadb

pd =PDFExtraction
tclean =TextCleaning
tchuk =TextChunking

def process_and_store_pdf(
    pdf_path: str,
    chroma_path: str = "./brain_medical_database",
    collection_name: str = "brain_anatomy",
    metadata_template: dict = None
):
    """
    Extracts text from a PDF, cleans it, chunks it, and stores it in ChromaDB.

    Args:
        pdf_path (str): Path to the PDF file.
        chroma_path (str): Path where ChromaDB should persist.
        collection_name (str): Name of the ChromaDB collection.
        metadata_template (dict): Template for metadata (chunk_number will be added automatically).
    """
    print("Extracting text from PDF.....")
    raw_data = a.pdf_extract(pdf_path)

    print("Cleaning extracted text.....")
    clean_data = b.text_clean(raw_data)

    print("Chunking cleaned text.....")
    chunk_data = c.text_chunks(clean_data)

    print(f"Initializing ChromaDB at {chroma_path}...")
    client = chromadb.PersistentClient(path=chroma_path)

    # Get or create the collection safely
    collection = client.get_or_create_collection(name=collection_name)
    print(f"Using collection: {collection_name}")

    # Default metadata if none provided
    if metadata_template is None:
        metadata_template = {
            "organ": "brain",
            "source": "Di_Ieva_anatomy_booklet",
            "content_type": "medical_anatomy"
        }

    print("Storing chunks in ChromaDB..... this migh take a moment")
    collection.add(
        documents=chunk_data,
        ids=[f"{collection_name}_chunk_{i}" for i in range(len(chunk_data))],
        metadatas=[
            {**metadata_template, "chunk_number": i}
            for i in range(len(chunk_data))
        ]
    )

    print(f"Successfully stored {len(chunk_data)} chunks in ChromaDB!")


if __name__ == "__main__":
    process_and_store_pdf("Brain_Facts_BookHighRes.pdf")

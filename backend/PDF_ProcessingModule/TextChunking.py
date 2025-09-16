from . import PDFExtraction as pd
from . import TextCleaning as tc
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoTokenizer

# Setup tokenizer once
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# Medical separators for semantic chunking
medical_separators = [
    "\n\n",           # Paragraph breaks
    "\n",             # Line breaks  
    ". ",             # Sentence breaks
    "Symptoms:",      # Medical sections
    "Treatment:",       
    "Diagnosis:",
    " ",              # Word breaks
    ""                # Character breaks
]

def text_chunks(text, chunk_size=300, overlap=50):
    """
    Semantic chunking using LangChain + HuggingFace
    """
    # Create semantic text splitter
    text_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer=tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=medical_separators
    )
    
    # Create chunks
    documents = text_splitter.create_documents([text])
    chun = [doc.page_content for doc in documents]
    
    # Filter small chunks
    chun = [chunk.strip() for chunk in chun if len(chunk.strip()) > 50]
    
    return chun

# Usage (same as before):
# raw = pd.pdf_extract('Brain_Facts_BookHighRes.pdf')
# clean = tc.text_clean(raw)
# chunkss = text_chunks(clean)
# print(f"Created {len(chunkss)} semantic chunks")

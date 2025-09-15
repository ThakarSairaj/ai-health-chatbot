from . import PDFExtraction as pd
from . import TextCleaning as tc

def text_chunks(text, chunks = 1000, overlap = 100):

    chun = []
    words = text.split()

    for i in range(0, len(words), chunks - overlap):
        chunk = ' '.join(words[i:i + chunks])
        if(len(chunk.strip()) > 50):
            chun.append(chunk.strip())
        
    return chun


# raw = pd.pdf_extract('Brain_Facts_BookHighRes.pdf')

# clean = tc.text_clean(raw)

# chunkss = text_chunks(clean)

# print(clean)
import re
import PDFExtraction as pd

def text_clean(text):

    #Removes Extra Spaces and break lines
    text = re.sub(r'\s+' , ' ', text)

    #Userful to remove the header and footer
    text = re.sub(r'Pages \d+', '', text)
    text = re.sub(r'Chapter \d+', '', text)

    #Fix Broken Sentences
    text = re.sub(r'([a-z])\n([a-z])', r'\1 \2', text)
    
    #Removes Extra Puncuation Marks
    text = re.sub(r'\.{2,}', '.', text)

    return text.strip()

raw = pd.pdf_extract('Brain_Facts_BookHighRes.pdf')
clean = text_clean(raw)
print(clean)
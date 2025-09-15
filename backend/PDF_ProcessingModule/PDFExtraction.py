import fitz

def pdf_extract(file_path):
    pdf_doc = fitz.open(file_path)

    full_text = ''
    for pdf in range(pdf_doc.page_count):
        page = pdf_doc[pdf]
        text = page.get_text("text", flags=0)
        clean_text = text.replace('Ø', '').replace('*', '').replace('', '')
        full_text += clean_text + "\n"

    pdf_doc.close()
    return full_text

print(pdf_extract('Brain_Facts_BookHighRes.pdf'))
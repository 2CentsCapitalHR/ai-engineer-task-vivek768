from docx import Document

def parse_docx(file_path):
    """Extract all text from DOCX and list of short clause headings."""
    doc = Document(file_path)
    full_text = []
    headings = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            full_text.append(text)
            if len(text.split()) < 15 and text[0].isupper():
                headings.append(text)
    return "\n".join(full_text), headings

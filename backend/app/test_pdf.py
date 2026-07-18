from backend.app.extra.pdfService import extract_pdf_text

path = "https://arxiv.org/pdf/1706.03762.pdf"

text = extract_pdf_text(path)
print(text[:5000])
import fitz
import requests
import tempfile

def extract_pdf_text(pdf_url:str):
    response = requests.get(pdf_url)

    if response.status_code != 200:
        return None
    
    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix='.pdf',
    ) as temp_file:
        temp_file.write(response.content)

        pdf_path = temp_file.name

    doc= fitz.open(pdf_path)
    full_text=""

    for page in doc:
        full_text+=page.get_text()
    doc.close()

    return full_text


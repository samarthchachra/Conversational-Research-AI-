import tempfile
import requests
import fitz

from langchain_core.documents import (
    Document
)

from utils.textProcessing import (
    preprocess_text
)


def download_pdf(pdf_url: str):

    response = requests.get(
        pdf_url,
        timeout=30
    )

    response.raise_for_status()

    with tempfile.NamedTemporaryFile(

        delete=False,

        suffix=".pdf"

    ) as tmp_file:

        tmp_file.write(response.content)

        return tmp_file.name


def extract_text_from_pdf(pdf_path: str):

    doc = fitz.open(pdf_path)

    full_text = ""

    for page in doc:

        text = page.get_text()

        full_text += text + "\n"

    doc.close()

    return full_text


def ingest_pdf(

    pdf_url: str,

    metadata: dict
):

    try:

        print("\nDownloading PDF...\n")

        pdf_path = download_pdf(
            pdf_url
        )

        print("\nExtracting PDF text...\n")

        raw_text = extract_text_from_pdf(
            pdf_path
        )

        print("\nPreprocessing text...\n")

        cleaned_text = preprocess_text(
            raw_text
        )

        document = Document(

            page_content=cleaned_text,

            metadata=metadata
        )

        return {
            "success": True,
            "document": document
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
"""Document chunking for the offline corpus builder.

Splits preprocessed paper text into overlapping chunks suitable for
dense and sparse embedding. Parameters mirror the backend chunkingService
to keep chunk shapes consistent across corpus builds.
"""

from __future__ import annotations

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


CHUNK_SIZE = 2000
CHUNK_OVERLAP = 400
SEPARATORS = ["\n\n", "\n", ". ", ""]


def chunk_documents(documents: list[Document]) -> list[Document]:
    """Split a list of Documents into overlapping text chunks.

    Args:
        documents: Full-text LangChain Document objects (one per paper).

    Returns:
        List of chunk Documents with identical metadata inherited from
        the parent document.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=SEPARATORS,
    )
    return splitter.split_documents(documents)

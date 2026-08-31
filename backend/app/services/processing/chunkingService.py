from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(documents):
    splitter = RecursiveCharacterTextSplitter(

        chunk_size = 2000,
        chunk_overlap=400,
        separators=[
            "\n\n",
            "\n",
            ". ",
            ""]
    )

    chunks = splitter.split_documents(documents=documents)
    return chunks
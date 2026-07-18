from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_document(documents):
    splitter = RecursiveCharacterTextSplitter(

        chunk_size = 10000,
        chunk_overlap=1000,
        separators=[
            "\n\n",
            "\n",
            ". ",
            ""]
    )

    chunks = splitter.split_documents(documents=documents)
    return chunks
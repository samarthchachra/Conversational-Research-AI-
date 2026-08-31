from sentence_transformers import (
    SentenceTransformer
)

model = SentenceTransformer(
    "BAAI/bge-base-en"
)

def create_emebedding(chunks):
    texts=[chunk.page_content 
           for chunk in chunks]
    embeddings = model.encode(
        texts,
        show_progress_bar=True
    )
    
    return embeddings

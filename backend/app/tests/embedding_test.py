from app.services.vectorstore.embeddingService import (
    HuggingFaceAPIEmbeddings
)


embeddings = HuggingFaceAPIEmbeddings()

vector = embeddings.embed_query(
    "What is machine learning?"
)


print("Type:", type(vector))
print("Dimension:", len(vector))
print("Element type:", type(vector[0]))
print("First 5:", vector[:5])
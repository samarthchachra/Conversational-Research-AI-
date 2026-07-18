# from services.arxivService import arxiv_search
# from services.paperRetriever import retrieve_papers
# from services.chunkingService import chunk_document
# from backend.app.extra.embeddingService import create_emebedding
# from services.qdrantService import create_vector_store
# from backend.app.services.ragService import create_retriever_chain
# from langchain_core.documents import Document
# from rich import pretty,print
# from dotenv import load_dotenv

# load_dotenv()

# response = retrieve_papers("explain vision transformer architecture")
# docs=[]
# documents = response["papers"]

# ## converting back to documents

# for paper in documents:
#     docs.append(Document(
#         page_content=paper["content"],
#         metadata=paper["metadata"]
#     )
#     )
# chunks = chunk_document(docs)
# # embeddings = create_emebedding(
# #     chunks
# # )

# vector_store = create_vector_store(chunks)

# print("VECTOR STORE CREATED")

# chain = create_retriever_chain(vector_store=vector_store)
# response = chain.invoke(
#     {"query": "explain vision transformer architecture"})

# print(response['result'])

# # results = vector_store.similarity_search(
# #     "vision transformer architecture",
# #     k=3
# # )

# # print(results[0].page_content[:1000])
# # print(len(chunks))
# # print(chunks[0].page_content[:100])
# # print(chunks[0].metadata)
# # print(len(docs))
# # print(embeddings.shape)


from backend.app.services.retireval.retrievalPipeline import get_retriever
from backend.app.services.retireval.ragService import create_rag_chain
from utils.constants import SIMILARITY_THRESHOLD

query="retrieval augumented generation techniques"
print("query:",query)

retriever = get_retriever(query=query, similarity_threshhold= SIMILARITY_THRESHOLD)

docs = retriever.invoke(query)

for i, doc in enumerate(docs):

    print(f"\nDOC {i}\n")

    print(doc.metadata)
    print("---------------------------------------------------------------")
    print(doc.page_content[:1000])

rag_chain = create_rag_chain(retriever=retriever)

response = rag_chain.invoke({
    "query":query
})

print(response['result'])


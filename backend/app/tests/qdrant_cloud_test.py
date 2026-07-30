# app/tests/qdrant_service_test.py

from app.services.vectorstore.qdrantService import client

print("Testing application Qdrant client...")

print(client.get_collections())

print(
    client.get_collection(
        collection_name="research_papers"
    )
)
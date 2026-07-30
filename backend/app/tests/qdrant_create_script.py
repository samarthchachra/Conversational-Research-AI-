from app.services.vectorstore.qdrantService import (
    create_collection,
    client
)

create_collection()

print(client.get_collections())
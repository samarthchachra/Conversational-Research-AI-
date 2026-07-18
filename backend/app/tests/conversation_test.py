from app.database.database import SessionLocal

from app.services.conversation.conversation_service import (
    ConversationService
)
import app.models

db = SessionLocal()

service = ConversationService()

##########################################################

conversation = service.create_conversation(
    db=db,
    title="Vision Transformer"
)

##########################################################

response = service.chat(
    db=db,
    conversation_id=conversation.id,
    query="Explain Vision Transformer."
)

print(response["answer"])

##########################################################

response = service.chat(
    db=db,
    conversation_id=conversation.id,
    query="How is it different from Swin?"
)

print(response["answer"])

##########################################################

messages = service.get_messages(
    db=db,
    conversation_id=conversation.id
)

for message in messages:

    print(
        message.role,
        message.content[:100]
    )

db.close()
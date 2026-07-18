import uuid

from sqlalchemy.orm import Session

from app.models.conversation import Conversation
from app.models.message import Message
from app.models.enums import MessageRole


class ConversationRepository:

    ###########################################################

    def create_conversation(
        self,
        db: Session,
        title: str | None = None
    ):

        conversation = Conversation(
            title=title
        )

        db.add(conversation)

        db.commit()

        db.refresh(conversation)

        return conversation

    ###########################################################

    def get_conversation(
        self,
        db: Session,
        conversation_id: uuid.UUID
    ):

        return (

            db.query(Conversation)

            .filter(
                Conversation.id == conversation_id
            )

            .first()

        )

    ###########################################################

    def get_messages(
        self,
        db: Session,
        conversation_id: uuid.UUID
    ):

        return (

            db.query(Message)

            .filter(
                Message.conversation_id == conversation_id
            )

            .order_by(
                Message.created_at.asc()
            )

            .all()

        )

    ###########################################################

    def save_message(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        role: MessageRole,
        content: str
    ):

        message = Message(

            conversation_id=conversation_id,

            role=role,

            content=content
        )

        db.add(message)

        db.commit()

        db.refresh(message)

        return message

    ###########################################################

    def update_title(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        title: str
    ):

        conversation = self.get_conversation(
            db,
            conversation_id
        )

        if conversation is None:
            return None

        conversation.title = title

        db.commit()

        db.refresh(conversation)

        return conversation

    ###########################################################

    def delete_conversation(
        self,
        db: Session,
        conversation_id: uuid.UUID
    ):

        conversation = self.get_conversation(
            db,
            conversation_id
        )

        if conversation is None:
            return False

        db.delete(conversation)

        db.commit()

        return True

    ###########################################################

    def list_conversations(
        self,
        db: Session
    ):

        return (

            db.query(Conversation)

            .order_by(
                Conversation.created_at.desc()
            )

            .all()

        )
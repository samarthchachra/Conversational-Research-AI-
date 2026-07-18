import uuid

from sqlalchemy.orm import Session

from app.models.enums import MessageRole
from app.models.conversation import Conversation
from app.models.message import Message
import app.models

from app.repositories.conversation_repo import (
    ConversationRepository
)
from app.services.retrieval.adaptive_rag_pipeline import (
    AdaptiveRagPipeline
)

from app.services.conversation.query_rewriter import (
    QueryRewriter
)


class ConversationService:

    def __init__(self):

        self.repository = ConversationRepository()

        self.rag_pipeline = AdaptiveRagPipeline()

        self.query_rewriter = QueryRewriter()

    ###########################################################

    def create_conversation(
        self,
        db: Session,
        title: str | None = None
    ):

        return self.repository.create_conversation(
            db=db,
            title=title
        )

    ###########################################################

    def get_conversation(
        self,
        db: Session,
        conversation_id: uuid.UUID
    ):

        return self.repository.get_conversation(
            db=db,
            conversation_id=conversation_id
        )

    ###########################################################

    def list_conversations(
        self,
        db: Session
    ):

        return self.repository.list_conversations(
            db=db
        )

    ###########################################################

    def get_messages(
        self,
        db: Session,
        conversation_id: uuid.UUID
    ):

        return self.repository.get_messages(
            db=db,
            conversation_id=conversation_id
        )

    ###########################################################

    def chat(
        self,
        db: Session,
        conversation_id: uuid.UUID,
        query: str
    ):

        conversation = self.repository.get_conversation(
            db=db,
            conversation_id=conversation_id
        )

        if conversation is None:

            raise ValueError(
                "Conversation not found."
            )

        self.repository.save_message(
            db=db,
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=query
        )
        history = self.get_messages(
            db=db,
            conversation_id=conversation_id
        )

        rewritten_query = self.query_rewriter.rewrite(
        history=history,
        query=query
        )

        print(
        f"\nRewritten Query:\n{rewritten_query}\n"
        )

        response = self.rag_pipeline.invoke(
            query=rewritten_query
        )

        self.repository.save_message(
            db=db,
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=response["answer"]
        )

        return response
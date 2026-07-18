import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    Text,Enum
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.enums import MessageRole
from app.database.database import Base


class Message(Base):

    __tablename__ = "messages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "conversations.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    role = Column(
        Enum(MessageRole),
        nullable=False
    )

    content = Column(
        Text,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    conversation = relationship(
        "Conversation",
        back_populates="message"
    )
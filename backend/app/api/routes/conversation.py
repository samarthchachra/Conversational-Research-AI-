from fastapi import APIRouter, Depends, Header

from sqlalchemy.orm import Session

from uuid import UUID

from app.database.database import get_db

from app.schemas.chat import (
    ChatRequest,
    ChatResponse
)

from app.schemas.conversation import (
    CreateConversationRequest,
    ConversationResponse,
    UpdateTitleRequest
)

from app.services.conversation.conversation_service import (
    ConversationService
)

router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"]
)

service = ConversationService()



@router.post(
    "",
    response_model=ConversationResponse
)
def create_conversation(
    request: CreateConversationRequest,
    db: Session = Depends(get_db),
    x_user_id: str = Header(...)
):

    return service.create_conversation(
        db=db,
        user_id=x_user_id,
        title=request.title
    )



@router.delete(
    "/{conversation_id}"
)
def delete_conversation(
    conversation_id: UUID,
    db: Session = Depends(get_db),
    x_user_id: str = Header(...)
):

    return service.delete_conversation(
        db=db,
        conversation_id=conversation_id,
        user_id=x_user_id
    )


@router.put(
    "/{conversation_id}/title"
)
def update_title(
    conversation_id: UUID,
    request: UpdateTitleRequest,
    db: Session = Depends(get_db),
    x_user_id: str = Header(...)
):

    return service.update_title(
        db=db,
        conversation_id=conversation_id,
        user_id=x_user_id,
        title=request.title
    )


@router.post(
    "/chat",
    response_model=ChatResponse
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    x_user_id: str = Header(...)
):

    return service.chat(
        db=db,
        conversation_id=request.conversation_id,
        user_id=x_user_id,
        query=request.query
    )



@router.get("")
def list_conversations(
    db: Session = Depends(get_db),
    x_user_id: str = Header(...)
):

    return service.list_conversations(
        db=db,
        user_id=x_user_id
    )



@router.get("/{conversation_id}/messages")
def get_messages(
    conversation_id: UUID,
    db: Session = Depends(get_db)
):

    return service.get_messages(
        db=db,
        conversation_id=conversation_id
    )
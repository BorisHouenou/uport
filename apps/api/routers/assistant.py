"""RAG compliance assistant chat endpoint."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.assistant import AssistantMessage, AssistantChatRequest

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/chat")
async def chat(
    request: AssistantChatRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    RAG-powered compliance assistant.
    Streams responses grounded in trade agreement texts.
    Cites specific articles and annexes.
    """
    from services.rag_service import stream_compliance_answer

    async def generate():
        async for chunk in stream_compliance_answer(
            messages=request.messages,
            org_id=current_user["org_id"],
            agreement_filter=request.agreement_filter,
        ):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@router.get("/chat/history")
async def get_chat_history(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
):
    """Retrieve recent chat history for the current user."""
    from services.rag_service import get_chat_history
    return await get_chat_history(db, current_user["user_id"], limit)

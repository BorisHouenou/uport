"""RAG compliance assistant chat endpoint."""
import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from middleware.auth import CurrentUser
from schemas.assistant import AssistantMessage, AssistantChatRequest

router = APIRouter(prefix="/assistant", tags=["assistant"])
_limiter = Limiter(key_func=get_remote_address)


@router.post("/chat")
@_limiter.limit("30/minute")
async def chat(
    http_request: Request,
    request: AssistantChatRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    RAG-powered compliance assistant.
    Streams responses grounded in trade agreement texts.
    Cites specific articles and annexes.
    Persists the completed turn to chat_messages after streaming.
    """
    from services.rag_service import stream_compliance_answer, save_chat_turn

    user_messages = [m for m in request.messages if m.role == "user"]
    last_user_content = user_messages[-1].content if user_messages else ""

    accumulated_text = []
    accumulated_citations: list | None = None

    async def generate():
        nonlocal accumulated_citations
        async for chunk in stream_compliance_answer(
            messages=[{"role": m.role, "content": m.content} for m in request.messages],
            org_id=current_user["org_id"],
            agreement_filter=request.agreement_filter,
        ):
            # Collect for persistence
            try:
                parsed = json.loads(chunk)
                if parsed.get("type") == "text":
                    accumulated_text.append(parsed["text"])
                elif parsed.get("type") == "citations":
                    accumulated_citations = parsed["citations"]
            except Exception:
                pass

            yield f"data: {chunk}\n\n"

        yield "data: [DONE]\n\n"

        # Persist turn after stream completes
        try:
            await save_chat_turn(
                db=db,
                org_id=current_user["org_id"],
                user_id=current_user["user_id"],
                user_content=last_user_content,
                assistant_content="".join(accumulated_text),
                citations=accumulated_citations,
            )
        except Exception:
            pass  # never fail the response due to persistence error

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

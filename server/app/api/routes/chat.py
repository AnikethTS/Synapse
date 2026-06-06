from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.core.prompts import SYSTEM_PROMPT
from app.middleware.rate_limit import check_rate_limit
from app.models.chat import ChatRequest
from app.services.context import maybe_summarize, preprocess, trim_to_budget
from app.services.groq_client import get_groq_client
from app.services.streaming import stream_with_retry

router = APIRouter()


@router.post("/chat", dependencies=[Depends(check_rate_limit)])
async def chat(body: ChatRequest) -> StreamingResponse:
    """Stream an LLM response for the given conversation history."""
    client = get_groq_client()

    try:
        messages = preprocess(body.messages)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    messages = maybe_summarize(client, messages)
    messages = trim_to_budget(messages)

    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]

    return StreamingResponse(
        stream_with_retry(client, groq_messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )

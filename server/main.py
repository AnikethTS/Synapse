"""
Synapse Backend — FastAPI + Groq streaming chat API.
"""

import os
from collections.abc import Generator

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from groq import Groq
from pydantic import BaseModel, field_validator

load_dotenv()

app = FastAPI(title="Synapse API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL = "llama-3.3-70b-versatile"
SYSTEM_PROMPT = (
    "You are Synapse, a helpful and knowledgeable AI assistant for developers. "
    "You excel at explaining code, debugging, architecture decisions, and technical concepts. "
    "Format code examples with appropriate markdown code blocks."
)


class Message(BaseModel):
    role: str
    content: str

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in {"user", "assistant", "system"}:
            raise ValueError("role must be 'user', 'assistant', or 'system'")
        return v


class ChatRequest(BaseModel):
    messages: list[Message]

    @field_validator("messages")
    @classmethod
    def validate_messages(cls, v: list[Message]) -> list[Message]:
        if not v:
            raise ValueError("messages list cannot be empty")
        return v


def _get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is not configured")
    return Groq(api_key=api_key)


def _stream_chat(messages: list[Message]) -> Generator[str, None, None]:
    """Yield SSE-formatted chunks from the Groq streaming API."""
    client = _get_groq_client()

    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m.role, "content": m.content} for m in messages
    ]

    with client.chat.completions.create(
        model=MODEL,
        messages=groq_messages,
        stream=True,
        temperature=0.7,
        max_tokens=4096,
    ) as stream:
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                # Escape newlines so they don't break the SSE frame
                escaped = delta.content.replace("\n", "\\n")
                yield f"data: {escaped}\n\n"

    yield "data: [DONE]\n\n"


@app.post("/chat")
async def chat(request: ChatRequest) -> StreamingResponse:
    """Stream an LLM response for the given conversation history."""
    return StreamingResponse(
        _stream_chat(request.messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable nginx buffering
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

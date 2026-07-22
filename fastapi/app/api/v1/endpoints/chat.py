from fastapi import APIRouter, status
from fastapi.responses import StreamingResponse

from app.schemas.chat import ChatRequest
from app.services.llm import stream_chat

router = APIRouter(tags=["chat"])


@router.post("/chat", status_code=status.HTTP_200_OK, summary="Send a chat message")
async def chat(request: ChatRequest):
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    async def event_stream():
        async for chunk in stream_chat(messages, request.language):
            payload = _escape_json(chunk)
            yield f"data: {{{{ \"content\": \"{payload}\", \"done\": false }}}}\n\n"
        yield "data: {\"content\": \"\", \"done\": true}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _escape_json(s: str) -> str:
    for old, new in (("\\", "\\\\"), ('"', '\\"'), ("\n", "\\n"), ("\r", "\\r"), ("\t", "\\t")):
        s = s.replace(old, new)
    return s

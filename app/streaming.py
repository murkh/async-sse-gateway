import json
from collections.abc import AsyncIterator

from fastapi.responses import StreamingResponse


def sse_event(data: str, event: str | None = None) -> str:
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json.dumps(data)}\n\n"


async def to_sse(chunks: AsyncIterator[str]) -> AsyncIterator[str]:
    async for chunk in chunks:
        yield sse_event(chunk)
    yield sse_event("[DONE]", event="done")


def sse_response(chunks: AsyncIterator[str]) -> StreamingResponse:
    return StreamingResponse(
        to_sse(chunks),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

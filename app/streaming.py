import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import aclosing

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from starlette.types import Receive, Scope, Send

MAX_STREAMS = 5000  # concurrent streams per worker; cluster capacity = MAX_STREAMS x workers
SEND_TIMEOUT = 10.0  # seconds a client may stall a write before we drop it

# ponytail: per-process limit; total = MAX_STREAMS x workers. Shared counter (Redis) if a global cap is needed.
active_streams = 0


def sse_event(data: str, event: str | None = None) -> str:
    prefix = f"event: {event}\n" if event else ""
    return f"{prefix}data: {json.dumps(data)}\n\n"


async def to_sse(chunks: AsyncIterator[str]) -> AsyncIterator[str]:
    async with aclosing(chunks):
        async for chunk in chunks:
            yield sse_event(chunk)
    yield sse_event("[DONE]", event="done")


class _SSEResponse(StreamingResponse):
    """Pull-based: next upstream chunk is requested only after the previous write drains
    (uvicorn's send awaits transport flow control). A client that stalls a write past
    SEND_TIMEOUT is dropped. Always closes upstream and frees the slot."""

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        async def timed_send(message):
            async with asyncio.timeout(SEND_TIMEOUT):
                await send(message)

        global active_streams
        try:
            await super().__call__(scope, receive, timed_send)
        finally:
            active_streams -= 1
            await self.body_iterator.aclose()


def sse_response(chunks: AsyncIterator[str]) -> StreamingResponse:
    global active_streams
    if active_streams >= MAX_STREAMS:
        raise HTTPException(503, "Too many concurrent streams", headers={"Retry-After": "1"})
    active_streams += 1  # no await between check and increment: race-free on one event loop
    return _SSEResponse(
        to_sse(chunks),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

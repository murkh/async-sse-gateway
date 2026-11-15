import asyncio

import pytest
from fastapi.testclient import TestClient

from app import streaming
from app.main import app

client = TestClient(app)


def test_stream_emits_sse_events_and_done():
    with client.stream("GET", "/stream", params={"prompt": "hi there"}) as r:
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("text/event-stream")
        body = "".join(r.iter_text())

    events = [e for e in body.split("\n\n") if e]
    assert events[:3] == ['data: "Echo: "', 'data: "hi "', 'data: "there "']
    assert events[-1] == 'event: done\ndata: "[DONE]"'


def test_stream_rejects_empty_prompt():
    assert client.get("/stream", params={"prompt": ""}).status_code == 422


def test_stream_rejects_when_at_capacity(monkeypatch):
    monkeypatch.setattr(streaming, "MAX_STREAMS", 0)
    r = client.get("/stream", params={"prompt": "hi"})
    assert r.status_code == 503
    assert r.headers["retry-after"] == "1"


def test_stalled_client_is_dropped_and_upstream_closed(monkeypatch):
    monkeypatch.setattr(streaming, "SEND_TIMEOUT", 0.05)
    closed = False

    async def upstream():
        nonlocal closed
        try:
            while True:
                yield "tok"
        finally:
            closed = True

    async def stalled_send(message):
        if message["type"] == "http.response.body":
            await asyncio.Event().wait()  # client never drains

    async def receive():
        await asyncio.Event().wait()

    async def run():
        before = streaming.active_streams
        resp = streaming.sse_response(upstream())
        assert streaming.active_streams == before + 1
        with pytest.raises(TimeoutError):
            await resp({"type": "http", "asgi": {"spec_version": "2.3"}}, receive, stalled_send)
        assert streaming.active_streams == before

    asyncio.run(run())
    assert closed

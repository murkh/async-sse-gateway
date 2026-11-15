from fastapi.testclient import TestClient

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

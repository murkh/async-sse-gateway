# async-sse-gateway

FastAPI gateway streaming LLM tokens over Server-Sent Events.

```
app/main.py        routes (/health, /stream)
app/llm.py         token generator (fake; swap for real provider)
app/streaming.py   SSE formatting + StreamingResponse
tests/             pytest
loadtest/          Locust load test
```

## Run

```sh
uv sync
uv run fastapi dev app/main.py
curl -N "localhost:8000/stream?prompt=hello"
```

## Test

```sh
uv run pytest
uv run locust -f loadtest/locustfile.py --host http://localhost:8000   # web UI on :8089
uv run locust -f loadtest/locustfile.py --host http://localhost:8000 --headless -u 50 -r 10 -t 30s
```

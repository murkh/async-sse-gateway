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

## Production / 10k+ concurrent

```sh
ulimit -n 65535                                  # 1 fd per connection
sudo sysctl -w kern.ipc.somaxconn=4096           # macOS caps --backlog at 128 (Linux: net.core.somaxconn)
uv run uvicorn app.main:app --workers 4 --backlog 4096
```

Capacity = `MAX_STREAMS` (app/streaming.py) x workers; excess requests get 503 + `Retry-After`.

## Test

```sh
uv run pytest
uv run locust -f loadtest/locustfile.py --host http://localhost:8000   # web UI on :8089
uv run locust -f loadtest/locustfile.py --host http://localhost:8000 --headless -u 50 -r 10 -t 30s
k6 run -e HOST=http://localhost:8000 loadtest/k6.js                     # brew install k6; ramps to 10k VUs
```

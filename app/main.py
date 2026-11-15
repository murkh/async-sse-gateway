from fastapi import FastAPI, Query

from app.llm import generate_tokens
from app.streaming import sse_response

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/stream")
async def stream(prompt: str = Query(min_length=1, max_length=4000)):
    return sse_response(generate_tokens(prompt))

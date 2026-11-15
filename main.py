from asyncio import sleep

from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


async def generate_numbers():
    for i in range(10):
        yield f"{i}\n"
        await sleep(1)


@app.get("/stream_numbers")
async def stream_numbers():
    return StreamingResponse(
        generate_numbers(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

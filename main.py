from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}



async def generate_numbers():
    for i in range(10):
        yield i


@app.get("/stream_numbers")
async def stream_numbers():
    return StreamingResponse(generate_numbers(), media_type="text/plain")
from asyncio import sleep
from collections.abc import AsyncIterator


async def generate_tokens(prompt: str, delay: float = 0.05) -> AsyncIterator[str]:
    for word in f"Echo: {prompt}".split():
        yield word + " "
        await sleep(delay)
